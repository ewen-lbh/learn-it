import os
import re

LEARNDATA_ROOT = '~/Documents/work/learndata'
DATA_FILE = 'maths/suites.txt'
LOG_LEVEL = 'WARNING'

PRESETS_FILE = 'presets.json'
DEBUG = False
AUTO_ANSWER = False

SYNTAX = {
    'flags'   : re.compile(r'--([\w][\w\-]*)(?:[ =](.+))?'),  # [0]: trues, [1]: falses
    'booleans': (('true', 'yes', 'on'), ('false', 'no', 'off')),
    'lists'   : re.compile(r'\[([,\w]+)\]'),
    'comments': re.compile(r'(?://)|(?:#) (.+)')
}

MESSAGES = {
    'choose_mode': 'Choose a mode:\n<choices>'
}

MODES_PRETTY = {
    'training': 'Training mode', 'testing': 'Testing mode'
}

FLAGS_DEFAULTS = {
    # 'and-syntax'                 : '&&',
    # 'or-syntax'                  : '||',
    # 'no-colors'                  : False,
    'always-show-grade'          : False,
    'ask-for'                    : 'values',
    'ask-for-typos'              : False,
    'ask-order'                  : 'random',
    'ask-sentence'               : '<>',
    'case-sensitive'             : False,
    'debug'                      : DEBUG,
    'good-grade'                 : 0.5,
    'grade-max'                  : 100,
    'grade-precision'            : 2,
    'header'                     : '---- <> ----',
    'header-color'               : 'cyan',
    'show-answer-in-testing-mode': True,
    'show-items-count'           : DEBUG,
    'title'                      : 'untitled',
    'warn-unknown-flags'         : True,
    'whitelist'                  : [],
}

# automaticaly get flag types from defaults
# warning: this will only work for flags that accept a SINGLE type
# FLAGS_TYPES = {flag: type(default) for flag, default in FLAGS_DEFAULTS.items()}

FLAGS_TYPES = {
    # 'and-syntax'                 : str,
    # 'or-syntax'                  : str,
    # 'no-colors'                  : bool,
    'always-show-grade'          : bool,
    'ask-for'                    : ('values', 'both', 'keys'),
    'ask-for-typos'              : bool,
    'ask-order'                  : ('random', 'keep', "alphabetical"),
    'ask-sentence'               : str,
    'case-sensitive'             : bool,
    'debug'                      : bool,
    'good-grade'                 : float,
    'grade-max'                  : int,
    'grade-precision'            : int,
    'header'                     : str,
    'header-color'               : ('white', 'red', 'yellow', 'green', 'cyan', 'blue', 'magenta'),
    'show-answer-in-testing-mode': bool,
    'show-items-count'           : bool,
    'title'                      : str,
    'warn-unknown-flags'         : bool,
    'whitelist'                  : list,
}

# Get real and absolute paths for DATA_FILE and PRESETS_FILE
LEARNDATA_ROOT = os.path.normpath(os.path.expanduser(LEARNDATA_ROOT))
DATA_FILE = os.path.abspath(os.path.join(LEARNDATA_ROOT, DATA_FILE))
PRESETS_FILE = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), PRESETS_FILE))

# available logging levels
LOGGING_LEVELS = ["FATAL", "ERROR", "WARNING", "INFO", "DEBUG"]
# termcolor attributes, comma-separated (with a space after the comma)
LOGGING_LEVELS_FORMATTING = {
    "FATAL": "white, on_red", "ERROR": "red", "WARNING": "yellow", "INFO": "white", "DEBUG": "white"
}