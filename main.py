import pygame
from sys import exit
import car_sprite
import math

class Game:
    def __init__(self):
        player_sprite = car_sprite.Car(WIDTH / 2, HEIGHT / 2, "./textures/silver_car.png", 1500, )
        self.player = player_sprite
        background = pygame.image.load("./textures/backg2.png").convert()
        background = pygame.transform.scale(background, (background.get_width() * 3, background.get_height() * 3))
        self.background = background
    def run(self):
        self.handle_background()
        self.player.draw(screen)
        self.player.move()
        if clock.get_time() % 2 == 0:
            self.player.print_status()
        draw_a_line(self.player)
    def handle_background(self):

        background_rect = self.background.get_rect(topleft=-self.player.location)
        screen.blit(self.background, background_rect)

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


if __name__ == '__main__':
    WIDTH, HEIGHT = 1400, 800
    FRAME_RATE = 30
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("PWR CARS 2")
    clock = pygame.time.Clock()
    game = Game()


    ang= 0
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
        game.run()

        pygame.display.update()
        clock.tick(FRAME_RATE)


