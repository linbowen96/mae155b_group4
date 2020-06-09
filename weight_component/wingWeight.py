import numpy as np

from openmdao.api import ExplicitComponent


class wingWeightComp(ExplicitComponent):

    def initialize(self):
        self.options.declare('N', types=float)
        self.options.declare('t_c', types=float)
        self.options.declare('AR', types=float)
        self.options.declare('sweep', types=float)
        self.options.declare('taper', types=float)

    def setup(self):
        self.add_input('W0')
        self.add_input('S_w')
        self.add_output('W_wing')

        self.declare_partials('W_wing', 'W0')
        self.declare_partials('W_wing', 'S_w')

    def compute(self, inputs, outputs):
        N = self.options['N']
        t_c = self.options['t_c']
        AR = self.options['AR']
        sweep = self.options['sweep']
        taper = self.options['taper']

        W0 = inputs['W0']
        S_w = inputs['S_w']

        cosSweep = np.cos(sweep * (np.pi / 180))

        outputs['W_wing'] = 0.0051 * W0 ** 0.557 * N ** 0.557 * S_w ** 0.649 * AR ** 0.5 * t_c ** -0.4 * (1 + taper) ** 0.1 * cosSweep ** -1 * 0.2 ** 0.1 * S_w ** 0.1

    def compute_partials(self, inputs, partials):
        N = self.options['N']
        t_c = self.options['t_c']
        AR = self.options['AR']
        sweep = self.options['sweep']
        taper = self.options['taper']

        W0 = inputs['W0']
        S_w = inputs['S_w']

        cosSweep = np.cos(sweep * np.pi / 180)

        partials['W_wing', 'W0'] = 0.0051 * 0.557 * W0 ** -0.443 * N ** 0.557 * S_w ** 0.649 * AR ** 0.5 * t_c ** -0.4 * (1 + taper) ** 0.1 * cosSweep ** -1 * 0.2 ** 0.1 * S_w ** 0.1
        partials['W_wing', 'S_w'] = 0.0051 * W0 ** 0.557 * N ** 0.557 * 0.649 * S_w ** -0.351 * AR ** 0.5 * t_c ** -0.4 * (1 + taper) ** 0.1 * cosSweep ** -1 * 0.2 ** 0.1 * 0.1 * S_w ** -0.9