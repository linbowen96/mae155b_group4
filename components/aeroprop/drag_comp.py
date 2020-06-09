import numpy as np

from openmdao.api import ExplicitComponent


class dragComp(ExplicitComponent):

    # def initialize(self):
    #     self.options.declare('CD', types=float)

    def setup(self):
        self.add_input('speed')
        self.add_input('density')
        self.add_input('CD')
        self.add_input('S_w')
        self.add_output('drag')

        self.declare_partials('drag', 'speed')
        self.declare_partials('drag', 'density')
        self.declare_partials('drag', 'CD')
        self.declare_partials('drag', 'S_w')

    def compute(self, inputs, outputs):
        # CD = self.options['CD']

        speed = inputs['speed']
        density = inputs['density']
        CD = inputs['CD']
        S_w = inputs['S_w']
        outputs['drag'] = CD * 0.5 * speed ** 2 * density * S_w

    def compute_partials(self, inputs, partials):
        # CD = self.options['CD']

        speed = inputs['speed']
        density = inputs['density']
        CD = inputs['CD']
        S_w = inputs['S_w']

        partials['drag', 'speed'] = CD * density * speed * S_w
        partials['drag', 'density'] = CD * 0.5 * speed ** 2 * S_w
        partials['drag', 'CD'] = density * 0.5 * speed ** 2 * S_w
        partials['drag', 'S_w'] = CD * density * 0.5 * speed ** 2