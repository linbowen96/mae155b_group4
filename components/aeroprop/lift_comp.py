import numpy as np

from openmdao.api import ExplicitComponent


class liftComp(ExplicitComponent):

    # def initialize(self):
    #     self.options.deCLare('CL', types=float)

    def setup(self):
        self.add_input('speed')
        self.add_input('density')
        self.add_input('CL')
        self.add_input('S_w')
        self.add_output('lift')

        self.declare_partials('lift', 'speed')
        self.declare_partials('lift', 'density')
        self.declare_partials('lift', 'CL')
        self.declare_partials('lift', 'S_w')

    def compute(self, inputs, outputs):
        # CL = self.options['CL']

        speed = inputs['speed']
        density = inputs['density']
        CL = inputs['CL']
        S_w = inputs['S_w']
        outputs['lift'] = CL * 0.5 * speed ** 2 * density * S_w

    def compute_partials(self, inputs, partials):
        # CL = self.options['CL']

        speed = inputs['speed']
        density = inputs['density']
        CL = inputs['CL']
        S_w = inputs['S_w']

        partials['lift', 'speed'] = CL * density * speed * S_w
        partials['lift', 'density'] = CL * 0.5 * speed ** 2 * S_w
        partials['lift', 'CL'] = density * 0.5 * speed ** 2 * S_w
        partials['lift', 'S_w'] = CL * density * 0.5 * speed ** 2