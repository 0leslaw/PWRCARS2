import pygame
from sys import exit
import car_sprite, map_sprite
import math
import numpy as np

import my_utils
from config_loaded import ConfigData


class SinglePlayerGame:
    def __init__(self, respawn_center, respawn_tilt):
        # FIXME REMOVE THIS AFTER PRODUCTION
        #
        my_utils.VecsTest.screen = screen
        #

        player_sprite = car_sprite.Car(WIDTH / 2, HEIGHT / 2, "./textures/silver_car.png", respawn_center, respawn_tilt)
        self.player = player_sprite
        self.background = map_sprite.Map()

    def run(self):
        # self.handle_background()
        screen.fill((0, 0, 0))
        self.background.collisions([self.player])
        self.background.update(self.player.delta_location + self.player.init_location)
        self.background.draw(screen, self.player.delta_location)
        self.player.draw(screen)
        self.player.move()
        #   FIXME REMOVE
        #
        my_utils.VecsTest.blit_vec()
        #
        self.player.print_status(screen)


class SplitScreenGame:
    def __init__(self, respawn_center, respawn_tilt, num_of_players):
        if num_of_players == 2:
            self.player1 = car_sprite.Car(WIDTH / 4, HEIGHT / 2, "./textures/silver_car.png", respawn_center, respawn_tilt)
            self.player2 = car_sprite.Car(WIDTH * 3 / 4, HEIGHT / 2, "./textures/silver_car.png", respawn_center+np.array([-100, -100]), respawn_tilt)
            self.map = map_sprite.Map()

            self.canvas = pygame.Surface((WIDTH, HEIGHT))
            player1_camera = pygame.Rect(0, 0, WIDTH/2, HEIGHT)
            player2_camera = pygame.Rect(WIDTH/2, 0, WIDTH/2, HEIGHT)

            self.sub1 = self.canvas.subsurface(player1_camera)
            self.sub2 = self.canvas.subsurface(player2_camera)

    def run(self):
        screen.fill((0, 0, 0))
        self.map.collisions([self.player])
        self.map.update(self.player.delta_location + self.player.init_location)
        self.background.draw(screen, self.player.delta_location)
        self.player.draw(screen)
        self.player.move()



if __name__ == '__main__':
    WIDTH, HEIGHT = 1400, 800
    FRAME_RATE = 30
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("PWR CARS 2")
    clock = pygame.time.Clock()
    match ConfigData.get_attr('game_mode'):
        case 'single_player':
            game = SinglePlayerGame(np.array([1800., 900.]), 1.1)
        case 'split_screen':
            game = SplitScreenGame(ConfigData.get_attr('num_of_players'))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
        game.run()

        pygame.display.update()
        clock.tick(FRAME_RATE)


def draw_a_line(car: car_sprite.Car):
    # Calculate the end points of the line

    length = 20
    start_point = (40, 40)
    angle_radians = car.rotation - math.pi/2
    end_point = (start_point[0] + length * math.cos(angle_radians),
                 start_point[1] + length * math.sin(angle_radians))

    # Set the color of the line (RGB)
    line_color = (255, 0, 0)

    # Draw the line
    pygame.draw.line(screen, line_color, start_point, end_point, 2)