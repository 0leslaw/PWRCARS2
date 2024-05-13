import math
from enum import Enum

import numpy as np

import globals


class PerkState(Enum):
    LAYING = 0
    TAKEN = 1
    ACTIVE = 2


class Perk:
    def __init__(self, init_loc: np.ndarray, laying_image, active_image, state: PerkState = PerkState.LAYING):
        self.init_loc = init_loc
        self.laying_image = laying_image
        self.active_image = active_image
        self.state = state

    def draw_laying(self, screen, offset):
        screen.blit(self.laying_image, self.init_loc - offset + (0, 5*math.sin(globals.TICKS_PASSED)))

class MinePerk(Perk):
    def __init__(self, init_loc, laying_image, active_image, state: PerkState = PerkState.LAYING):
        super().__init__(init_loc, laying_image, active_image, state)



