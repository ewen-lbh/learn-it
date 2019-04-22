import os
import re

from src import helpers

if os.name == 'nt':
    LEARNDATA_ROOT = 'D:\\Users\\ewenl\\Documents\\work\\learndata'
else:
    LEARNDATA_ROOT = '~/Documents/work/learndata'

DATA_FILE = 'maths/suites.txt'
LOG_LEVEL = 'WARNING'
LANGUAGE = 'fr'

PRESETS_FILE = 'presets.json'
DEBUG = False
AUTO_ANSWER = False
ALWAYS_USE_DATA_FILE = False

SYNTAX = {
    'flags'   : re.compile(r'--([\w][\w\-]*)(?:[ =](.+))?'),  # [0]: trues, [1]: falses
    'booleans': (('true', 'yes', 'on'), ('false', 'no', 'off')),
    'lists'   : re.compile(r'\[([,\w ]+)\]'),
    'comments': re.compile(r'(?://)|(?:#) (.+)')
}

T = helpers.get_translations(LANGUAGE)

FLAGS_DEFAULTS = {
    # 'and-syntax'                 : '&&',
    # 'or-syntax'                  : '||',
    # 'no-colors'                  : False,
    'always-show-grade'          : False,
    'ask-for'                    : 'values',
    'ask-for-typos'              : False,
    'ask-order'                  : 'random',
    'ask-sentence'               : '<>',
    'auto-blacklist'             : False,
    'case-sensitive'             : False,
    'debug'                      : DEBUG,
    'good-grade'                 : 0.5,
    'grade-max'                  : 100,
    'grade-precision'            : 2,
    'header'                     : '---- <> ----',
    'header-color'               : 'cyan',
    # todo rename to --show-answer
    'show-answer-in-testing-mode': True,
    'show-items-count'           : DEBUG,
    'show-remaining-items-count' : False,
    'strict-learn-about'         : True,
    'title'                      : 'untitled',
    'warn-unknown-flags'         : True,
    'whitelist'                  : [],
    'blacklist'                  : [],
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
    'auto-blacklist'             : bool,
    'case-sensitive'             : bool,
    'debug'                      : bool,
    'good-grade'                 : float,
    'grade-max'                  : int,
    'grade-precision'            : int,
    'header'                     : str,
    'header-color'               : ('white', 'red', 'yellow', 'green', 'cyan', 'blue', 'magenta'),
    'show-answer-in-testing-mode': bool,
    'show-items-count'           : bool,
    'show-remaining-items-count' : bool,
    'strict-learn-about'         : bool,
    'title'                      : str,
    'warn-unknown-flags'         : bool,
    'whitelist'                  : list,
    'blacklist'                  : list,
}

# Get real and absolute paths for DATA_FILE and PRESETS_FILE
LEARNDATA_ROOT = os.path.normpath(os.path.expanduser(LEARNDATA_ROOT))
if DATA_FILE.startswith('<no_append_root>'):
    DATA_FILE = os.path.abspath(os.path.expanduser(DATA_FILE.replace('<no_append_root>','',1)))
else:
    DATA_FILE = os.path.abspath(os.path.join(LEARNDATA_ROOT, DATA_FILE))
PRESETS_FILE = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), PRESETS_FILE))

# available logging levels
LOGGING_LEVELS = ["FATAL", "ERROR", "WARNING", "INFO", "DEBUG"]
# termcolor attributes, comma-separated (with a space after the comma)
LOGGING_LEVELS_FORMATTING = {
    "FATAL": "white, on_red", "ERROR": "red", "WARNING": "yellow", "INFO": "white", "DEBUG": "white"
}
