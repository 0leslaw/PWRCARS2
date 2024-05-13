from collections import deque
from typing import List, Any
import configparser
import numpy as np
import pygame
from config_loaded import ConfigData


def same_sign(num1, num2):
    # Przesunięcie bitowe o 31 bity w lewo - dostaniemy 1 dla liczby ujemnej i 0 dla liczby nieujemnej
    # sign1 = (num1 >> 31) & 1
    # sign2 = (num2 >> 31) & 1
    sign1 = np.sign(num1)
    sign2 = np.sign(num2)
    # Porównanie bitów znaku
    return sign1 == sign2


# Define a function to rotate a vector
def rotate_vector(vector, angle_radians):
    # Define the rotation matrix
    rotation_matrix = np.array([[np.cos(angle_radians), -np.sin(angle_radians)],
                                [np.sin(angle_radians), np.cos(angle_radians)]])

    # Rotate the vector
    rotated_vector = np.dot(rotation_matrix, vector)

    return rotated_vector


def point_collides(mask, point):
    #   if alpha is non zero there is a collision
    print(mask.get_at(point))

    return mask.get_at(point) != 1


def get_unit_vector(vec: np.ndarray):
    return vec / np.linalg.norm(vec)


def mirror_vector(vector: np.ndarray, normal: np.ndarray, not_normal=False):
    """Returns the mirrored vector across the plane defined by the normal vector."""
    if not_normal:
        normal = normal / np.linalg.norm(normal)  # Ensure normal vector is unit length
    # return vector - 2 * np.outer(np.dot(vector, normal), normal).squeeze()
    n1, n2 = normal[0], normal[1]
    mirror_matrix = np.array([[1 - 2 * n1 ** 2, -2 * n1 * n2],
                              [-2 * n1 * n2, 1 - 2 * n2 ** 2]])
    return np.dot(mirror_matrix, vector)


def get_angle_between_vectors(vector_1, vector_2):
    unit_vector_1 = vector_1 / np.linalg.norm(vector_1)
    unit_vector_2 = vector_2 / np.linalg.norm(vector_2)
    dot_product = np.dot(unit_vector_1, unit_vector_2)
    return np.arccos(dot_product)


def lin_to_exponential(x, coef=3., degree=3., max_amplitude=1.3) -> float:
    return np.clip(coef * x ** degree, -max_amplitude, max_amplitude)


def lin_to_regulated(fun, *args):
    def regulated(x):
        return fun(x, *args)

    return regulated


def reset_queue_to_length(point: np.ndarray, length: int) -> deque:
    return deque([point.copy() for _ in range(length)])

# FIXME
class VecsTest:
    screen = None
    vecs: dict[str, np.ndarray] = {}
    vecs_origin = np.array([200, 100])
    colors = list(ConfigData.get_attr('colors').values())

    def __init__(self):
        pass

    @staticmethod
    def blit_vec():
        font_size = 30
        font = pygame.font.Font(None, font_size)  # None means default system font, 36 is the font size
        pygame.draw.rect(VecsTest.screen, (0, 0, 0, 255), pygame.Rect(0, 0, 300, font_size * len(VecsTest.vecs)))
        for i, (name, vec) in enumerate(VecsTest.vecs.items()):
            curr_color = VecsTest.colors[i]
            #   blit the name
            text_surface = font.render(name, 0,
                                       curr_color)
            VecsTest.screen.blit(text_surface, (i, i * font_size))
            # blit the vector
            pygame.draw.line(VecsTest.screen, curr_color, VecsTest.vecs_origin, VecsTest.vecs_origin + vec, 2)
