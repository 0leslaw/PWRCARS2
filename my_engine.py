import math

import numpy as np
import pygame

import car_sprite
import my_utils
import my_utils as utils
from config_loaded import ConfigData

#   THE CALCULATIONS ARE *NOT* PHYSICALLY ACCURATE

def calculate_car_speeds(car: car_sprite.Car):
    steering_angle = car.steerwheel_turn_extent.counter

    car.rotation_speed = steering_angle * lin_to_regulated(car.longitudinal_speed.counter, coef=0.1,
                                                           max_amplitude=0.5)

    apply_speeds(car)


def apply_speeds(car: car_sprite):
    car.rotation += car.rotation_speed
    # car.rotation = car.rotation % (2*math.pi)
    side_traction_loss = car.rotation_speed / math.pi
    side_vel = -10 * side_traction_loss * car.longitudinal_speed.counter
    forward_vel = 10 * (1 - side_traction_loss) * lin_to_regulated(-car.longitudinal_speed.counter, coef=0.4,
                                                                   degree=1, max_amplitude=4)
    absolute_x_vec = np.array([side_vel, forward_vel])
    # absolute_x_vec = np.array([-20 * lin_to_regulated(car.rotation_speed, degree=4) * car.gas_or_brake_pedal_extent.counter,
    #                            10 * lin_to_regulated(-car.gas_or_brake_pedal_extent.counter, degree=2, max_amplitude=2)])
    delta_x_vec = utils.rotate_vector(absolute_x_vec, car.rotation)
    car.delta_location += delta_x_vec
    # delta_x_vec[1] = -delta_x_vec[1]
    # car.rect.center = car.location


def lin_to_regulated(x, coef=3, degree=3, max_amplitude=1.3) -> int:
    return np.clip(coef * x ** degree, -max_amplitude, max_amplitude)


def get_vector_along_wall_tangent(point_of_contact: np.ndarray, image):
    """
    will make a small circle of a small resolution (number of vertices) around the
    point of contact sampling for a wall approximation, then returns
    its tangent. Note that by rotating the directrix in the same direction we contain the
    information on the orientation of the wall, thus we can know the normal will point
    to the side where the point contacted the wall
    :param point_of_contact:
    :param image:
    :return: vector along wall tangent
    """
    radius = 50
    resolution_subdivision = 200
    step_angle = 2 * np.pi / resolution_subdivision

    # TODO is it even a correct word
    directrix = np.array([0, radius])
    #   find any point outside the wall for a clear start
    while image.get_at((point_of_contact + directrix).astype(int)) == ConfigData.mask_color:
        print("petla1")
        directrix = my_utils.rotate_vector(directrix, step_angle)
    #   assume we have to do this in a while loop because there might be a calculation err
    while image.get_at((point_of_contact + directrix).astype(int)) != ConfigData.mask_color:
        directrix = my_utils.rotate_vector(directrix, step_angle)
        print("petla2")
    wall_points = []
    #   while we haven't left the wall zone
    while image.get_at((point_of_contact + directrix).astype(int)) == ConfigData.mask_color:
        wall_points.append(directrix)
        print("petla3")
        print(directrix)
        directrix = my_utils.rotate_vector(directrix, step_angle)
        print(wall_points[-1] - wall_points[0])
    return wall_points[-1] - wall_points[0]


def get_wall_normal(point_of_contact: np.ndarray, image):
    """
    by rotating the vector along tangent by 90 deg, we are sure it returns a normal
    :param image: has black pixels where we detect collision
    :param point_of_contact:
    :return: normal unit vector of normal of the approximated wall tangent
    """
    wall_tangent = get_vector_along_wall_tangent(point_of_contact, image)

    return my_utils.get_unit_vector(my_utils.rotate_vector(wall_tangent, -np.pi / 2))


def get_rebound_direction(point_of_contact: np.ndarray, movement_direction: np.ndarray, image, to_unit=False) -> np.ndarray:
    """
    :param to_unit: specifies if you want the result to be a unit vector
    :param point_of_contact:
    :param movement_direction:
    :param image: has black pixels where we detect collision
    :return: rebound direction
    """
    wall_normal = get_wall_normal(point_of_contact, image)
    # wall_normal = np.array([0, 1])
    #   FIXME RM
    #
    my_utils.VecsTest.vecs['wall_normal'] = wall_normal
    #
    return my_utils.mirror_vector(movement_direction, wall_normal)


def get_turn_rebound_direction(point_of_contact: np.ndarray, center_of_mass: np.ndarray, image):
    """

    :param center_of_mass:
    :param point_of_contact:
    :param movement_direction:
    :param image:
    :return: -1 if clockwise and 1 if counterclockwise
    """
    wall_normal = get_wall_normal(point_of_contact, image)
    contact_to_center_vec = center_of_mass - point_of_contact
    return -1 if my_utils.get_angle_between_vectors(wall_normal, contact_to_center_vec) > 90 else 1


def handle_map_collision(car: car_sprite.Car, point_of_contact: np.ndarray, image):
    dampening_factor = 0.5
    # car.rotation_speed = (get_turn_rebound_direction(point_of_contact, car.abs_location, image)
    #                       * abs(car.rotation_speed) * dampening_factor)
    rebound_direction = get_rebound_direction(point_of_contact,
                                              my_utils.rotate_vector(np.array([0, -1]), car.rotation),
                                              image,
                                              True)
    new_speed_vec = car.longitudinal_speed.counter * rebound_direction
    # FIXME REMOVE AFTER PRODUCITON
    #
    my_utils.VecsTest.vecs['rebound_dir'] = 70*rebound_direction
    #
    car.transverse_speed = new_speed_vec[0]
    car.longitudinal_speed.counter = new_speed_vec[1]
    car.delta_location += 100 * rebound_direction
