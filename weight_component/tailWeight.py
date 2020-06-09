import numpy as np

from openmdao.api import ExplicitComponent


class htailWeightComp(ExplicitComponent):

    def initialize(self):
        self.options.declare('N', types=float)
        self.options.declare('Lt', types=float)
        self.options.declare('AR_ht', types=float)
        self.options.declare('sweepht', types=float)
    

    def setup(self):
        self.add_input('W0')
        self.add_input('S_ht')
        self.add_output('W_ht')

        self.declare_partials('W_ht', 'W0')
        self.declare_partials('W_ht', 'S_ht')

    def compute(self, inputs, outputs):
        N = self.options['N']
        Lt = self.options['Lt']
        AR_ht = self.options['AR_ht']
        sweepht = self.options['sweepht']
       

        W0 = inputs['W0']
        S_ht = inputs['S_ht']

        cosSweepht = np.cos(sweepht * np.pi / 180)
        Ky = 0.3 * Lt

        outputs['W_ht'] = 0.0379 * 1.2 ** -0.25 * W0 ** 0.639 * N ** 0.1 * S_ht ** 0.75 * Lt ** -1 * Ky ** 0.704 * cosSweepht ** -1 * AR_ht ** 0.166

    def compute_partials(self, inputs, partials):
        N = self.options['N']
        Lt = self.options['Lt']
        AR_ht = self.options['AR_ht']
        sweepht = self.options['sweepht']

        W0 = inputs['W0']
        S_ht = inputs['S_ht']

        cosSweepht = np.cos(sweepht * np.pi / 180)
        Ky = 0.3 * Lt

        partials['W_ht', 'W0'] = 0.0379 * 1.2 ** -0.25 * 0.639 * W0 ** -0.361 * N ** 0.1 * S_ht ** 0.75 * Lt ** -1 * Ky ** 0.704 * cosSweepht ** -1 * AR_ht ** 0.166
        partials['W_ht', 'S_ht'] = 0.0379 * 1.2 ** -0.25 * W0 ** 0.639 * N ** 0.1 * 0.75 * S_ht ** -0.25 * Lt ** -1 * Ky ** 0.704 * cosSweepht ** -1 * AR_ht ** 0.166

class vtailWeightComp(ExplicitComponent):

    def initialize(self):
        self.options.declare('N', types=float)
        self.options.declare('Lt', types=float)
        self.options.declare('AR_vt', types=float)
        self.options.declare('sweepvt', types=float)
        self.options.declare('t_c',types=float)
    

    def setup(self):
        self.add_input('W0')
        self.add_input('S_vt')
        self.add_output('W_vt')

        self.declare_partials('W_vt', 'W0')
        self.declare_partials('W_vt', 'S_vt')

    def compute(self, inputs, outputs):
        N = self.options['N']
        Lt = self.options['Lt']
        AR_vt = self.options['AR_vt']
        sweepvt = self.options['sweepvt']
        t_c = self.options['t_c']
       

        W0 = inputs['W0']
        S_vt = inputs['S_vt']

        cosSweepvt = np.cos(sweepvt * np.pi / 180)
        Kz = Lt

        outputs['W_vt'] = 0.0026 * W0 ** 0.556 * N ** 0.536 * S_vt ** 0.5 * Lt ** -0.5 * Kz ** 0.875 * cosSweepvt ** -1 * AR_vt ** 0.35 * t_c ** -0.5

    def compute_partials(self, inputs, partials):
        N = self.options['N']
        Lt = self.options['Lt']
        AR_vt = self.options['AR_vt']
        sweepvt = self.options['sweepvt']
        t_c = self.options['t_c']

        W0 = inputs['W0']
        S_vt = inputs['S_vt']

        cosSweepvt = np.cos(sweepvt * np.pi / 180)
        Kz = Lt

        partials['W_vt', 'W0'] = 0.0026 * 0.556 * W0 ** -0.444 * N ** 0.536 * S_vt ** 0.5 * Lt ** -0.5 * Kz ** 0.875 * cosSweepvt ** -1 * AR_vt ** 0.35 * t_c ** -0.5
        partials['W_vt', 'S_vt'] = 0.0026 * W0 ** 0.556 * N ** 0.536 * 0.5 * S_vt ** -0.5 * Lt ** -0.5 * Kz ** 0.875 * cosSweepvt ** -1 * AR_vt ** 0.35 * t_c ** -0.5
