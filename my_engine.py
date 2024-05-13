import math

import numpy as np
import pygame

import car_sprite
from map_sprite import Map
import my_utils
from my_utils import lin_to_exponential
from config_loaded import ConfigData


#   THE CALCULATIONS ARE *NOT* PHYSICALLY ACCURATE

def calculate_car_speeds(car: car_sprite.Car):
    steering_angle = car.steerwheel_turn_extent.count

    car.rotation_speed = steering_angle * lin_to_exponential(car.longitudinal_speed.count, coef=0.1,
                                                             max_amplitude=0.5)
    car.rotation_speed += car.rebound_angular_vel.count
    car.rebound_velocity.update_counter()
    car.rebound_angular_vel.two_side_scale_update()
    apply_speeds(car)


def apply_speeds(car: car_sprite):
    car.rotation += car.rotation_speed
    # car.rotation = car.rotation % (2*math.pi)
    side_traction_loss = car.rotation_speed / math.pi
    side_vel = -10 * side_traction_loss * car.longitudinal_speed.count

    forward_vel = 10 * (1 - side_traction_loss) * lin_to_exponential(-car.longitudinal_speed.count, coef=0.4,
                                                                     degree=1, max_amplitude=4)
    absolute_x_vec = np.array([side_vel, forward_vel])
    # absolute_x_vec = np.array([-20 * lin_to_regulated(car.rotation_speed, degree=4) * car.gas_or_brake_pedal_extent.counter,
    #                            10 * lin_to_regulated(-car.gas_or_brake_pedal_extent.counter, degree=2, max_amplitude=2)])
    delta_x_vec = my_utils.rotate_vector(absolute_x_vec, car.rotation)
    car.velocity = delta_x_vec + car.rebound_velocity.vector_now
    car.delta_location += car.velocity
    # delta_x_vec[1] = -delta_x_vec[1]
    # car.rect.center = car.location





def get_vector_along_wall_tangent(point_of_contact: np.ndarray, map: Map):
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


    # TODO is it even a correct word
    def helper(radius, resolution_subdivision):
        wall_points = []
        step_angle = 2 * np.pi / resolution_subdivision
        directrix = np.array([0, radius])
        freeze_flag = True
        #   find any point outside the wall for a clear start
        while freeze_flag:
            for _ in range(resolution_subdivision):
                print("petla1")
                directrix = my_utils.rotate_vector(directrix, step_angle)
                if map.get_pixel_from_mask_map(point_of_contact + directrix) != ConfigData.get_attr('mask_color'):
                    freeze_flag = False
                    break
            if freeze_flag:
                directrix = 2 * directrix
                resolution_subdivision *= 2

        freeze_flag = True
        #   make sure we are in the beginning of wall
        while freeze_flag:
            for i in range(resolution_subdivision):
                directrix = my_utils.rotate_vector(directrix, step_angle)
                print("petla2")
                if map.get_pixel_from_mask_map(point_of_contact + directrix) == ConfigData.get_attr('mask_color'):
                    freeze_flag = False
                    break
            if freeze_flag:
                directrix = 2 * directrix
                resolution_subdivision *= 2


        #   while we haven't left the wall zone
        while map.get_pixel_from_mask_map(point_of_contact + directrix) == ConfigData.get_attr('mask_color'):
            wall_points.append(directrix)
            print("petla3")
            print(directrix)
            directrix = my_utils.rotate_vector(directrix, step_angle)
            print(wall_points[-1] - wall_points[0])
        return wall_points

    for i in range(5):
        wall_points = helper(50 + 20 * i, 200 + 60 * i)
        if len(wall_points) > 1:
            break

    return wall_points[-1] - wall_points[0]


def get_wall_normal(point_of_contact: np.ndarray, map: Map):
    """
    by rotating the vector along tangent by 90 deg, we are sure it returns a normal
    :param image: has black pixels where we detect collision
    :param point_of_contact:
    :return: normal unit vector of normal of the approximated wall tangent
    """
    wall_tangent = get_vector_along_wall_tangent(point_of_contact, map)
    #   FIXME RM
    #
    my_utils.VecsTest.vecs['wall_tangent'] = 70 * my_utils.get_unit_vector(wall_tangent)
    #
    return my_utils.get_unit_vector(my_utils.rotate_vector(wall_tangent, np.pi / 2))


def get_rebound_direction(point_of_contact: np.ndarray, movement_direction: np.ndarray, map: Map,
                          to_unit=False) -> np.ndarray:
    """
    :param to_unit: specifies if you want the result to be a unit vector
    :param point_of_contact:
    :param movement_direction:
    :param map: has black pixels where we detect collision
    :return: rebound direction
    """
    wall_normal = get_wall_normal(point_of_contact, map)
    # wall_normal = np.array([0, 1])
    #   FIXME RM
    #
    my_utils.VecsTest.vecs['wall_normal'] = 70 * wall_normal
    #
    return my_utils.mirror_vector(movement_direction, wall_normal)


def get_turn_rebound_direction(point_of_contact: np.ndarray, center_of_mass: np.ndarray, map: Map):
    """

    :param center_of_mass:
    :param point_of_contact:
    :param movement_direction:
    :param image:
    :return: -1 if clockwise and 1 if counterclockwise
    """
    wall_normal = get_wall_normal(point_of_contact, map)
    contact_to_center_vec = center_of_mass - point_of_contact
    return -1 if my_utils.get_angle_between_vectors(wall_normal, contact_to_center_vec) > 90 else 1


def handle_map_collision(car: car_sprite.Car, point_of_contact: np.ndarray, map: Map):
    dampening_factor = 0.1
    rebound_vel = get_rebound_direction(point_of_contact,
                                        car.velocity,
                                        map,
                                        True)
    rebound_vel *= dampening_factor
    # FIXME REMOVE AFTER PRODUCITON
    #
    my_utils.VecsTest.vecs['rebound_dir'] = 70*my_utils.get_unit_vector(rebound_vel)
    #
    car.longitudinal_speed.reset()
    car.rebound_velocity.start(rebound_vel)
    car.rebound_angular_vel.count = (get_turn_rebound_direction(point_of_contact, car.abs_location, map)
                                     * abs(car.rotation_speed))
    car.delta_location += 20 * my_utils.get_unit_vector(my_utils.get_unit_vector(rebound_vel))


#   TODO USIADZ NA SPOKOJNIE I PRZEANALIZUJ JAKA FUNKCJE PELNIA POLA CAR