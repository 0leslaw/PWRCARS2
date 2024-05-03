import os

import pygame


class Map(pygame.sprite.Sprite):

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        textures_dir_path = "./textures/pwr_map/map_textures"
        self.images = []
        self.IMG_HEIGHT, self.IMG_WIDTH = 1080, 1920
        name_list = os.listdir()
        name_list = sorted(name_list, key=lambda name: int(name.split("_")[0]))

        for name in name_list:
            self.images.append(
                pygame.image.load(os.path.join(textures_dir_path, name)).convert_alpha()
            )

        self.images_location = [(0, 0)]
        for i, name in enumerate(name_list, start=1):
            self.images_location.append(self.images_location[i - 1] + self.get_offset_from_name(name))

        self.main_image_index = 0
        # self.main_image = self.images[self.main_image_index]
        # self.prev_image = self.images[len(self.images)-1]
        # self.next_image = self.images[1]

    def get_offset_from_name(self, name):
        name_divided = name.split("_")
        name_divided[3] = (name_divided[3])[:-4]

        if name_divided[1] == 'R':
            x = self.IMG_WIDTH
            y = int(name_divided[3])
            if name_divided[2] == 'min':
                y = -y
        elif name_divided[1] == 'L':
            x = -self.IMG_WIDTH
            y = int(name_divided[3])
            if name_divided[2] == 'min':
                y = -y

        elif name_divided[1] == 'D':
            x = int(name_divided[3])
            y = self.IMG_HEIGHT
            if name_divided[2] == 'min':
                x = -x
        elif name_divided[1] == 'U':
            x = int(name_divided[3])
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
        i_main, i_prev, i_next = self.main_image_index, self.prev_img_ind(self.main_image_index), self.next_img_ind(self.main_image_index)
        screen.blit(self.images[i_main], self.images_location[i_main] - offset)
        screen.blit(self.images[i_prev], self.images_location[i_prev] - offset)
        screen.blit(self.images[i_next], self.images_location[i_next] - offset)

    def update(self, offset):
        self.update_main_image(offset)

    def update_main_image(self, offset):
        """
        Updates the index of the main image
        :param offset: is the player position
        :return:
        """
        if not self.is_point_outside_rectangle(offset, self.images_location[self.main_image_index]):
            if self.is_point_outside_rectangle(offset, self.images_location[self.next_img_ind(self.main_image_index)]):
                self.main_image_index = self.next_img_ind(self.main_image_index)
            elif self.is_point_outside_rectangle(offset, self.images_location[self.prev_img_ind(self.main_image_index)]):
                self.main_image_index = self.prev_img_ind(self.main_image_index)

    def is_point_outside_rectangle(self, point, rectangle_top_left):
        x, y = point
        x1, y1 = rectangle_top_left
        x2, y2 = rectangle_top_left + (self.IMG_WIDTH, self.IMG_HEIGHT)
        # Check if the point is outside the rectangle
        if x < x1 or x > x2 or y < y1 or y > y2:
            return True
        else:
            return False

    def next_img_ind(self, index):
        return index + 1 if index != len(self.images_location) - 1 else 0

    def prev_img_ind(self, index):
        return index - 1 if index != 0 else len(self.images) - 1