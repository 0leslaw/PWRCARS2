from typing import Callable
import math
import numpy as np
import my_utils as utils


class Counter:

    def __init__(self, init_state, init_count=0, magnitude=1, max_turn=10, normalizer_fun: Callable = lambda x: x):
        Counter.magnitude = magnitude
        Counter.max_turn = max
        self.normalizer_fun = normalizer_fun
        self._count = init_count
        self.state = init_state
        self.max_turn = max_turn
        self.magnitude = magnitude

    @property
    def count(self):
        return self.normalizer_fun(self._count)

    @count.setter
    def count(self, value):
        self._count = np.clip(value, -self.max_turn, self.max_turn)

    def reset(self):
        self._count = 0

    def set_to_max(self):
        self._count = self.max_turn

    def set_to_min(self):
        self._count = -self.max_turn

    def increment(self, amm=None):
        if amm is None:
            amm = self.magnitude
        self._count += amm

    def get_state(self):
        return self.state

    def two_side_scale_update(self, tilt_reduction_reaction=0):
        if self.state == "S":
            self.diminish_two_side_scale_amplitude()
        elif self.state == "L":
            self.dec_two_side_scale(tilt_reduction_reaction)
        elif self.state == "R":
            self.inc_two_side_scale(tilt_reduction_reaction)

    def diminish_two_side_scale_amplitude(self):
        inc = math.copysign(self.magnitude, -self.count)
        self._count = self._count + inc
        #   if we moved past the center
        if utils.same_sign(self._count, inc):
            self._count = 0

    def dec_two_side_scale(self, tilt_reduction_reaction=0):
        self._count = max(-self.max_turn, self._count - self.magnitude)
        if self._count > 0:
            for i in range(tilt_reduction_reaction):
                self._count = max(-self.max_turn, self._count - self.magnitude)

    def inc_two_side_scale(self, tilt_reduction_reaction):
        self._count = min(self.max_turn, self._count + self.magnitude)
        if self._count < 0:
            for i in range(tilt_reduction_reaction):
                self._count = min(self.max_turn, self._count + self.magnitude)


class TwoDimentionalCounter:
    def __init__(self, counter: Counter, init_vector: np.ndarray = np.array([0, 0])):
        self.counter = counter
        self.start_vector = init_vector

    @property
    def vector_now(self):
        return self.counter.count * self.start_vector

    def start(self, start_vector: np.ndarray):
        self.start_vector = start_vector
        self.counter.set_to_max()

    def update_counter(self):
        self.counter.diminish_two_side_scale_amplitude()
