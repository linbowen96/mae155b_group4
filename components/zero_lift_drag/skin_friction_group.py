import numpy as np

from openmdao.api import ExplicitComponent,IndepVarComp
import openmdao.api as om
from openmdao.api import Group,Problem
from lsdo_utils.api import OptionsDictionary, LinearCombinationComp, PowerCombinationComp, GeneralOperationComp, ElementwiseMinComp


class SkinFrictionGroup(Group):

    def initialize(self):
        self.options.declare('shape', types=tuple)
        
    def setup(self):
        shape = self.options['shape']

        skin_friction_roughness = 0.4e-5 
        laminar_pctg = 5
        Mach_number = 0.85 

        # comp = IndepVarComp()
        # comp.add_output('speed', val = 250.)
        # comp.add_output('characteristic_length', val = 5.)
        # comp.add_output('density', val = 1.225)
        # comp.add_output('dynamic_viscosity', val = 0.0017893145130960248)
        # self.add_subsystem('inputs_comp', comp, promotes=['*'])

        # creates component for calculating Re
        comp = PowerCombinationComp(
            shape=shape,
            out_name='Re',
            powers_dict=dict(
                density=1.,
                speed=1.,
                characteristic_length=1.,
                dynamic_viscosity=-1.,
            ),
        )
        self.add_subsystem('Re_comp', comp, promotes=['*'])
        # creates component for calculating Re_Cutoff for subsonic and sonic flows
        if Mach_number < 0.9:
            comp = PowerCombinationComp(
                shape=shape,
                out_name='Re_cutoff',
                coeff=38.21 * skin_friction_roughness ** -1.053,
                powers_dict=dict(
                    characteristic_length=1.053,
                ),
            )
            self.add_subsystem('Re_cutoff_comp', comp, promotes=['*'])
        elif Mach_number > 0.9:
            comp = PowerCombinationComp(
                shape=shape,
                out_name='Re_cutoff',
                coeff=44.62 * skin_friction_roughness ** -1.053,
                powers_dict=dict(
                    characteristic_length=1.053,
                    Mach_number=1.16,
                ),
            )
            self.add_subsystem('Re_cutoff_comp', comp, promotes=['*'])
        else:
            raise Exception()
        # creates component for determining whether to use Re_cutoff or Re for later use in calculating Cf
        comp = ElementwiseMinComp(
            shape=shape, 
            out_name='Re_turbulent_min', 
            in_names=['Re', 'Re_cutoff'], 
            rho=1e-3,
        )
        self.add_subsystem('Re_turbulent_min_comp', comp, promotes=['*'])
        # creates component for Cf_laminar
        comp = PowerCombinationComp(
            shape=shape,
            out_name='skin_friction_coeff_laminar',
            coeff=1.328,
            powers_dict=dict(
                Re=-0.5,
            ),
        )
        self.add_subsystem('skin_friction_coeff_laminar_comp', comp, promotes=['*'])
        # defines function for Cf under turbulent conditions 
        def func(Re, M):
            Cf = 0.455 / ( np.log(Re) / np.log(10) ) ** 2.58 / (1 + 0.144 * M ** 2) ** 0.65
            return Cf

        def deriv(Re, M):
            dCf_dRe = -2.58 * 0.455 / ( np.log(Re) / np.log(10) ) ** 3.58 * 1 / Re / np.log(10) / (1 + 0.144 * M ** 2) ** 0.65
            dCf_dM = 0.455 / ( np.log(Re) / np.log(10) ) ** 2.58 * -0.65 / (1 + 0.144 * M ** 2) ** 1.65 * 2 * 0.144 * M
            return (dCf_dRe, dCf_dM)

        comp = GeneralOperationComp(
            shape=shape,
            out_name='skin_friction_coeff_turbulent',
            in_names=['Re_turbulent_min', 'Mach_number'],
            func=func,
            deriv=deriv,
        )
        self.add_subsystem('skin_friction_coeff_turbulent_comp', comp, promotes=['*'])

        comp = LinearCombinationComp(
            shape=shape,
            out_name='skin_friction_coeff',
            coeffs_dict=dict(
                skin_friction_coeff_laminar = laminar_pctg / 100.,
                skin_friction_coeff_turbulent = 1 - laminar_pctg / 100.,
            ),
        )
        self.add_subsystem('skin_friction_coeff_comp', comp, promotes=['*'])

# runs a test to see if calculated values make sense
if __name__ == "__main__":
    
    shape = (1,)

    prob = Problem()

    skin_friction_group = SkinFrictionGroup(
        shape = shape,
    )
    prob.model.add_subsystem('skin_friction_group', skin_friction_group)

    prob.setup(check=True)
    prob['skin_friction_group.speed'] = 250.
    prob['skin_friction_group.density'] = 1.227
    prob['skin_friction_group.Mach_number'] = 0.85
    prob['skin_friction_group.dynamic_viscosity'] = 0.0017893145130960248
    prob['skin_friction_group.characteristic_length'] = 5.


    prob.run_model()
    prob.model.list_outputs(prom_name=True)
