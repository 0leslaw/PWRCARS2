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

    car.rotation_speed = steering_angle * lin_to_regulated(car.gas_or_brake_pedal_extent.counter, coef=0.1, max_amplitude=0.5)

    apply_speeds(car)


def apply_speeds(car: car_sprite):
    car.rotation += car.rotation_speed
    # car.rotation = car.rotation % (2*math.pi)
    side_traction_loss = car.rotation_speed / math.pi
    side_vel = -10 * side_traction_loss * car.gas_or_brake_pedal_extent.counter
    forward_vel = 10 * (1 - side_traction_loss) * lin_to_regulated(-car.gas_or_brake_pedal_extent.counter, coef=0.4, degree=1, max_amplitude=2)
    absolute_x_vec = np.array([side_vel, forward_vel])
    # absolute_x_vec = np.array([-20 * lin_to_regulated(car.rotation_speed, degree=4) * car.gas_or_brake_pedal_extent.counter,
    #                            10 * lin_to_regulated(-car.gas_or_brake_pedal_extent.counter, degree=2, max_amplitude=2)])
    delta_x_vec = utils.rotate_vector(absolute_x_vec, car.rotation)
    car.location += delta_x_vec
    # delta_x_vec[1] = -delta_x_vec[1]
    # car.rect.center = car.location


def lin_to_regulated(x, coef=3, degree=3, max_amplitude=1.3) -> int:
    return np.clip(coef*x**degree, -max_amplitude, max_amplitude)
