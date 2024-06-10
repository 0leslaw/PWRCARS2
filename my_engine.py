import math
import numpy as np
import car_sprite
from map_sprite import Map
import my_utils
from my_errors import StuckInWallError
from my_utils import lin_to_exponential
from config_loaded import ConfigData


#   THE CALCULATIONS ARE *NOT* PHYSICALLY ACCURATE

def calculate_car_speeds(car: car_sprite.Car):
    """
    Calculate the speeds of the car based on steering and longitudinal speed.

    Args:
        car (car_sprite.Car): The car object whose speeds are to be calculated.
    """
    steering_angle = car.steerwheel_turn_extent.count
    car.rotation_speed = steering_angle * lin_to_exponential(car.longitudinal_speed.count, coef=0.1, max_amplitude=0.5)
    car.rotation_speed += car.rebound_angular_vel.count
    car.rebound_velocity.update_counter()
    car.rebound_angular_vel.two_side_scale_update()
    apply_speeds(car)


def apply_speeds(car: car_sprite.Car):
    """
    Apply the calculated speeds to update the car's state.

    Args:
        car (car_sprite.Car): The car object to which speeds are applied.
    """
    car.rotation += car.rotation_speed
    side_traction_loss = car.rotation_speed / math.pi
    side_vel = -10 * side_traction_loss * car.longitudinal_speed.count

    forward_vel = 10 * (1 - side_traction_loss) * lin_to_exponential(-car.longitudinal_speed.count, coef=0.4,
                                                                     degree=1, max_amplitude=4)
    absolute_x_vec = np.array([side_vel, forward_vel])
    delta_x_vec = my_utils.rotate_vector(absolute_x_vec, car.rotation)
    car.velocity = delta_x_vec + car.rebound_velocity.vector_now
    car.delta_location += car.velocity


def get_vector_along_wall_tangent(point_of_contact: np.ndarray, map: Map):
    """
     will make a small circle of a small resolution (number of vertices) around the
    point of contact sampling for a wall approximation, then returns
    its tangent. Note that by rotating the directrix in the same direction we contain the
    information on the orientation of the wall, thus we can know the normal will point
    to the side where the point contacted the wall

    Args:
        point_of_contact (np.ndarray): The point of contact with the wall.
        map (Map): The map object containing wall information.

    Returns:
        np.ndarray: The vector along the wall tangent.
    """
    radius = 50
    resolution_subdivision = 200

    def helper(radius, resolution_subdivision):
        wall_points = []
        step_angle = 2 * np.pi / resolution_subdivision
        directrix = np.array([0, radius])
        freeze_flag = True
        # Find any point outside the wall for a clear start
        for _ in range(resolution_subdivision):
            directrix = my_utils.rotate_vector(directrix, step_angle)
            if map.get_pixel_from_mask_map(point_of_contact + directrix) != ConfigData.get_attr('mask_color'):
                freeze_flag = False
                break

        if freeze_flag:
            raise StuckInWallError

        freeze_flag = True
        # Make sure we are in the beginning of the wall
        for i in range(resolution_subdivision):
            directrix = my_utils.rotate_vector(directrix, step_angle)
            if map.get_pixel_from_mask_map(point_of_contact + directrix) == ConfigData.get_attr('mask_color'):
                freeze_flag = False
                break

        if freeze_flag:
            raise StuckInWallError

        # While we haven't left the wall zone
        while map.get_pixel_from_mask_map(point_of_contact + directrix) == ConfigData.get_attr('mask_color'):
            wall_points.append(directrix)
            directrix = my_utils.rotate_vector(directrix, step_angle)
        return wall_points

    for i in range(2):
        wall_points = helper(50 + 40 * i, 200 + 80 * i)
        if len(wall_points) > 1:
            break

    return wall_points[-1] - wall_points[0]


def get_wall_normal(point_of_contact: np.ndarray, map: Map):
    """
    Calculate the wall normal by rotating the wall tangent by 90 degrees.

    Args:
        point_of_contact (np.ndarray): The point of contact with the wall.
        map (Map): The map object containing wall information.

    Returns:
        np.ndarray: The normal unit vector of the approximated wall tangent.
    """
    wall_tangent = get_vector_along_wall_tangent(point_of_contact, map)
    my_utils.VecsTest.vecs['wall_tangent'] = 70 * my_utils.get_unit_vector(wall_tangent)
    return get_normal_from_tangent(wall_tangent)


