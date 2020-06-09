
import numpy as np
from openmdao.api import ExplicitComponent
import openmdao.api as om

# 
#    Computes the Form Factor which takes into account the interference drag
# 

class FormDragCo(ExplicitComponent):

    def setup(self):
        # inputs for wing form factor

        self.add_input('t_c')
        # # x_t is the position of maximum thickness
        self.add_input('x_t', val = .30 )
        self.add_input('Mach_number')
        self.add_input('sweep')
        self.add_output('FF_wing')

        # inputs for fuselage form factor
        # finesse ratio is length / diameter of thing being looked at
        self.add_input('fuselage_finesse_ratio')
        self.add_output('FF_fuselage')
        # # inputs for nacelle form factor
        # self.add_input('nacelle_finesse_ratio')
        # self.add_output('FF_nacelle')
        # declare partials for FF_wing with respect to t_c, mach, x_t, and sweep angle

        self.declare_partials('FF_wing', 't_c')
        self.declare_partials('FF_wing', 'Mach_number')
        self.declare_partials('FF_wing', 'x_t')
        self.declare_partials('FF_wing', 'sweep')

        # declare partials for FF_fuselage with respect to its finesse ratio
        self.declare_partials('FF_fuselage', 'fuselage_finesse_ratio')
        # declare partials for FF_nacelle with respect to its finesse ratio
        # self.declare_partials('FF_nacelle', 'nacelle_finesse_ratio')
        
        
    def compute(self, inputs, outputs):
        t_c = inputs['t_c']
        x_t = inputs['x_t']
        Mach_number = inputs['Mach_number']
        sweep = inputs['sweep']
        # fuselage terms
        fuselage_finesse_ratio = inputs['fuselage_finesse_ratio']
        # nacelle terms
        # nacelle_finesse_ratio = inputs['nacelle_finesse_ratio']
        
        # compute equations for FF
        outputs['FF_wing'] = (1+ (0.6/x_t)*(t_c) + 100 *t_c**4)*(1.34*Mach_number**0.18 * np.cos(sweep)**0.28)
        outputs['FF_fuselage'] = 1 + 60/(fuselage_finesse_ratio**3) + fuselage_finesse_ratio/400
        # outputs['FF_nacelle'] = 1 + (0.35/nacelle_finesse_ratio)

    def compute_partials(self, inputs, partials):
        t_c = inputs['t_c']
        x_t = inputs['x_t']
        Mach_number = inputs['Mach_number']
        sweep = inputs['sweep']
        # fuselage terms
        fuselage_finesse_ratio = inputs['fuselage_finesse_ratio']
        # nacelle terms
        # nacelle_finesse_ratio = inputs['nacelle_finesse_ratio']


        partials['FF_wing', 't_c'] = 536*Mach_number**0.18 *np.cos(sweep)**0.28 * (t_c**3 *x_t + 0.0015)/x_t
        partials['FF_wing', 'x_t'] = -0.804*t_c*Mach_number**0.18 *np.cos(sweep)**0.28 / x_t**2
        partials['FF_wing', 'Mach_number'] = 0.2412*np.cos(sweep)**0.28 * (1+ (0.6/x_t)*(t_c) + 100 *t_c**4)
        partials['FF_wing', 'sweep'] = -0.3752*Mach_number**0.18*np.sin(sweep) * (1+ (0.6/x_t)*(t_c) + 100 *t_c**4) / np.cos(sweep)**0.72

        partials['FF_fuselage', 'fuselage_finesse_ratio'] = -180 / (fuselage_finesse_ratio**4) + 1/400
        # partials['FF_nacelle', 'nacelle_finesse_ratio'] = -0.35 / (nacelle_finesse_ratio**2)

# runs a test to see if calculated values make sense
if __name__ == "__main__":
    model = om.Group()
    ivc = om.IndepVarComp()
    ivc.add_output('x_t', 0.3)
    ivc.add_output('t_c', 0.1)
    ivc.add_output('Mach_number', 0.85)
    ivc.add_output('sweep', 22 * np.pi / 180)
    ivc.add_output('fuselage_finesse_ratio', 8)
    # ivc.add_output('nacelle_finesse_ratio', 5)
    model.add_subsystem('des_vars', ivc)
    model.add_subsystem('form_drag_co', FormDragCo())

    model.connect('des_vars.x_t', 'form_drag_co.x_t')
    model.connect('des_vars.t_c', 'form_drag_co.t_c')
    model.connect('des_vars.Mach_number', 'form_drag_co.Mach_number')
    model.connect('des_vars.sweep', 'form_drag_co.sweep')
    model.connect('des_vars.fuselage_finesse_ratio', 'form_drag_co.fuselage_finesse_ratio')
    # model.connect('des_vars.nacelle_finesse_ratio', 'form_drag_co.nacelle_finesse_ratio')

    prob = om.Problem(model)
    prob.setup()
    prob.run_model()
    print('FF_wing')
    print(prob['form_drag_co.FF_wing'])
    print('FF_fuselage')
    print(prob['form_drag_co.FF_fuselage'])
    # print('FF_nacelle')
    # print(prob['form_drag_co.FF_nacelle'])