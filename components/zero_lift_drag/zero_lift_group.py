import numpy as np

from openmdao.api import ExplicitComponent, IndepVarComp, Group, Problem
from lsdo_utils.api import OptionsDictionary, LinearCombinationComp, PowerCombinationComp, GeneralOperationComp, ElementwiseMinComp
from .atmosphere_group import AtmosphereGroup
from .s_wet import SWet
from .skin_friction_group import SkinFrictionGroup
from .form_drag_co import FormDragCo

class ZeroLiftGroup(Group):

    def initialize(self):
        self.options.declare('shape', types=tuple)
        
    def setup(self):
        shape = self.options['shape']
        
        comp = IndepVarComp()
        comp.add_output('altitude', val = 12000.)
        comp.add_output('speed', val = 250.)
        comp.add_output('t_c', val = .13)
        comp.add_output('sweep', val = 22.5 * np.pi/180)
        # comp.add_output('Mach_number', val = 0.85)

        comp.add_output('S_w', val = 157. )
        comp.add_output('S_f', val = 2000. )

        comp.add_output('fuselage_finesse_ratio', val = 8.)
        comp.add_output('characteristic_length', val = 5.)
        

        comp.add_output('interference_factor', val = 1.)
        self.add_subsystem('inputs_comp', comp, promotes=['*'])
        
        atmosphere_group = AtmosphereGroup(
            shape = shape,
        )
        self.add_subsystem('atmosphere_group', atmosphere_group, promotes=['*'])
        

        skin_friction_group = SkinFrictionGroup(
            shape = shape,
        )

        self.add_subsystem('skin_friction_group', skin_friction_group, promotes=['*'])

        wetted_area_comp = SWet()
        self.add_subsystem('wetted_area_comp', wetted_area_comp, promotes=['*'])

        form_drag_comp = FormDragCo()
        self.add_subsystem('form_drag_comp', form_drag_comp, promotes=['*'])

        comp = PowerCombinationComp(
            shape=shape,
            out_name='C0_wing',
            powers_dict=dict(
                skin_friction_coeff = 1.,
                S_wet_w= 1.,
                FF_wing=1.,
                S_w= -1.,
                interference_factor=1.,
                ),
            )
        self.add_subsystem('C0_wing_comp', comp, promotes=['*'])

        comp = PowerCombinationComp(
            shape=shape,
            out_name='C0_fuselage',
            powers_dict=dict(
                skin_friction_coeff = 1.,
                S_wet_f=1.,
                FF_fuselage=1.,
                S_f=-1.,
                interference_factor=1.,
                ),
            )
        self.add_subsystem('C0_fuse_comp', comp, promotes=['*'])

        comp = LinearCombinationComp(
            shape = shape,
            in_names = ['C0_wing','C0_fuselage'],
            out_name = 'CD0',
            coeffs = [1.,1.],

        )
        self.add_subsystem('CD0', comp, promotes=['*'])
        
        
# runs a test to see if calculated values make sense
if __name__ == "__main__":
    
    shape = (1,)

    prob = Problem()

    zero_lift_group = ZeroLiftGroup(
        shape = shape,
    )
    prob.model.add_subsystem('zero_lift_group', zero_lift_group)
    

    prob.setup(check=True)
    prob.run_model()

    prob.model.list_inputs(prom_name=True)
    prob.model.list_outputs(prom_name=True)