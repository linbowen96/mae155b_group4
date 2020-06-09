from openmdao.api import Group, IndepVarComp, ExecComp, Problem

from weight_component.wingWeight import wingWeightComp
from weight_component.tailWeight import htailWeightComp
from weight_component.tailWeight import vtailWeightComp
from weight_component.fuselageWeight import fuselageWeightComp
from weight_component.gearWeight import maingearWeightComp
from weight_component.gearWeight import nosegearWeightComp
from weight_component.hydraulicWeight import hydraulicWeightComp
from weight_component.airconWeight import airconWeightComp

class weightCompGroup(Group):


    def setup(self):

        comp = IndepVarComp()
        comp.add_output('W0', val=256000)
        comp.add_output('Wl', val=150000)
        # comp.add_output('S_w', val=1757)
        comp.add_output('Bw',val=126)
        comp.add_output('S_ht',val=300)
        comp.add_output('S_vt',val=300)
        comp.add_output('W_furnish',val=8900)
        comp.add_output('W_engine',val=32000)
        # comp.add_design_var('W0', lower=150000)
        self.add_subsystem('inputs_comp', comp, promotes=['*'])
        
        comp = wingWeightComp(N=3.5,t_c=0.3,AR=9.,sweep=30.,taper = 0.3)
        self.add_subsystem('wingWeight',comp,promotes=['*'])

        comp = htailWeightComp(N=3.5,Lt=85.,AR_ht=4., sweepht=27.)
        self.add_subsystem('htailWeight',comp,promotes=['*'])

        comp = vtailWeightComp(N=3.5,Lt=85.,AR_vt=4.,sweepvt=27., t_c=0.3)
        self.add_subsystem('vtailWeight',comp,promotes=['*'])

        comp = fuselageWeightComp(N=3.5,L=205.,LD=17.,S_fuse=15030.,sweep=30.,taper=0.3)
        self.add_subsystem('fuselageWeight',comp,promotes=['*'])

        comp = maingearWeightComp(Nl=5.,Vstall=150.)
        self.add_subsystem('maingearWeight',comp,promotes=['*'])

        comp = nosegearWeightComp(Nl=5.)
        self.add_subsystem('nosegearWeight',comp,promotes=['*'])

        comp = airconWeightComp(Np=410.,Vpr=39000.)
        self.add_subsystem('airconWeight',comp,promotes=['*'])

        comp = hydraulicWeightComp()
        self.add_subsystem('hydraulicWeight',comp,promotes=['*'])

        comp = ExecComp('emptyTotal = W_wing + W_ht + vtailWeight + W_fuse + W_mgear + W_ngear + W_aircon + W_hydraulic + W_furnish + W_engine')
        self.add_subsystem('emptyWeight',comp,promotes=['*'])
        
# runs a test to see if calculated values make sense
if __name__ == "__main__":
    

    prob = Problem()

    weight_group = weightCompGroup()
    prob.model.add_subsystem('weight_group', weight_group)
    

    prob.setup(check=True)
    prob.run_model()

    prob.model.list_inputs(prom_name=True)
    prob.model.list_outputs(prom_name=True)