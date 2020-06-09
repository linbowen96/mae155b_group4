import numpy as np

import openmdao.api as om

from openaerostruct.geometry.geometry_group import Geometry as GeometryGroup
from openaerostruct.aerodynamics.aero_groups import AeroPoint as AeroPointGroup
from openmdao.api import ExplicitComponent, Group


class OASGroup(Group):

    def initialize(self):
        self.options.declare('surface', types=dict)

    def setup(self):
        surface = self.options['surface']

        indep_var_comp = om.IndepVarComp()
        indep_var_comp.add_output('v', val=257.222, units='m/s')
        indep_var_comp.add_output('alpha', val=5., units='deg')
        # indep_var_comp.add_output('Mach_number', val=0.84)
        indep_var_comp.add_output('re', val=1.e6, units='1/m')
        indep_var_comp.add_output('rho', val=0.38, units='kg/m**3')
        indep_var_comp.add_output('cg', val=np.zeros((3)), units='m')

        # Add this IndepVarComp to the problem model
        self.add_subsystem('prob_vars',
            indep_var_comp,
            promotes=['*'])

        # Create and add a group that handles the geometry for the
        # aerodynamic lifting surface
        geom_group = GeometryGroup(surface=surface)
        self.add_subsystem(surface['name'], geom_group)

        # Create the aero point group, which contains the actual aerodynamic
        # analyses
        aero_group = AeroPointGroup(surfaces=[surface])
        point_name = 'aero_point_0'
        self.add_subsystem(point_name, aero_group,
            promotes_inputs=['v', 'alpha', 'Mach_number', 're', 'rho', 'cg'])

        name = surface['name']

        # Connect the mesh from the geometry component to the analysis point
        self.connect(name + '.mesh', point_name + '.' + name + '.def_mesh')

        # Perform the connections with the modified names within the
        # 'aero_states' group.
        self.connect(name + '.mesh', point_name + '.aero_states.' + name + '_def_mesh')

        self.connect(name + '.t_over_c', point_name + '.' + name + '_perf.' + 't_over_c')