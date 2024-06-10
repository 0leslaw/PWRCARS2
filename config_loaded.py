import ast
from typing import Tuple, Any
import configparser


def set_config_for_game(settings):
    # Read the configuration file
    config = configparser.ConfigParser()
    config.read('config.ini')

    # Modify the configuration
    config['game_init']['laps'] = settings['laps']
    config['game_init']['game_mode'] = settings['game_mode']
    config['player_1']['car_texture'] = settings['player_1']
    if 'player_2'in settings:
        config['player_2']['car_texture'] = settings['player_2']

    # Write the modified configuration back to the file
    with open('config.ini', 'w') as configfile:
        config.write(configfile)

    ConfigData._update_config()


def update_car_config(player_car):
    config = configparser.ConfigParser()
    config.read('config.ini')

    # Modify the configuration

    config[player_car[0]]['car_texture'] = player_car[1]

    # Write the modified configuration back to the file
    with open('config.ini', 'w') as configfile:
        config.write(configfile)

def mask_color(config: configparser.ConfigParser) -> Tuple[int, ...]:
    return tuple(map(int, config['special_colors']['mask_color'].split(', ')))


def load_config_to_name2int_tuple_dict(config: configparser.ConfigParser, config_branch: str) -> dict[
    str, tuple[int, ...]]:
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
        'colors': load_config_to_name2int_tuple_dict(config, 'ordinary_colors'),
        'game_mode': config['game_init']['game_mode'],
        'num_of_players': int(config['game_init']['num_of_players']),
        'laps': int(config['game_init']['laps']),
        'player1': {
            'name': config['player_1']['name'],
            'keys': ast.literal_eval(config['player_1']['keys']),
            'car_texture': config['player_1']['car_texture']
        },
        'player2': {
            'name': config['player_2']['name'],
            'keys': ast.literal_eval(config['player_2']['keys']),
            'car_texture': config['player_2']['car_texture']
        },
        'car_textures_dir': config['textures']['car_textures_dir']
    }


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
    def _update_config(cls):
        cls._config_dict = read_config()

    @classmethod
    def get_attr(cls, attr_name: str) -> Any:
        return cls.get_config()[attr_name]
