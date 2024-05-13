import os
from typing import List

import numpy as np
import pygame

import car_sprite
import my_utils
from config_loaded import ConfigData
from my_errors import StuckInWallError


class Map(pygame.sprite.Sprite):

    def __init__(self, init_map_offset=np.array([0, 0])):
        pygame.sprite.Sprite.__init__(self)
        textures_dir_path = "./textures/pwr_map/map_textures"
        self.SCALE = 2
        self.IMG_HEIGHT, self.IMG_WIDTH = 1080 * self.SCALE, 1920 * self.SCALE

        self.images = self._load_images(textures_dir_path)
        self.images = [pygame.transform.scale(self.images[i], (self.IMG_WIDTH, self.IMG_HEIGHT)) for i in
                       range(len(self.images))]

        self.image_masks = self._load_images("./textures/pwr_map/map_collision_masks")
        self.image_masks = [pygame.transform.scale(self.image_masks[i], (self.IMG_WIDTH, self.IMG_HEIGHT)) for i in
                            range(len(self.image_masks))]
        # self.image_masks = [pygame.mask.from_surface(img) for img in self.image_masks]

        self.images_location = self._get_locations(textures_dir_path, init_map_offset)

        self.main_img_ind = 0

    @property
    def main_image(self):
        return self.images[self.main_img_ind]

    @property
    def prev_to_main_img(self):
        return self.images[self.prev_img_ind(self.main_img_ind)]

    @property
    def next_to_main_img(self):
        return self.images[self.next_img_ind(self.main_img_ind)]

    @property
    def main_img_location(self):
        return self.images_location[self.main_img_ind]

    @property
    def prev_to_main_img_location(self):
        return self.images_location[self.prev_img_ind(self.main_img_ind)]

    @property
    def next_to_main_img_location(self):
        return self.images_location[self.next_img_ind(self.main_img_ind)]

    @property
    def main_img_mask(self):
        return self.image_masks[self.main_img_ind]

    @property
    def prev_to_main_img_mask(self):
        return self.image_masks[self.prev_img_ind(self.main_img_ind)]

    @property
    def next_to_main_img_mask(self):
        return self.image_masks[self.next_img_ind(self.main_img_ind)]

    def _get_locations(self, textures_dir_path, init_map_offset: np.ndarray):
        name_list = os.listdir(textures_dir_path)
        name_list = sorted(name_list, key=lambda name: int(name.split("_")[0]))
        image_locations = [np.array([0, 0]) + init_map_offset]
        for i, name in enumerate(name_list[1:], start=1):
            image_locations.append(image_locations[i - 1] + np.array(self._get_offset_from_name(name)))
        # print(self.images_location)
        return image_locations

    def _load_images(self, dir_path):
        name_list = os.listdir(dir_path)
        name_list = sorted(name_list, key=lambda name: int(name.split("_")[0]))
        images_list = []
        for name in name_list:
            images_list.append(
                pygame.image.load(os.path.join(dir_path, name)).convert_alpha()
            )
        return images_list

    def _get_offset_from_name(self, name):
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
        """
        Draw the sprite
        :param screen:
        :param offset: is the position of the player on the screen
        :return:
        """
        # screen.blit(self.main_image, self.main_img_location - offset)
        # screen.blit(self.prev_to_main_img, self.prev_to_main_img_location - offset)
        # screen.blit(self.next_to_main_img, self.next_to_main_img_location - offset)
        #
        #   FIXME REMOVE
        screen.blit(self.main_img_mask, self.main_img_location - offset)
        screen.blit(self.prev_to_main_img_mask, self.prev_to_main_img_location - offset)
        screen.blit(self.next_to_main_img_mask, self.next_to_main_img_location - offset)

    def update(self, offset):
        self.update_main_image(offset)

    def update_main_image(self, offset):
        """
        Updates the index of the main image
        :param offset: is the player position
        :return:
        """
        if not self.is_point_in_rect(offset, self.images_location[self.main_img_ind]):
            if self.is_point_in_rect(offset, self.images_location[self.next_img_ind(self.main_img_ind)]):
                print("next")
                self.main_img_ind = self.next_img_ind(self.main_img_ind)
            elif self.is_point_in_rect(offset, self.images_location[self.prev_img_ind(self.main_img_ind)]):
                self.main_img_ind = self.prev_img_ind(self.main_img_ind)
                print("prev")

            else:
                print(self.main_img_ind)

    def is_point_in_rect(self, point, rectangle_top_left):
        x, y = point
        x1, y1 = rectangle_top_left
        x2, y2 = rectangle_top_left + np.array([self.IMG_WIDTH, self.IMG_HEIGHT])
        # Check if the point is outside the rectangle
        if x < x1 or x > x2 or y < y1 or y > y2:
            return False
        else:
            return True

    def collisions(self, cars_list: List[car_sprite.Car]):
        from my_engine import handle_map_collision
        for car in cars_list:
            car_wheels = car.get_all_wheels_abs_positions(as_arrays=True)
            car_collided = False
            for i, wheel in enumerate(car_wheels):
                # print(car_wheels[i].astype(int))
                try:
                    if self.get_pixel_from_mask_map(car_wheels[i]) == ConfigData.get_attr('mask_color'):
                        car_collided = True
                        try:
                            handle_map_collision(car, car_wheels[i].astype(int), self)
                        except StuckInWallError:
                            car.handle_errors()

                except IndexError:
                    print("Tried collision outside the tile")
                    continue
                #   Logic for handling errors like getting stuck in the wall
                if car_collided:
                    car.ticks_in_wall.increment()
                    print("!!!", car.ticks_in_wall.count)
                else:
                    car.ticks_in_wall.reset()

    def next_img_ind(self, index):
        return index + 1 if index != len(self.images) - 1 else 0

    def prev_img_ind(self, index):
        return index - 1 if index != 0 else len(self.images) - 1

    def get_pixel_from_mask_map(self, point: np.ndarray):
        #   try except instead of ifs for faster execution
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
