import pygame
from sys import exit
import car_sprite, map_sprite
import math
import numpy as np

import globals
import my_utils
from config_loaded import ConfigData

WIDTH, HEIGHT = 1400, 800
FRAME_RATE = 30


class SinglePlayerGame:
    def __init__(self, respawn_center, respawn_tilt, screen):
        self.screen = screen

        # FIXME REMOVE THIS AFTER PRODUCTION
        #
        my_utils.VecsTest.screen = screen
        #

        player_sprite = car_sprite.Car(WIDTH / 2, HEIGHT / 2, ConfigData.get_attr('player1')['car_texture'], respawn_center, respawn_tilt)
        self.player = player_sprite
        self.background = map_sprite.Map(players=[self.player])
        self.surface = screen.subsurface(2, 2, WIDTH - 2, HEIGHT - 2)

    def run(self):
        # self.handle_background()
        self.screen.fill((0, 0, 0))
        self.background.track_boundries_collisions(self.player)
        self.background.switch_context(self.player.delta_location + self.player.init_location)
        self.background.draw(self.surface, self.player.delta_location)
        self.player.draw(self.screen)
        self.player.move()
        #   FIXME REMOVE
        #
        my_utils.VecsTest.blit_vec()
        #
        self.player.print_status(self.screen)



class SplitScreenGame:
    def __init__(self, respawn_center, respawn_tilt, num_of_players, screen):
        self.screen = screen
        self.players = []
        if num_of_players == 2:
            self.players = [car_sprite.Car(WIDTH / 4, HEIGHT / 2,
                                           ConfigData.get_attr('player1')['car_texture'], respawn_center+(500,0), respawn_tilt)]
            self.players.append(car_sprite.Car(WIDTH / 4, HEIGHT / 2, ConfigData.get_attr('player2')['car_texture'],
                                               respawn_center+np.array([400, -100]), respawn_tilt,
                                               keys=ConfigData.get_attr('player2')['keys']))
        self.map = map_sprite.Map(players=self.players)

        self.player2subscreen = {
            self.players[0]: screen.subsurface(0, 0, WIDTH//2, HEIGHT),
            self.players[1]: screen.subsurface(WIDTH//2, 0, WIDTH//2, HEIGHT)
            }



    def run(self):
        self.screen.fill((0, 0, 0))

        for player in self.players:
            self.map.switch_context(player.abs_location)
            self.map.track_boundries_collisions(player)
            self.map.draw(self.player2subscreen[player], player.delta_location)
            # self.player.draw(screen)
            player.move()
        self.map.cars_collisions()
        self.map.perks_actions()


def start_game():
    pygame.init()
    pygame.display.set_caption("PWR CARS 2")
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    match ConfigData.get_attr('game_mode'):
        case 'Single Player':
            game = SinglePlayerGame(np.array([1800., 900.]), 1.1, screen)
        case 'Two Player':
            game = SplitScreenGame(np.array([1800., 900.]), 1.1, ConfigData.get_attr('num_of_players'), screen)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
        game.run()

        pygame.display.update()
        clock.tick(FRAME_RATE)
        globals.TICKS_PASSED += 1


def draw_a_line(car: car_sprite.Car, screen):
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


if __name__ == '__main__':
    start_game()