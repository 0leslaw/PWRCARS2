import math

import numpy as np
import pygame

import car_sprite
import my_utils as utils


def calc(car: car_sprite.Car):
    # curr_angle = math.atan2(v0[0], v0[1]) - np.radians(90)
    #
    # rotation_matrix = np.array([[np.cos(curr_angle), -np.sin(curr_angle)],
    #                             [np.sin(curr_angle), np.cos(curr_angle)]])
    #
    # vector_column = np.array(absolute_vel_change_vec).reshape((2, 1))
    #
    # # Rotate the vector using the rotation matrix
    # relative_vel_change_vec = np.dot(rotation_matrix, vector_column)
    #
    # # Convert the rotated vector back to a 1D array
    # relative_vel_change_vec = relative_vel_change_vec.flatten()

    # car.velocity[0] += absolute_vel_change_vec[0]
    steering_angle = car.steerwheel_turn_extent.counter

    car.rotation_speed = steering_angle

    apply_speeds(car)


def apply_speeds(car: car_sprite):
    car.rotation += car.rotation_speed
    # car.rotation = car.rotation % (2*math.pi)
    delta_x_vec = utils.rotate_vector(np.array([-1*root_on_whole_domain(car.rotation_speed) * car.gas_or_brake_pedal_extent.counter, 10*root_on_whole_domain(-car.gas_or_brake_pedal_extent.counter)]), car.rotation)
    car.location += delta_x_vec
    delta_x_vec[1] = -delta_x_vec[1]
    # car.image = pygame.transform.rotate(car.image, car.rotation_speed)
    # car.rect = car.image.get_rect()
    car.rect.center = car.location


def root_on_whole_domain(x, degree=5):
    return np.sign(x) * math.pow(abs(x), 1/degree)
