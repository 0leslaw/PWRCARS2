import math
from collections import deque
from email.mime import image
from typing import Dict
import pygame
import numpy as np

import my_utils
from counter import *


class Car(pygame.sprite.Sprite):
    def __init__(self, x_pos_on_screen, y_pos_on_screen, image_path, initial_position=np.array([0., 0.]), initial_rotation=0, keys=None):
        pygame.sprite.Sprite.__init__(self)
        if keys is None:
            keys = {'forward': pygame.K_w, 'left': pygame.K_a, 'backward': pygame.K_s, 'right': pygame.K_d}
        self.keys = keys
        self.image = pygame.image.load(image_path).convert_alpha()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect(center=(x_pos_on_screen, y_pos_on_screen))
        self.path = my_utils.reset_queue_to_length(np.array([0., 0.]), 20)
        self.ticks_in_wall = Counter("S", max_turn=5)
        self.delta_location: np.ndarray = initial_position
        self.init_location: np.ndarray = np.array([x_pos_on_screen, y_pos_on_screen])
        self.velocity: np.ndarray = np.array([0, 0])
        self.rotation = initial_rotation
        self.rotation_speed = 0
        self.steerwheel_turn_extent = Counter("S", magnitude=0.02, max_turn=0.5)     # straight
        self.longitudinal_speed = Counter("S", magnitude=0.1, max_turn=8)
        self.rebound_velocity = TwoDimentionalCounter(Counter("S", magnitude=0.1, max_turn=8,
                                                              normalizer_fun=my_utils.lin_to_regulated(my_utils.lin_to_exponential, 0.4, 1., 4.)))
        self.rebound_angular_vel = Counter("S", magnitude=0.02, max_turn=0.5)

    @property
    def abs_location(self):
        """is the abstract location of the car i.e. where it would be
        if we didn't consider a player-central perspective"""
        return self.init_location + self.delta_location

    def handle_steering(self):
        key = pygame.key.get_pressed()
        absolute_vel_change_vec = np.ndarray([0, 0])

        self.longitudinal_speed.state = "S"
        self.steerwheel_turn_extent.state = "S"

        #   handle forward backward
        if key[self.keys['forward']] is True:
            self.longitudinal_speed.state = "R"
        elif key[self.keys['backward']] is True:
            self.longitudinal_speed.state = "L"
        else:
            self.longitudinal_speed.state = "S"

        #   handle left to right
        flag_for_both = False
        if key[self.keys['left']] is True:
            self.steerwheel_turn_extent.state = "L"
            flag_for_both = True
        if key[self.keys['right']] is True:
            if flag_for_both:
                self.steerwheel_turn_extent.state = "S"
            else:
                self.steerwheel_turn_extent.state = "R"

        self.longitudinal_speed.two_side_scale_update(2)
        self.steerwheel_turn_extent.two_side_scale_update(5)

    def move(self):
        # self.handle_collisions(rigid_bodies)
        self.handle_steering()
        from my_engine import calculate_car_speeds
        calculate_car_speeds(self)
        self.update_path()

    def update_path(self):
        self.path.popleft()
        self.path.append(self.delta_location)
        if self.ticks_in_wall.count == self.ticks_in_wall.max_turn:
            self.handle_errors()

    def handle_errors(self):
        self.ticks_in_wall.reset()
        self.delta_location = self.path.popleft()
        self.path.append(np.array(self.delta_location))
        print("10 razy w tym")
        self.path = my_utils.reset_queue_to_length(self.delta_location, len(self.path))

    def reset_dynamics(self):
        self.velocity = np.ndarray([0, 0])
        self.rotation_speed = 0
        self.longitudinal_speed.reset()
        self.rebound_velocity.reset()

    def print_status(self, screen):
        font = pygame.font.Font(None, 36)  # None means default system font, 36 is the font size
        message = self.delta_location.__str__() + self.longitudinal_speed.count.__str__()
        # Render the text onto a surface
        text_surface = font.render(message, 0,
                                   (255, 255, 255))  # True enables anti-aliasing, (255, 255, 255) is white color
        screen.blit(text_surface, (10, 10))

    def draw(self, screen, context_player_delta_loc=None):
        rot_in_degrees = np.degrees(-self.rotation)
        rotated_img = pygame.transform.rotate(self.image, rot_in_degrees)
        if context_player_delta_loc is not None:
            rec = rotated_img.get_rect(center=self.abs_location - context_player_delta_loc)
        else:
            rec = rotated_img.get_rect(center=self.rect.center)
        screen.blit(rotated_img, rec)
        self.draw_wheel_trail(screen)
        #   FIXME REMOVE
        #
        my_utils.VecsTest.vecs['velocity'] = self.velocity
        #

    def get_vector_to_other(self, other):
        return other.delta_location - self.delta_location

    def draw_wheel_trail(self, screen):
        #   TODO
        left_wheel_pos, right_wheel_pos = self.get_wheels_rel_to_mid(is_back_wheels=True)
        pygame.draw.circle(screen, center=left_wheel_pos, color=(0, 0, 0), radius=2)
        pass

    def get_wheel_pos_rel_to_car(self, is_back_wheels=True):
        real_distance_scaler = 0.85
        h = self.image.get_height()/2 * real_distance_scaler
        a = self.image.get_width()/2 * real_distance_scaler
        # print(self.image.get_height())
        if not is_back_wheels:
            h = -h
        left_wheel_pos = (a, h)
        right_wheel_pos = (-a, h)
        return left_wheel_pos, right_wheel_pos

    def get_wheels_rel_to_mid(self, is_back_wheels=True, as_arrays=False):
        """
        get wheel position relative to car initial location rotated
        :param as_arrays:
        :param is_back_wheels:
        :return:
        """
        relative_left_wheel_pos, relative_right_wheel_pos = self.get_wheel_pos_rel_to_car(is_back_wheels)
        r_l_vec = np.array(relative_left_wheel_pos)
        r_r_vec = np.array(relative_right_wheel_pos)

        r_l_vec = my_utils.rotate_vector(r_l_vec, self.rotation) + self.init_location
        r_r_vec = my_utils.rotate_vector(r_r_vec, self.rotation) + self.init_location
        if not as_arrays:
            return tuple(r_l_vec), tuple(r_r_vec)
        else:
            return r_l_vec, r_r_vec

    def get_all_wheels_positions(self, as_arrays=True):
        return *self.get_wheels_rel_to_mid(as_arrays=as_arrays), *self.get_wheels_rel_to_mid(is_back_wheels=False, as_arrays=as_arrays)

    def get_all_wheels_abs_positions(self, as_arrays=True):
        """returns the absolute abstract positions of the wheels in order LB, RB, LF, RF"""
        left_back, right_back = self.get_wheels_rel_to_mid(as_arrays=True)
        left_front, right_front = self.get_wheels_rel_to_mid(is_back_wheels=False, as_arrays=True)
        if as_arrays:
            return (left_back + self.delta_location, right_back + self.delta_location,
                    left_front + self.delta_location, right_front + self.delta_location)
        else:
            return (tuple(left_back + self.delta_location), tuple(right_back + self.delta_location),
                    tuple(left_front + self.delta_location), tuple(right_front + self.delta_location))

    