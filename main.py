import ast
import itertools
import os
import random
import collections
import re
from termcolor import cprint
import helpers

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

    def print(self):
        helpers.pprint_dict(self.to_dict(), sep='', column_names=('FLAG NAMES', 'VALUES'))


def handle_flags(data: collections.OrderedDict, flags: FlagsParser) -> tuple:
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


def yesno(msg) -> bool:
    return input(msg + '\n(y/n)>').lower().strip().startswith('y')


def get_ans(asked, answer, flags) -> bool:
    global AUTO_ANSWER

    def ask(asked):
        sentence = flags.ask_sentence.replace('<>', asked)
        return input(sentence + '\n>') if not AUTO_ANSWER else ''

    # ans is the *user's* answer
    # answer is the *correct* answer
    ans = ask(asked).strip()

    if not flags.case_sensitive:
        ans = ans.lower()

    if ans == answer:
        return True
    else:
        if flags.ask_for_typos and not AUTO_ANSWER:
            if yesno("Was this a typo ?"):
                return get_ans(asked, answer)
        return False


def testing_loop(data: collections.OrderedDict, flags: FlagsParser) -> tuple:
    found = list()
    notfound = list()
    for asked, answer in data.items():
        if get_ans(asked, answer, flags):
            cprint("Correct !", "green")
            found.append(asked)
        else:
            if flags.show_answer_in_testing_mode:
                cprint("The correct answer was: {}".format(answer), 'red')
            else:
                cprint("Wrong", 'red')
            notfound.append(asked)

        if flags.always_show_grade:
            show_grade(found, data, flags)
    return found, notfound


def show_grade(found, data: collections.OrderedDict, flags: FlagsParser) -> float:
    grade = round(len(found) / flags.grade_max, flags.grade_precision)
    color = 'green' if grade >= flags.grade_max * flags.good_grade else 'red'
    cprint('Your grade: {}/{} ({}/{})'.format(grade, int(flags.grade_max), len(found), len(data)), color)
    return grade


def train_loop(data: collections.OrderedDict, flags: FlagsParser) -> None:
    found = list()
    # if we still have stuff not found
    while len(found) < len(data.keys()):
        # randomly pick a question, and get its corresponding answer
        asked = random.choice(list(data.keys()))
        answer = data[asked]
        # if the user replied correctly
        if get_ans(asked, answer, flags):
            # add the question to found
            found.append(asked)
        else:
            cprint('The correct answer was "{}"'.format(answer), 'red')


def recap(data: collections.OrderedDict) -> None:
    cprint("You need to learn about:", 'red')
    maxlen = max([len(e) for e in data.keys()])
    for asked, answer in data.items():
        sp = ' ' * (3 + (maxlen - len(asked)))
        print('{}{}:{}'.format(asked, sp, answer))


def selection(msg: str, choices: list, shortcuts=True, shortcuts_level: int = 1) -> str:
    """
    Ask the user to select a choice in a given choices list. This is NOT case sensitive.
    :param msg: message to display.
    The list of choices is generated automatically, insert it in your message by adding "<choices>" in it.
    :param choices: list of choices to choose from
    :param shortcuts: whether to use shortcuts or not
    :param shortcuts_level: shortcuts lengths (>= 1)
    This is useful when your choices list have choices that start with the same letter(s)
    :return: a string that is in choices
    """

    # todo auto-detect shortcuts_level

    if shortcuts_level < 1: shortcuts_level = 1

    # HANDLING SHORTCUTS {
    if shortcuts:
        shortcuts_map = {choice[:shortcuts_level]: choice for choice in choices}
        # remove duplicates from the list of shortcuts, and get the length
        deduped = list(set(list(shortcuts_map.keys())))
        # see if shortcuts are unambiguous by seeing if we removed any duplicates
        # if we removed any, the deduplicated list is shorter than the original shortcut map
        # this will also be considered ambiguous if deduped_len is greater than original_len, tho
        # this case should be unreachable.
        ambiguous_shortcuts = len(choices) != len(deduped)
        # if shortcuts are indeed ambiguous, use numbers instead, starting at one.
        if ambiguous_shortcuts:
            shortcuts_map = {str(i + 1): choice for i, choice in enumerate(choices)}
    else:
        shortcuts_map = {choice: choice for choice in choices}
    # }

    # HANDLING INPUT MESSAGE {
    choicelist = list()
    for shortcut, choice in shortcuts_map.items():
        if not shortcuts:
            choicelist.append('- {}'.format(choice))
        elif ambiguous_shortcuts:
            choicelist.append('{}: {}'.format(shortcut, choice))
        else:
            choicelist.append('[{}]{}'.format(shortcut, choice[len(shortcut):]))

    msg = msg.replace('<choices>', '\n'.join(choicelist)) + '\n>'
    # }

    ans = input(msg).strip().lower()
    while ans not in [e.lower() for e in shortcuts_map.keys()]:
        cprint('"{}" is not a valid choice. Please try again'.format(ans), 'red')
        ans = input('>').strip().lower()
    return


def header(flags: FlagsParser, custom_text: str = None):
    if flags.title != 'untitled' or custom_text:
        text = custom_text or flags.title
        cprint(flags.header.replace('<>', text), flags.header_color)


def main(learndata_file=DATA_FILE):
    # parse the flags and data from the text file
    data, flags = parse_file(learndata_file)
    # convert the flags into a FlagsParser object, and clean up flags by:
    # - adding non-declared flags with their default values
    # - removing unknown flags
    flags = FlagsParser(flags)
    # transform data according to the flags
    data = handle_flags(data, flags)

    # debug
    header(flags, custom_text='Debug info')
    if flags.debug:
        flags.print()
        helpers.pprint_dict(data, sep='', column_names=('KEYS','VALUES'))

    # print header
    header(flags)

    # print loaded items count
    if flags.show_items_count:
        cprint('Loaded {} item{} from {}'.format(len(data), 's' if len(data) != 1 else '', DATA_FILE), 'green')

    # choose testing or training mode
    training_mode = selection(MESSAGES['choose_mode'], list(MODES_PRETTY.values())) == MODES_PRETTY[
        'testing'] if not flags.debug else True

    if training_mode:
        found, notfound = testing_loop(data, flags)
        show_grade(found, data, flags)
    else:
        # in training mode, all items are always found
        notfound = list()
        train_loop(data, flags)

    if len(notfound):
        recap(data)


if __name__ == '__main__':
    main()
