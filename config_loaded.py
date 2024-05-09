from dataclasses import dataclass
from typing import Tuple
import configparser

def mask_color():

    config = configparser.ConfigParser()
    config.read('config.ini')
    return tuple(map(int, config['special_colors']['mask_color'].split(', ')))


def load_config_to_name2int_tuple_dict(config_branch: str) -> dict[str, tuple[int, ...]]:
    config = configparser.ConfigParser()
    config.read('config.ini')
    name_tuple = config[config_branch]
    name2int_tuple = {}
    for name, value in name_tuple.items():
        name2int_tuple[name] = tuple(map(int, value.split(', ')))
    return name2int_tuple

def default_fac():
    return "ERROR INCORRECT KEY"


@dataclass
class ConfigData:
    mask_color: Tuple[int, int, int, int] = mask_color()
    colors: dict[str, Tuple[int, int, int, int]] = load_config_to_name2int_tuple_dict('ordinary_colors')

    def __post_init__(self):
        colors = load_config_to_name2int_tuple_dict('ordinary_colors')
#   TODO


