import math
import os.path
import sys
from abc import abstractmethod, ABC
from enum import Enum

import numpy as np
import pygame

import car_sprite
import globals
import map_sprite
import my_utils


class PerkSet:
    def __init__(self, limit=3):
        self.perks: list[Perk] = []
        self.chosen = 0
        self.limit = limit
        self.tick_of_last_release = 0

    def not_full(self):
        return len(self.perks) < self.limit

    def add_perk(self, perk):
        if self.not_full():
            self.perks.append(perk)
            return True
        return False

    def inc_pos(self):
        self.chosen = min(self.chosen + 1, len(self.perks) - 1)

    def dec_pos(self):
        self.chosen = max(self.chosen - 1, 0)

    def use_perk(self):
        # FIXME patch for the faulty key press detection system of pygame
        if globals.TICKS_PASSED - self.tick_of_last_release > 5:
            if len(self.perks) != 0:
                self.tick_of_last_release = globals.TICKS_PASSED
                used = self.perks.pop(self.chosen)
                used.release()
                self.dec_pos()


class PerkState(Enum):
    LAYING = 0
    TAKEN = 1
    ACTIVE = 2
    PASSED = 3


class Perk:
    def __init__(self, init_loc: np.ndarray, laying_image, active_image, state: PerkState = PerkState.LAYING):
        self.init_loc = init_loc
        self.curr_loc = init_loc
        self.laying_image = laying_image
        self.active_image = active_image
        self.state = state
        self.owner: car_sprite.Car | None = None
        self.state_change_frame = 0

    def update_state_change_frame(self):
        self.state_change_frame = globals.TICKS_PASSED

    def state_change_period(self):
        return globals.TICKS_PASSED - self.state_change_frame

    def reset(self):
        self.state = PerkState.LAYING
        self.update_state_change_frame()
        self.curr_loc = self.init_loc

    def draw_laying(self, screen, offset):
        screen.blit(self.laying_image, self.init_loc - offset + (0, 5*math.sin(globals.TICKS_PASSED/3)))

    def check_pickups(self, map: map_sprite.Map):
        for player in map.players:
            if my_utils.rectangles_collide((*self.curr_loc, self.laying_image.get_width(), self.laying_image.get_height()),
                                           (*player.abs_location, player.rect.width, player.rect.height))\
                    and player.perks.not_full():
                player.perks.add_perk(self)
                self.owner = player
                self.state = PerkState.TAKEN
                self.update_state_change_frame()

    @abstractmethod
    def release(self):
        pass

    @abstractmethod
    def draw_released(self, screen, offset):
        pass

    @abstractmethod
    def draw_hit(self, screen, offset):
        pass

    def check_hits(self, map: map_sprite.Map):
        for player in map.players:
            wheels = player.get_all_wheels_abs_positions(as_arrays=False)
            perk_vertices = self.curr_loc, self.curr_loc + (self.active_image.get_width(), )
            if my_utils.rectangles_collide((*self.curr_loc, self.active_image.get_width(), self.active_image.get_height()),
                                           (*player.abs_location, player.rect.width, player.rect.height)):
                self.hit_action(player)

    @abstractmethod
    def hit_action(self, one_hit: car_sprite.Car):
        pass

    def draw_on_map(self, screen, offset):
        """handles all states"""
        if self.state == PerkState.LAYING:
            self.draw_laying(screen, offset)
        if self.state == PerkState.ACTIVE:
            self.draw_released(screen, offset)
        if self.state == PerkState.PASSED:
            self.draw_hit(screen, offset)

    @abstractmethod
    def update(self, map: map_sprite.Map):
        pass


class MinePerk(Perk, ABC):
    def __init__(self, init_loc, state: PerkState = PerkState.LAYING):
        laying_image = pygame.image.load('./textures/perks/laying/mine.png').convert_alpha()
        active_image = pygame.image.load('./textures/perks/active/mine.png').convert_alpha()
        super().__init__(init_loc, laying_image, active_image, state)
        self.hit_images = self.load_hit_images()
        self.explosion_duration_in_ticks = 30

    def load_hit_images(self):
        filenames = [os.path.join("./textures/perks/passed/mine/", filename) for filename in os.listdir("./textures/perks/passed/mine/")]
        filenames = sorted(filenames, key=my_utils.get_single_int_from_string)
        return [pygame.image.load(filename) for filename in filenames]

    def hit_action(self, one_hit: car_sprite.Car):
        if one_hit == self.owner:
            return
        self.owner = one_hit
        ste = one_hit.steerwheel_turn_extent
        ste.max_turn *= 3
        if ste.count > 0:
            ste.set_to_max()
        else:
            ste.set_to_min()
        self.state = PerkState.PASSED
        self.update_state_change_frame()

    def release(self):
        self.curr_loc = self.owner.abs_location.copy()
        self.state = PerkState.ACTIVE
        self.update_state_change_frame()

    def draw_released(self, screen, offset):
        if self.state == PerkState.ACTIVE:
            screen.blit(self.active_image, self.curr_loc - offset)

    def draw_hit(self, screen, offset):
        chosen_ind = min(math.floor(len(self.hit_images) * (self.state_change_period() / self.explosion_duration_in_ticks)),
                         len(self.hit_images) - 1)
        screen.blit(self.hit_images[chosen_ind], self.curr_loc - offset)

    def update(self, map: map_sprite.Map):
        if self.state == PerkState.LAYING:
            self.check_pickups(map)

        if self.state == PerkState.ACTIVE:
            self.check_hits(map)

        if self.state == PerkState.PASSED:
            ste = self.owner.steerwheel_turn_extent
            if self.state_change_period() < 3:
                if ste.count > 0:
                    ste.set_to_max()
                else:
                    ste.set_to_min()
            if self.state_change_period() == 3:
                ste.max_turn /= 3
            if self.state_change_period() > self.explosion_duration_in_ticks:
                self.reset()
