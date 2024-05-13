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
        self.background = map_sprite.Map(players=[self.player])
        self.surface = screen.subsurface(2, 2, WIDTH - 2, HEIGHT - 2)

    def run(self):
        # self.handle_background()
        screen.fill((0, 0, 0))
        self.background.track_boundries_collisions([self.player])
        self.background.switch_context(self.player.delta_location + self.player.init_location)
        self.background.draw(self.surface, self.player.delta_location)
        self.player.draw(screen)
        self.player.move()
        #   FIXME REMOVE
        #
        my_utils.VecsTest.blit_vec()
        #
        self.player.print_status(screen)


class SplitScreenGame:
    def __init__(self, respawn_center, respawn_tilt, num_of_players):
        self.players = []
        if num_of_players == 2:
            self.players = [car_sprite.Car(WIDTH / 4, HEIGHT / 2, "./textures/silver_car.png", respawn_center+(500,0), respawn_tilt)]
            self.players.append(car_sprite.Car(WIDTH / 4, HEIGHT / 2, "./textures/silver_car.png",
                                               respawn_center+np.array([400, -100]), respawn_tilt,
                                               keys={'forward': pygame.K_UP, 'left': pygame.K_LEFT, 'right': pygame.K_RIGHT, 'backward': pygame.K_DOWN}))
        self.map = map_sprite.Map(players=self.players)

        self.player2subscreen = {
            self.players[0]: screen.subsurface(0, 0, WIDTH//2, HEIGHT),
            self.players[1]: screen.subsurface(WIDTH//2, 0, WIDTH//2, HEIGHT)
                                 }



    def run(self):
        screen.fill((0, 0, 0))
        self.map.cars_collisions()
        for player in self.players:
            self.map.switch_context(player.abs_location)
            self.map.track_boundries_collisions(player)
            self.map.draw(self.player2subscreen[player], player.delta_location)
            # self.player.draw(screen)
            player.move()



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
            game = SplitScreenGame(np.array([1800., 900.]), 1.1, ConfigData.get_attr('num_of_players'))

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