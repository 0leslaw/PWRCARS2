from collections import deque
import pygame
import numpy as np
import globals
import my_utils
from counter import *


class Car(pygame.sprite.Sprite):
    def __init__(self, x_pos_on_screen, y_pos_on_screen, image_path, initial_position=np.array([0., 0.]), initial_rotation=0, keys=None):
        """
        Initialize a Car instance.

        Args:
            x_pos_on_screen (int): The x position on the screen.
            y_pos_on_screen (int): The y position on the screen.
            image_path (str): Path to the car image.
            initial_position (np.ndarray, optional): Initial position of the car. Defaults to np.array([0., 0.]).
            initial_rotation (int, optional): Initial rotation of the car. Defaults to 0.
            keys (dict, optional): Dictionary of keys for car controls. Defaults to None.
        """
        pygame.sprite.Sprite.__init__(self)
        if keys is None:
            keys = {'forward': pygame.K_w, 'left': pygame.K_a, 'backward': pygame.K_s, 'right': pygame.K_d, 'release': pygame.K_q}
        self.keys = keys
        self.image = pygame.image.load(image_path).convert_alpha()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect(center=(x_pos_on_screen, y_pos_on_screen))
        self.path: deque = my_utils.reset_queue_to_length(initial_position, 20)
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
        import perks_sprites
        self.perks = perks_sprites.PerkSet()
        self.visited_tiles_indices = [0]
        self.time_of_laps_completion = []

    @property
    def abs_location(self):
        """
        Get the absolute location of the car, considering a player-central perspective.

        Returns:
            np.ndarray: The absolute location of the car.
        """
        return self.init_location + self.delta_location

    def add_visited_tile(self, tile_ind, tile_count):
        """
        Add a tile index to the list of visited tiles and handle lap completion.

        Args:
            tile_ind (int): The index of the tile.
            tile_count (int): The total number of tiles.
        """
        if tile_ind not in self.visited_tiles_indices:
            self.visited_tiles_indices.append(tile_ind)
            print(self.visited_tiles_indices)
            if len(self.visited_tiles_indices) == tile_count:
                self.visited_tiles_indices = []
                self.time_of_laps_completion.append(globals.TICKS_PASSED * globals.FRAME_RATE)
                print("next lap")

    def handle_perk_control(self):
        """
        Handle the control of perks by the player.
        """
        key = pygame.key.get_pressed()
        if key[self.keys['release']]:
            self.perks.use_perk()

    def handle_steering(self):
        """
        Handle the steering controls of the car.
        """
        key = pygame.key.get_pressed()

        self.longitudinal_speed.state = "S"
        self.steerwheel_turn_extent.state = "S"

        # Handle forward and backward movement
        if key[self.keys['forward']] is True:
            self.longitudinal_speed.state = "R"
        elif key[self.keys['backward']] is True:
            self.longitudinal_speed.state = "L"
        else:
            self.longitudinal_speed.state = "S"

        # Handle left and right movement
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
        """
        Move the car based on the current steering and speed.
        """
        self.handle_steering()
        from my_engine import calculate_car_speeds
        calculate_car_speeds(self)
        self.update_path()
        self.handle_perk_control()

    def update_path(self):
        """
        Update the list of past locations of the car.
        """
        if globals.TICKS_PASSED % 10 == 0:
            self.path.popleft()
            self.path.append(self.delta_location.copy())
            if self.ticks_in_wall.count == self.ticks_in_wall.max_turn:
                self.handle_errors()

    def handle_errors(self):
        """
        Handle errors when the car gets stuck or encounters an issue.
        """
        self.ticks_in_wall.reset()
        self.delta_location = self.path[0].copy()
        print("THERE HAS BEEN AN ERROR, THE PLAYER HAS BEEN RETURNED TO PREV LOC")
        self.path = my_utils.reset_queue_to_length(self.path[0].copy(), len(self.path))
        self.reset_dynamics()

    def reset_dynamics(self):
        """
        Reset the dynamics of the car (velocity, rotation, etc.).
        """
        self.velocity[0] = 0
        self.velocity[1] = 0
        self.rotation_speed = 0
        self.longitudinal_speed.reset()
        self.rebound_velocity.reset()
        print(self.delta_location)

    def print_status(self, screen):
        """
        Print the current status of the car on the screen.

        Args:
            screen (pygame.Surface): The screen surface to print on.
        """
        font = pygame.font.SysFont('Courier New', 36)
        message = (f'location:{np.round(self.delta_location[0], 2):<10}, {np.round(self.delta_location[1], 2):<10}'
                   f' speed:{np.round(self.longitudinal_speed.count, 2)}')
        # Render the text onto a surface
        text_surface = font.render(message, 0,
                                   (255, 255, 255))  # True enables anti-aliasing, (255, 255, 255) is white color
        screen.blit(text_surface, (10, 10))

    def draw(self, screen, context_player_delta_loc=None):
        """
        Draw the car on the screen.

        Args:
            screen (pygame.Surface): The screen surface to draw on.
            context_player_delta_loc (np.ndarray, optional): The delta location of the context player. Defaults to None.
        """
        rot_in_degrees = np.degrees(-self.rotation)
        rotated_img = pygame.transform.rotate(self.image, rot_in_degrees)
        if context_player_delta_loc is not None:
            rec = rotated_img.get_rect(center=self.abs_location - context_player_delta_loc)
        else:
            rec = rotated_img.get_rect(center=self.rect.center)
        self.rect = rec
        screen.blit(rotated_img, rec)
        # self.draw_wheel_trail(screen)
        # FIXME REMOVE
        my_utils.VecsTest.vecs['velocity'] = self.velocity

    def get_vector_to_other(self, other):
        """
        Get the vector from this car to another car.

        Args:
            other (Car): The other car.

        Returns:
            np.ndarray: The vector to the other car.
        """
        return other.delta_location - self.delta_location

    def draw_wheel_trail(self, screen):
        """
        Draw the wheel trail of the car on the screen.
        """
        # TODO
        left_wheel_pos, right_wheel_pos = self.get_wheels_rel_to_mid(is_back_wheels=True)
        pygame.draw.circle(screen, center=left_wheel_pos, color=(0, 0, 0), radius=2)
        pass

    def get_wheel_pos_rel_to_car(self, is_back_wheels=True):
        """
        Get the position of the wheels relative to the car.

        Args:
            is_back_wheels (bool, optional): Whether to get the back wheels. Defaults to True.

        Returns:
            tuple: The positions of the left and right wheels.
        """
        real_distance_scaler = 0.85
        h = self.image.get_height() / 2 * real_distance_scaler
        a = self.image.get_width() / 2 * real_distance_scaler
        if not is_back_wheels:
            h = -h
        left_wheel_pos = (a, h)
        right_wheel_pos = (-a, h)
        return left_wheel_pos, right_wheel_pos

    def get_wheels_rel_to_mid(self, is_back_wheels=True, as_arrays=False):
        """
        Get the wheel positions relative to the car's midpoint.

        Args:
            is_back_wheels (bool, optional): Whether to get the back wheels. Defaults to True.
            as_arrays (bool, optional): Whether to return the positions as arrays. Defaults to False.

        Returns:
            tuple: The positions of the left and right wheels.
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
        """
        Get the positions of all wheels relative to the car's midpoint.

        Args:
            as_arrays (bool, optional): Whether to return the positions as arrays. Defaults to True.

        Returns:
            tuple: The positions of all wheels.
        """
        return *self.get_wheels_rel_to_mid(as_arrays=as_arrays), *self.get_wheels_rel_to_mid(is_back_wheels=False, as_arrays=as_arrays)

    def get_all_wheels_abs_positions(self, as_arrays=True):
        """
        Get the absolute positions of all wheels.

        Args:
            as_arrays (bool, optional): Whether to return the positions as arrays. Defaults to True.

        Returns:
            tuple: The absolute positions of all wheels.
        """
        left_back, right_back = self.get_wheels_rel_to_mid(as_arrays=True)
        left_front, right_front = self.get_wheels_rel_to_mid(is_back_wheels=False, as_arrays=True)
        if as_arrays:
            return (left_back + self.delta_location, right_back + self.delta_location,
                    left_front + self.delta_location, right_front + self.delta_location)
        else:
            return (tuple(left_back + self.delta_location), tuple(right_back + self.delta_location),
                    tuple(left_front + self.delta_location), tuple(right_front + self.delta_location))
