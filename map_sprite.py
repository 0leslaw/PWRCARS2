import ast
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
        # self.image_masks = [pygame.mask.from_surface(img) for img in self.image_masks]

        self.images_location = self._get_locations(textures_dir_path, init_map_offset)
        self.main_img_ind = 0

        import perks_sprites
        # self.perks = [perks_sprites.MinePerk(np.array([2900., 1000.]))]
        if show_perks:
            self.perks = [perks_sprites.MinePerk(loc) for loc in globals.ON_MAP_POINTS]
        else:
            self.perks = []

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

        screen.blit(self.main_image, self.main_img_location - offset)
        screen.blit(self.prev_to_main_img, self.prev_to_main_img_location - offset)
        screen.blit(self.next_to_main_img, self.next_to_main_img_location - offset)
        #
        #   FIXME REMOVE
        # screen.blit(self.main_img_mask, self.main_img_location - offset)
        # screen.blit(self.prev_to_main_img_mask, self.prev_to_main_img_location - offset)
        # screen.blit(self.next_to_main_img_mask, self.next_to_main_img_location - offset)
        #   FIXME actually also blits the main player
        for player in self.players:
            player.draw(screen, offset)
        # context_car_mask = pygame.mask.from_surface(
        #     pygame.transform.rotate(self.players[0].image, np.degrees(-self.players[0].rotation)))
        # screen.blit(context_car_mask.to_surface(), self.players[0].init_location)
        # other_mask = pygame.mask.from_surface(pygame.transform.rotate(self.players[1].image, np.degrees(-self.players[1].rotation)))
        # screen.blit(other_mask.to_surface(), self.players[1].init_location + tuple(self.players[0].get_vector_to_other(self.players[1])))
        # pygame.draw.rect(screen,(255,255,0), self.players[0].rect)
        # pygame.draw.rect(screen, (255,25,0), self.players[1].rect)
        for perk in self.perks:
            perk.draw_on_map(screen, offset)

    def switch_context(self, player):
        """switches the current context to the map to pos of the player"""
        self.update_main_image(player)

    def update_main_image(self, player: car_sprite.Car):
        """
        Updates the index of the main image
        :param player: is the player in question
        :return: if was updated
        """
        offset = player.abs_location
        if not is_point_in_img_rect((self.IMG_WIDTH, self.IMG_HEIGHT), offset, self.images_location[self.main_img_ind]):
            # went into the next one
            if is_point_in_img_rect((self.IMG_WIDTH, self.IMG_HEIGHT), offset, self.images_location[self.next_img_ind(self.main_img_ind)]):
                self.main_img_ind = self.next_img_ind(self.main_img_ind)
            # went into the prev one
            elif is_point_in_img_rect((self.IMG_WIDTH, self.IMG_HEIGHT), offset, self.images_location[self.prev_img_ind(self.main_img_ind)]):
                self.main_img_ind = self.prev_img_ind(self.main_img_ind)

            else:
                for i, location in enumerate(self.images_location):
                    if is_point_in_img_rect((self.IMG_WIDTH, self.IMG_HEIGHT), offset, location):
                        self.main_img_ind = i

    def cars_collisions(self):
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
        player.add_visited_tile(self.main_img_ind, len(self.images_location))

    def track_boundries_collisions(self, context_car: car_sprite.Car):
        """this depends on the context, since for every car there are different boundries"""
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
                    except (RuntimeWarning, Exception):
                        context_car.handle_errors()
                        print("Math problems due to unexpected behaviour")

            except IndexError as s:
                print(s.args)
                continue
            #   Logic for handling errors like getting stuck in the wall
            if car_collided:
                context_car.ticks_in_wall.increment()
                print("ticks in wall count ", context_car.ticks_in_wall.count)
            else:
                context_car.ticks_in_wall.reset()

    def perks_actions(self):
        for perks in self.perks:
            perks.update(self)

    def next_img_ind(self, index):
        return index + 1 if index != len(self.images) - 1 else 0

    def prev_img_ind(self, index):
        return index - 1 if index != 0 else len(self.images) - 1

    def get_pixel_from_mask_map(self, point: np.ndarray):
        #   try except instead of ifs for faster execution assuming it will break rarely
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
