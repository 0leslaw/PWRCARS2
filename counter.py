from typing import Callable
import math
import numpy as np
import my_utils as utils


class Counter:

    def __init__(self, init_state, counter_val=0, magnitude=1, max_turn=10):
        Counter.magnitude = magnitude
        Counter.max_turn = max
        self.counter = counter_val
        self.state = init_state
        self.max_turn = max_turn
        self.magnitude = magnitude

    def reset(self):
        self.counter = 0

    def increment(self, amm=None):
        if amm is None:
            amm = self.magnitude
        self.counter += amm

    def get_state(self):
        return self.state

    def two_side_scale_update(self):
        if self.state == "S":
            inc = math.copysign(self.magnitude, -self.counter)
            self.counter = self.counter + inc
            #   we moved past the center
            if utils.same_sign(self.counter, inc):
                self.counter = 0

        elif self.state == "L":
            self.counter = max(-self.max_turn, self.counter - self.magnitude)

        elif self.state == "R":
            self.counter = min(self.max_turn, self.counter + self.magnitude)
