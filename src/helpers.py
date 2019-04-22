import json
import logging
import os
import sys
from termcolor import colored as termcolored
import colorama


def pprint_dict(data: dict, pad: int = 1, sep: str = ': ', column_names: tuple = None, return_str: bool = False):
    k_maxlen = max([len(str(e)) for e in data.keys()])
    v_maxlen = max([len(str(e)) for e in data.values()])
    ret = list()

    data = list(data.items())
    if column_names:
        data.insert(0, column_names)
        data.insert(1, ('-' * k_maxlen, '-' * v_maxlen))

    for k, v in data:
        spaces = ' ' * (k_maxlen - len(k) + pad)
        if return_str:
            ret.append(f'{k}{spaces}{sep}{v}')
        else:
            print(k, spaces, sep, v, sep='')

    if return_str: return '\n'.join(ret)


def strip_list(iterable: list) -> list:
    def _partial_strip(iterable: list) -> list:
        while iterable and not iterable[-1]:
            iterable.pop()
        return iterable

    iterable = _partial_strip(iterable)
    iterable = list(reversed(_partial_strip(list(reversed(iterable)))))

    return iterable


def get_absolute_path(path: str) -> str:
    return os.path.abspath(os.path.expanduser(path))


def path_contract_user(path: str) -> str:
    return path.replace(os.path.expanduser('~'), '~', 1)


def invert_dict_mapping(dikt: dict) -> dict:
    return {v: k for k, v in dikt.items()}


def path_go_up(path: str, times: int = 1) -> str:
    path = os.path.abspath(path)
    for _ in range(times):
        path = os.path.dirname(path)
    return path

def get_translations(lang='en'):
    if lang == 'en':
        from translations.en import T
    elif lang == 'fr':
        from translations.fr import T
    else:
        logging.fatal(f'Unknown language "{lang}"')
        sys.exit(0)

    return T[lang]


def get_resource(resource_name):
    if resource_name == 'presets':
        from src.presets import PRESETS
        return PRESETS

def colored(*args, **kwargs):
    colorama.init()
    return termcolored(*args, **kwargs)

def cprint(*args, **kwargs):
    print(colored(*args, **kwargs))