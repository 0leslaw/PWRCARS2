import math
from email.mime import image
from typing import Dict
import pygame
import numpy as np
import my_utils
from counter import *


class Car(pygame.sprite.Sprite):
    def __init__(self, x, y, image_path, weight, axle_prop: float=0.8):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(image_path).convert_alpha()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect(center=(x, y))
        self.delta_location: np.ndarray = np.array([0., 0.])
        self.init_location: np.ndarray = np.array([x, y])
        self.velocity: np.ndarray = np.array([0, 0])
        self.rotation = 0
        self.rotation_speed = 0
        self.steerwheel_turn_extent = Counter("S", magnitude=0.02, max_turn=0.5)     # straight
        self.longitudinal_speed = Counter("S", magnitude=0.1, max_turn=8)
        self.rebound_velocity = TwoDimentionalCounter(Counter("S", magnitude=0.1, max_turn=8,
                                                              normalizer_fun=my_utils.lin_to_regulated(my_utils.lin_to_exponential, 0.4, 1., 4.)))
        self.rebound_angular_vel = Counter("S", magnitude=0.02, max_turn=0.5)
        self.weight = weight
        self.axle_height = axle_prop * self.rect.height / 2

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
        if key[pygame.K_w] is True:
            self.longitudinal_speed.state = "R"
        elif key[pygame.K_s] is True:
            self.longitudinal_speed.state = "L"
        else:
            self.longitudinal_speed.state = "S"

        #   handle left to right
        flag_for_both = False
        if key[pygame.K_a] is True:
            self.steerwheel_turn_extent.state = "L"
            flag_for_both = True
        if key[pygame.K_d] is True:
            if flag_for_both:
                self.steerwheel_turn_extent.state = "S"
            else:
                self.steerwheel_turn_extent.state = "R"

        self.longitudinal_speed.two_side_scale_update(2)
        self.steerwheel_turn_extent.two_side_scale_update(5)

    def prepare_update(self):
        pass

    def move(self):
        # self.handle_collisions(rigid_bodies)
        self.handle_steering()
        import my_engine
        my_engine.calculate_car_speeds(self)
        self.update_rotation_image()
    def handle_collisions(self, rigid_bodies):
        '''
        responsible for handling collisions between all rigid bodies
        in the game (should be within close range to optimise)
        :param rigid_bodies:
        :return: None
        '''
        self.rect.collidelist(rigid_bodies)

    def print_status(self, screen):
        font = pygame.font.Font(None, 36)  # None means default system font, 36 is the font size
        message = self.delta_location.__str__() + self.longitudinal_speed.count.__str__()
        # Render the text onto a surface
        text_surface = font.render(message, 0,
                                   (255, 255, 255))  # True enables anti-aliasing, (255, 255, 255) is white color
        screen.blit(text_surface, (10, 10))

    def update_rotation_image(self):
        pass


    def draw(self, screen):
        rot_in_degrees = np.degrees(-self.rotation)
        rotated_img = pygame.transform.rotate(self.image, rot_in_degrees)
        rec = rotated_img.get_rect(center=self.rect.center)
        screen.blit(rotated_img, rec)
        self.draw_wheel_trail(screen)
        #   FIXME REMOVE
        #
        my_utils.VecsTest.vecs['velocity'] = self.velocity
        #

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

    