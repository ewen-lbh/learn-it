import ast
import itertools
import collections
import random

from src import helpers
from src.consts import *


def parse(lines: list) -> tuple:
    
    def parse_flags(lines):
        def parse_flag_type(val):
            # handle booleans, see if the lowercase flag value is in ANY of the booleans syntax
            # (that's why we flatten the nested tuples with itertools.chain's from_iterable)
            if val.lower() in list(itertools.chain.from_iterable(SYNTAX['booleans'])):
                # the first child tuple contains trues
                return val.lower() in SYNTAX['booleans'][0]

            # handle lists. Those aren't handled by ast.literal_eval because the syntax used doesn't require
            # quotes around values, considering it as a list of string anyway
            if SYNTAX['lists'].match(val):
                # get only values
                vals = SYNTAX['lists'].search(val).group(1)
                # split by ",", and strip values to remove potential whitespace
                # (eg if the user noted the list with ", " as the separator)
                return [e.strip() for e in vals.split(',')]

            # handle everything else (floats, ints)
            try:
                parsed = ast.literal_eval(val)
            # if ast returns a Syntax or Value error, it means that the value is a string
            # that's because, again, we don't require quoting strings, and pyton's parser doesn't like that
            except ValueError:
                parsed = str(val).strip()
            except SyntaxError:
                parsed = str(val).strip()

            return parsed

        flags = dict()
        other_lines = list()
        for line in lines:
            if SYNTAX['flags'].match(line):
                flag = SYNTAX['flags'].search(line).group(1)
                val = SYNTAX['flags'].search(line).group(2)
                # we do this because an unmatched regex group (the value one in this case)
                # assigns a value of None to it. If we specify a flag alone,
                # we want to set it to true (kinda like bash's flags)
                if val is None:
                    val = True
                else:
                    # automatic types
                    val = parse_flag_type(val)
                # if there wasn't any errors while parsing and converting the
                # value to its correct type:
                if val is not None:
                    flags[flag] = val
            else:
                other_lines.append(line)
        return flags, other_lines

    def cleanup(lines: list):
        # removes comments, ending \n in lines list
        # and strips the list, removing all empty lines before and after data
        ret = list()
        for line in lines:
            line = line.rstrip('\n')
            if not SYNTAX['comments'].match(line):
                ret.append(line)

        ret = helpers.strip_list(ret)
        return ret

    def parse_data(lines: list):
        # reminder: the syntax used is :
        # key
        # value
        # <empty line>

        data = dict()
        for i, line in enumerate(lines):
            # get the previous/next line, or set it to an empty one
            # if this is the first/last line
            if i > 0:
                prevline = lines[i - 1]
            else:
                prevline = ''
            try:
                nextline = lines[i + 1]
            except IndexError:
                nextline = ''

            # if the previous line is empty (ie if the previous line is a separator)
            # we add a new item, with:
            # key - the current line
            # value - the next line
            if not prevline:
                data[line] = nextline
            # if we are in the middle of a item (ie on the value line) or on a separator, skip the line
            else:
                continue
        return data

    # parse flags first, and get a new "lines" list, without flags declarations in it.
    # we do this because we don't need to clean anything before, as the flags parser uses
    # a strict syntax (the line must match the SYNTAX['flags'] regex pattern)
    flags, lines = parse_flags(lines)
    # clean up the lines, removing:
    # - empty lines at the beginning and the end
    # - ending "\n" at each line
    # - comments
    lines = cleanup(lines)
    data = parse_data(lines)

    return data, flags


def parse_file(filepath: str) -> tuple:
    with open(filepath, 'r', encoding='utf8') as f:
        lines = f.readlines()
    return parse(lines)


class FlagsParser:
    def __init__(self, flags: dict):
        self.ask_order = None
        real_flags = dict()
        for flag, default in FLAGS_DEFAULTS.items():
            # set the value to the corresponding one in the dict, or get its default value
            # from FLAGS_DEFAULTS if not set
            val = flags.get(flag, default)

            # If the flag's value type does not match the one described in FLAGS_TYPES,
            # (eg. we passed a list to the --case-sensitive flag),
            # ignore the flag's value and fallback to the default one
            if type(val) is not FLAGS_TYPES[flag]:
                val = default

            real_flags[flag] = val

        # set attribues programmatically, changing dashes to undescores
        # for the attributes names
        for flag, val in real_flags.items():
            setattr(self, flag.replace('-', '_'), val)

    def to_dict(self) -> dict:
        ret = {}
        for flag in FLAGS_DEFAULTS.keys():
            ret[flag] = getattr(self, flag.replace('-', '_'))
        return ret

    def __str__(self):
        return helpers.pprint_dict(self.to_dict(), sep='', column_names=('FLAG NAMES', 'VALUES'), return_str=True)


def handle_flags(data: collections.OrderedDict, flags: FlagsParser) -> collections.OrderedDict:
    # --case-sensitive
    if not flags.case_sensitive:
        data = {k.lower(): v.lower() for k, v in data.items()}

    # --whitelist
    if len(flags.whitelist):
        data = {k: v for k, v in data.items() if k in flags.whitelist}

    # --ask-order
    if flags.ask_order == 'random':
        shuffled = list(data.items())
        # random.shuffle changes the list *in-place*
        random.shuffle(shuffled)
        data = collections.OrderedDict()
        for k, v in shuffled:
            data[k] = v
    elif flags.ask_order == 'alphabetical':
        data = collections.OrderedDict(sorted(data.keys()))

    else:
        data = collections.OrderedDict(**data)

    return data