import os
import re

LEARNDATA_ROOT = '~/Documents/work/learndata'
DATA_FILE = 'maths/suites.txt'
DEBUG = False
SYNTAX = {
    'flags'   : re.compile(r'--([\w\-]+)(?:[ =](.+))?'),  # [0]: trues, [1]: falses
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
    # 'warn-unknown-flags'         : True,
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
    'whitelist'                  : [],
}

# automaticaly get flag types from defaults
# warning: this will only work for flags that accept a SINGLE type
# todo specify allowed value(s) / type(s) instead
FLAGS_TYPES = {flag: type(default) for flag, default in FLAGS_DEFAULTS.items()}

AUTO_ANSWER = False
LEARNDATA_ROOT = os.path.normpath(os.path.expanduser(LEARNDATA_ROOT))
DATA_FILE = os.path.abspath(os.path.join(LEARNDATA_ROOT, DATA_FILE))