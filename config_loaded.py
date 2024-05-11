from dataclasses import dataclass
from typing import Tuple, Any
import configparser


def mask_color(config: configparser.ConfigParser) -> Tuple[int, ...]:
    return tuple(map(int, config['special_colors']['mask_color'].split(', ')))


def load_config_to_name2int_tuple_dict(config: configparser.ConfigParser, config_branch: str) -> dict[
    str, tuple[int, ...]]:
    config = configparser.ConfigParser()
    config.read('config.ini')
    name_tuple = config[config_branch]
    name2int_tuple = {}
    for name, value in name_tuple.items():
        name2int_tuple[name] = tuple(map(int, value.split(', ')))
    return name2int_tuple


def read_config():
    config = configparser.ConfigParser()
    config.read('config.ini')
    return {
        'mask_color': mask_color(config),
        'colors': load_config_to_name2int_tuple_dict(config, 'ordinary_colors')
    }


# @dataclass
# class ConfigData:
#     mask_color: Tuple[int, int, int, int] = mask_color()
#     colors: dict[str, Tuple[int, int, int, int]] = None
#
#     def __post_init__(self):
#         colors = load_config_to_name2int_tuple_dict('ordinary_colors')
# #   TODO

class ConfigData:
    _instance = None
    _config_dict = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def get_config(cls):
        if cls._config_dict is None:
            cls._config_dict = read_config()
        return cls._config_dict

    @classmethod
    def get_attr(cls, attr_name: str) -> Any:
        return cls.get_config()[attr_name]
