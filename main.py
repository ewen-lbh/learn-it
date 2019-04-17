import ast
import itertools
import random
import collections
import re
from termcolor import cprint, colored
from pprint import pprint

DATA_FILE = 'learndata_example.txt'
SYNTAX = {
    'flags'   : re.compile(r'--([\w\-]+) (.+)'),  # [0]: trues, [1]: falses
    'booleans': (('true', 'yes', 'on'), ('false', 'no', 'off')),
    'lists': re.compile(r'\[([,\w]+)\]'),
    'comments': re.compile(r'(?://)|(?:#) (.+)')
}

FLAGS_DEFAULTS = {
    'whitelist'      : [],
    'ask-sentence'   : '<>',
    'case-sensitive' : False,
    'ask-for'        : 'values',
    'ask-order'      : 'random',
    'ask-for-typos'  : False,
    'grade-max'      : 100,
    'good-grade'     : 0.5,
    'title'          : False,
    'and-syntax'     : '&&',
    'or-syntax'      : '||',
    'grade-precision': 2,
}

# automaticaly get flag types from defaults
# warning: this will only work for flags that accept a SINGLE type
FLAGS_TYPES = {flag: type(default) for flag, default in FLAGS_DEFAULTS.items()}


def parse(lines: list) -> tuple:
    def parse_flags(lines):
        def parse_flag_type(flag, val):
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
                parsed = str(val)
            except SyntaxError:
                parsed = str(val)

            # finally, if the parsed value's type correspond to the one described in FLAGS_TYPES,
            # return it. If it doesn't match (eg. we passed a list to the --case-sensitive flag), return None.
            if type(parsed) is FLAGS_TYPES[flag]:
                return parsed
            else:
                return None

        flags = dict()
        other_lines = list()
        for line in lines:
            if SYNTAX['flags'].match(line):
                flag = SYNTAX['flags'].search(line).group(1)
                val = SYNTAX['flags'].search(line).group(2)
                # automatic types
                val = parse_flag_type(flag, val)
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
        real_flags = dict()
        for flag, default in FLAGS_DEFAULTS.items():
            # set the value to the corresponding one in the dict, or get its default value
            # from FLAGS_DEFAULTS if not set
            real_flags[flag] = flags.get(flag, default)

        # set attribues programmatically, changing dashes to undescores
        # for the attributes names
        for flag, val in real_flags.items():
            setattr(self, flag.replace('-', '_'), val)

    def to_dict(self) -> dict:
        ret = {}
        for flag in FLAGS_DEFAULTS.keys():
            ret[flag] = getattr(self, flag.replace('-', '_'))
        return ret


def handle_flags(data: dict, flags: FlagsParser) -> tuple:
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
        print(shuffled)
        data = collections.OrderedDict()
        for k, v in shuffled:
            data[k] = v
    else:
        data = collections.OrderedDict(**data)

    return data


def yesno(msg) -> bool:
    return input(msg + '\n(y/n)>').lower().strip().startswith('y')


def get_ans(asked, answer, flags) -> bool:
    def ask(asked):
        sentence = flags.ask_sentence.replace('<>', asked)
        return input(sentence)

    # ans is the *user's* answer
    # answer is the *correct* answer
    ans = ask(asked).strip()

    if not flags.case_sensitive:
        ans = ans.lower()

    if ans == answer:
        return True
    else:
        if flags.ask_for_typos:
            if yesno("Was this a typo ?"):
                return get_ans(asked, answer)
        return False


def test_loop(data, flags) -> tuple:
    found = list()
    notfound = list()
    for asked, answer in data.items():
        if get_ans(asked, answer, flags):
            cprint("Correct !", "green")
            found.append(asked)
        else:
            cprint("The correct answer was: {}".format(answer), 'red')
            notfound.append(asked)


def main():
    DATA, FLAGS = parse_file(DATA_FILE)
    FLAGS = FlagsParser(FLAGS)
    DATA = handle_flags(DATA, FLAGS)
    print('===FLAGS===')
    pprint(FLAGS.to_dict())
    print('===DATA===')
    pprint(DATA)
    if yesno('Test mode ?'):
        found, notfound = test_loop(DATA, FLAGS)
        grade = round(len(found) / flags.grade_max, flags.grade_precision)
        color = 'green' if grade >= flags.grade_max * flags.good_grade else 'red'
        cprint('Your grade: {}/{} ({}/{})'.format(grade, int(flags.grade_max), len(found), len(DATA)), color)
    else:
        found, notfound = train_loop(DATA, FLAGS)

    if len(notfound):
        cprint("You need to learn about:", 'red')
        maxlen = max([len(e) for e in DATA.keys()])
        for asked, answer in DATA.items():
            sp = ' ' * (3 + (maxlen - len(asked)))
            print('{}{}:{}'.format(asked, sp, answer))


if __name__ == '__main__':
    main()
