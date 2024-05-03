import math
from email.mime import image
from typing import Dict
import pygame
import numpy as np
from counter import Counter


class Car(pygame.sprite.Sprite):
    def __init__(self, x, y, image_path, weight, axle_prop: float=0.8):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(image_path).convert_alpha()
        self.rect = self.image.get_rect(center=(x, y))
        self.location = np.array([x, y])
        self.velocity = np.array([0, 0])
        self.rotation = 0
        self.rotation_speed = 0
        self.steerwheel_turn_extent = Counter("S", magnitude=0.02, max_turn=0.5)     # straight
        self.gas_or_brake_pedal_extent = Counter("S", magnitude=0.1, max_turn=5)
        self.weight = weight
        self.axle_height = axle_prop * self.rect.height / 2

    def handle_steering(self):
        key = pygame.key.get_pressed()
        absolute_vel_change_vec = np.ndarray([0, 0])

        self.gas_or_brake_pedal_extent.state = "S"
        self.steerwheel_turn_extent.state = "S"

        #   handle forward backward
        if key[pygame.K_w] is True:
            self.gas_or_brake_pedal_extent.state = "R"
        elif key[pygame.K_s] is True:
            self.gas_or_brake_pedal_extent.state = "L"
        else:
            self.gas_or_brake_pedal_extent.state = "S"

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

        self.gas_or_brake_pedal_extent.two_side_scale_update()
        self.steerwheel_turn_extent.two_side_scale_update(5)

    def prepare_update(self):
        pass

    def move(self):
        # self.handle_collisions(rigid_bodies)
        self.handle_steering()
        import my_engine
        my_engine.calc(self)
        self.update_rotation_image()
    def handle_collisions(self, rigid_bodies):
        '''
        responsible for handling collisions between all rigid bodies
        in the game (should be within close range to optimise)
        :param rigid_bodies:
        :return: None
        '''
        self.rect.collidelist(rigid_bodies)

    def print_status(self):
        print('Current')
        print(self.steerwheel_turn_extent.counter)
        # print(self.rotation)
        # print(self.location)

    def update_rotation_image(self):
        pass


    def draw(self, screen):
        rot = np.degrees(-self.rotation)
        im = pygame.transform.rotate(self.image, rot)
        rec = im.get_rect(center=self.rect.center)
        screen.blit(im, rec)
        left_wheel_pos, right_wheel_pos = self.get_back_wheel_pos_rel_to_car()
        # pygame.draw.circle(screen, center=left_wheel_pos, color=(0, 0, self.rotation_speed*5), radius=5)


    def get_back_wheel_pos_rel_to_car(self):
        h = self.image.get_height()/2
        a = self.image.get_width()/2
        print(self.image.get_height())

        left_wheel_pos = (a, -h)
        right_wheel_pos = (-a, -h)
        return left_wheel_pos, right_wheel_pos
