import os
from typing import List
import numpy as np
import pygame
import car_sprite
import globals
from my_utils import is_point_in_img_rect
from config_loaded import ConfigData
from my_errors import StuckInWallError


class Map(pygame.sprite.Sprite):
    def __init__(self, players: List[car_sprite.Car], init_map_offset=np.array([0, 0]), show_perks=True):
        """Initialize a Map instance.

        Args:
            players (List[car_sprite.Car]): List of player car sprites.
            init_map_offset (np.ndarray, optional): Initial map offset. Defaults to np.array([0, 0]).
            show_perks (bool, optional): Flag to show perks. Defaults to True.
        """
        pygame.sprite.Sprite.__init__(self)
        textures_dir_path = "./textures/pwr_map/map_textures"
        self.players = players
        self.SCALE = 2
        self.IMG_HEIGHT, self.IMG_WIDTH = 1080 * self.SCALE, 1920 * self.SCALE
        self.images = self._load_images(textures_dir_path)
        self.images = [pygame.transform.scale(self.images[i], (self.IMG_WIDTH, self.IMG_HEIGHT)) for i in
                       range(len(self.images))]

        self.image_masks = self._load_images("./textures/pwr_map/map_collision_masks")
        self.image_masks = [pygame.transform.scale(self.image_masks[i], (self.IMG_WIDTH, self.IMG_HEIGHT)) for i in
                            range(len(self.image_masks))]

        self.images_location = self._get_locations(textures_dir_path, init_map_offset)
        self.main_img_ind = 0

        import perks_sprites
        if show_perks:
            self.perks = [perks_sprites.MinePerk(loc) for loc in globals.ON_MAP_POINTS]
        else:
            self.perks = []

    @property
    def main_image(self):
        """Get the main image of the map.

        Returns:
            pygame.Surface: The main image surface.
        """
        return self.images[self.main_img_ind]

    @property
    def prev_to_main_img(self):
        """Get the previous image relative to the main image.

        Returns:
            pygame.Surface: The previous image surface.
        """
        return self.images[self.prev_img_ind(self.main_img_ind)]

    @property
    def next_to_main_img(self):
        """Get the next image relative to the main image.

        Returns:
            pygame.Surface: The next image surface.
        """
        return self.images[self.next_img_ind(self.main_img_ind)]

    @property
    def main_img_location(self):
        """Get the location of the main image.

        Returns:
            np.ndarray: The location coordinates of the main image.
        """
        return self.images_location[self.main_img_ind]

    @property
    def prev_to_main_img_location(self):
        """Get the location of the previous image relative to the main image.

        Returns:
            np.ndarray: The location coordinates of the previous image.
        """
        return self.images_location[self.prev_img_ind(self.main_img_ind)]

    @property
    def next_to_main_img_location(self):
        """Get the location of the next image relative to the main image.

        Returns:
            np.ndarray: The location coordinates of the next image.
        """
        return self.images_location[self.next_img_ind(self.main_img_ind)]

    @property
    def main_img_mask(self):
        """Get the collision mask of the main image.

        Returns:
            pygame.Surface: The main image collision mask.
        """
        return self.image_masks[self.main_img_ind]

    @property
    def prev_to_main_img_mask(self):
        """Get the collision mask of the previous image relative to the main image.

        Returns:
            pygame.Surface: The previous image collision mask.
        """
        return self.image_masks[self.prev_img_ind(self.main_img_ind)]

    @property
    def next_to_main_img_mask(self):
        """Get the collision mask of the next image relative to the main image.

        Returns:
            pygame.Surface: The next image collision mask.
        """
        return self.image_masks[self.next_img_ind(self.main_img_ind)]

    def _get_locations(self, textures_dir_path, init_map_offset: np.ndarray):
        """Get the locations of images based on texture directory path and initial offset.

        Args:
            textures_dir_path (str): Directory path of the textures.
            init_map_offset (np.ndarray): Initial map offset.

        Returns:
            List[np.ndarray]: List of image locations.
        """
        name_list = os.listdir(textures_dir_path)
        name_list = sorted(name_list, key=lambda name: int(name.split("_")[0]))
        image_locations = [np.array([0, 0]) + init_map_offset]
        for i, name in enumerate(name_list[1:], start=1):
            image_locations.append(image_locations[i - 1] + np.array(self._get_offset_from_name(name)))
        return image_locations

    def _load_images(self, dir_path):
        """Load images from a directory.

        Args:
            dir_path (str): Path to the directory containing images.

        Returns:
            List[pygame.Surface]: List of loaded images.
        """
        name_list = os.listdir(dir_path)
        name_list = sorted(name_list, key=lambda name: int(name.split("_")[0]))
        images_list = []
        for name in name_list:
            images_list.append(
                pygame.image.load(os.path.join(dir_path, name)).convert_alpha()
            )
        return images_list

    def _get_offset_from_name(self, name):
        """Get offset from the image name.

        Args:
            name (str): Image name containing offset information.

        Returns:
            Tuple[int, int]: Offset coordinates.
        """
        name_divided = name.split("_")
        name_divided[3] = (name_divided[3])[:-4]

        if name_divided[1] == 'R':
            x = self.IMG_WIDTH
            y = int(name_divided[3]) * self.SCALE
            if name_divided[2] == 'min':
                y = -y
        elif name_divided[1] == 'L':
            x = -self.IMG_WIDTH
            y = int(name_divided[3]) * self.SCALE
            if name_divided[2] == 'min':
                y = -y

        elif name_divided[1] == 'D':
            x = int(name_divided[3]) * self.SCALE
            y = self.IMG_HEIGHT
            if name_divided[2] == 'min':
                x = -x
        elif name_divided[1] == 'U':
            x = int(name_divided[3]) * self.SCALE
            y = -self.IMG_HEIGHT
            if name_divided[2] == 'min':
                x = -x
        else:
            raise ValueError("Invalid texture name in map ")

        return x, y

    def draw(self, screen, offset):
        """Draw the map and its elements on the screen.

        Args:
            screen (pygame.Surface): The screen surface to draw on.
            offset (np.ndarray): The position offset of the player on the screen.
        """
        screen.blit(self.main_image, self.main_img_location - offset)
        screen.blit(self.prev_to_main_img, self.prev_to_main_img_location - offset)
        screen.blit(self.next_to_main_img, self.next_to_main_img_location - offset)

        for player in self.players:
            player.draw(screen, offset)

        for perk in self.perks:
            perk.draw_on_map(screen, offset)

    def switch_context(self, player):
        """Switch the current context of the map to the position of the player.

        Args:
            player (car_sprite.Car): The player whose position to switch to.
        """
        self.update_main_image(player)

    def update_main_image(self, player: car_sprite.Car):
        """Update the index of the main image based on the player's position.

        Args:
            player (car_sprite.Car): The player in question.
        """
        offset = player.abs_location
        if not is_point_in_img_rect((self.IMG_WIDTH, self.IMG_HEIGHT), offset, self.images_location[self.main_img_ind]):
            if is_point_in_img_rect((self.IMG_WIDTH, self.IMG_HEIGHT), offset, self.images_location[self.next_img_ind(self.main_img_ind)]):
                self.main_img_ind = self.next_img_ind(self.main_img_ind)
            elif is_point_in_img_rect((self.IMG_WIDTH, self.IMG_HEIGHT), offset, self.images_location[self.prev_img_ind(self.main_img_ind)]):
                self.main_img_ind = self.prev_img_ind(self.main_img_ind)
            else:
                for i, location in enumerate(self.images_location):
                    if is_point_in_img_rect((self.IMG_WIDTH, self.IMG_HEIGHT), offset, location):
                        self.main_img_ind = i

    def cars_collisions(self):
        """Check and handle collisions between cars."""
        for context_car in self.players:
            for car in self.players:
                if context_car != car:
                    if context_car.rect.colliderect(car.rect):
                        context_car_mask = pygame.mask.from_surface(pygame.transform.rotate(context_car.image, np.degrees(-context_car.rotation)))
                        other_mask = pygame.mask.from_surface(pygame.transform.rotate(car.image, np.degrees(-car.rotation)))
                        if context_car_mask.overlap(other_mask, tuple(context_car.get_vector_to_other(car))):
                            from my_engine import handle_cars_collision
                            handle_cars_collision(context_car, car)

    def check_car_progress_on_map(self, player: car_sprite.Car):
        """Update the player's progress on the map.

        Args:
            player (car_sprite.Car): The player whose progress to check.
        """
        player.add_visited_tile(self.main_img_ind, len(self.images_location))

    def track_boundries_collisions(self, context_car: car_sprite.Car):
        """Check and handle collisions between the car and the map boundaries.

        Args:
            context_car (car_sprite.Car): The car to check for boundary collisions.
        """
        from my_engine import handle_map_collision
        car_wheels = context_car.get_all_wheels_abs_positions(as_arrays=True)
        car_collided = False
        for i, wheel in enumerate(car_wheels):
            try:
                if self.get_pixel_from_mask_map(car_wheels[i]) == ConfigData.get_attr('mask_color'):
                    car_collided = True
                    try:
                        handle_map_collision(context_car, car_wheels[i].astype(int), self)
                    except StuckInWallError:
                        context_car.handle_errors()
                    except (ZeroDivisionError, Exception):
                        context_car.handle_errors()
                        print("Math problems due to unexpected behaviour")

            except IndexError as s:
                print(s.args)
                continue

            if car_collided:
                context_car.ticks_in_wall.increment()
                print("ticks in wall count ", context_car.ticks_in_wall.count)
            else:
                context_car.ticks_in_wall.reset()

    def perks_actions(self):
        """Update and handle actions related to perks on the map."""
        for perks in self.perks:
            perks.update(self)

    def next_img_ind(self, index):
        """Get the index of the next image.

        Args:
            index (int): Current image index.

        Returns:
            int: Next image index.
        """
        return index + 1 if index != len(self.images) - 1 else 0

    def prev_img_ind(self, index):
        """Get the index of the previous image.

        Args:
            index (int): Current image index.

        Returns:
            int: Previous image index.
        """
        return index - 1 if index != 0 else len(self.images) - 1

    def get_pixel_from_mask_map(self, point: np.ndarray):
        """Get the pixel color from the mask map at a given point.

        Args:
            point (np.ndarray): The point coordinates.

        Returns:
            pygame.Color: The color of the pixel at the given point.
        """
        try:
            the_pixel = self.main_img_mask.get_at(point.astype(int) - self.main_img_location)
        except IndexError:
            try:
                the_pixel = self.next_to_main_img_mask.get_at(point.astype(int) - self.next_to_main_img_location)
            except IndexError:
                try:
                    the_pixel = self.prev_to_main_img_mask.get_at(point.astype(int) - self.prev_to_main_img_location)
                except IndexError:
                    raise IndexError("Sampled pixel outside the 3 main tiles")
        return the_pixel