def get_normal_from_tangent(tangent_vector: np.ndarray):
    """
    Get the normal vector from the tangent vector.

    Args:
        tangent_vector (np.ndarray): The tangent vector.

    Returns:
        np.ndarray: The normal unit vector.
    """
    return my_utils.get_unit_vector(my_utils.rotate_vector(tangent_vector, np.pi / 2))


def get_rebound_direction(point_of_contact: np.ndarray, movement_direction: np.ndarray, map: Map, to_unit=False) -> np.ndarray:
    """
    Calculate the rebound direction based on the movement direction and wall normal.

    Args:
        point_of_contact (np.ndarray): The point of contact with the wall.
        movement_direction (np.ndarray): The movement direction vector.
        map (Map): The map object containing wall information.
        to_unit (bool, optional): Whether to return a unit vector. Defaults to False.

    Returns:
        np.ndarray: The rebound direction vector.
    """
    wall_normal = get_wall_normal(point_of_contact, map)
    my_utils.VecsTest.vecs['wall_normal'] = 70 * wall_normal
    return my_utils.mirror_vector(movement_direction, wall_normal)


def get_turn_rebound_direction(point_of_contact: np.ndarray, center_of_mass: np.ndarray, map: Map):
    """
    Determine the direction of the car's turn upon rebound from the wall.

    Args:
        point_of_contact (np.ndarray): The point of contact with the wall.
        center_of_mass (np.ndarray): The center of mass of the car.
        map (Map): The map object containing wall information.

    Returns:
        int: -1 if clockwise, 1 if counterclockwise.
    """
    wall_normal = get_wall_normal(point_of_contact, map)
    contact_to_center_vec = center_of_mass - point_of_contact
    return -1 if my_utils.get_angle_between_vectors(wall_normal, contact_to_center_vec) > 90 else 1


def handle_map_collision(car: car_sprite.Car, point_of_contact: np.ndarray, map: Map):
    """
    Handle the collision between the car and the map.

    Args:
        car (car_sprite.Car): The car object.
        point_of_contact (np.ndarray): The point of contact with the wall.
        map (Map): The map object containing wall information.
    """
    dampening_factor = 0.1
    rebound_vel = get_rebound_direction(point_of_contact, car.velocity, map, True)
    rebound_vel *= dampening_factor
    my_utils.VecsTest.vecs['rebound_dir'] = 70 * my_utils.get_unit_vector(rebound_vel)
    car.longitudinal_speed.reset()
    car.rebound_velocity.start(rebound_vel)
    car.rebound_angular_vel.count = (get_turn_rebound_direction(point_of_contact, car.abs_location, map)
                                     * abs(car.rotation_speed) * 1.2)
    car.delta_location += 20 * my_utils.get_unit_vector(my_utils.get_unit_vector(rebound_vel))


def handle_cars_collision(car1: car_sprite.Car, car2: car_sprite.Car):
    """
    Handle the collision between two cars.

    Args:
        car1 (car_sprite.Car): The first car object.
        car2 (car_sprite.Car): The second car object.
    """
    dampening_factor = 0.3
    combined_rebound_strength_divided = (np.linalg.norm(car1.velocity) + np.linalg.norm(car2.velocity)) / 2 * dampening_factor
    combined_direction = (car1.velocity + car2.velocity) / 4
    if np.linalg.norm(car1.velocity) == 0:
        car1_dir = my_utils.get_unit_vector(car2.velocity)
        car2_dir = my_utils.get_unit_vector(-car2.velocity)
    elif np.linalg.norm(car2.velocity) == 0:
        car1_dir = my_utils.get_unit_vector(-car1.velocity)
        car2_dir = my_utils.get_unit_vector(car1.velocity)
    else:
        car1_dir = my_utils.get_unit_vector(-car1.velocity)
        car2_dir = my_utils.get_unit_vector(-car2.velocity)
    car1.rebound_velocity.start(car1_dir * combined_rebound_strength_divided + combined_direction)
    car2.rebound_velocity.start(car2_dir * combined_rebound_strength_divided + combined_direction)
    car1.delta_location += car1_dir * 30
    car2.delta_location += car2_dir * 30
