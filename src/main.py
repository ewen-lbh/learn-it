import collections
import logging
import random

from termcolor import cprint, colored

from src import ask, parser, helpers
from src.consts import *


def train_loop(data: collections.OrderedDict, flags: parser.FlagsParser) -> None:
    found = list()
    # if we still have stuff not found
    while len(found) < len(data.keys()):
        # randomly pick a question, and get its corresponding answer
        asked = random.choice(list(data.keys()))
        answer = data[asked]
        # if the user replied correctly
        if ask.get_ans(asked, answer, flags):
            # add the question to found
            found.append(asked)
            cprint('Correct !', 'green')
        else:
            cprint('The correct answer was "{}"'.format(answer), 'red')


def testing_loop(data: collections.OrderedDict, flags: parser.FlagsParser) -> tuple:
    # init lists
    found = list()
    notfound = list()
    # for each learndata item
    for asked, answer in data.items():
        # if we found the correct answer
        if ask.get_ans(asked, answer, flags):
            # displays the message
            cprint("Correct !", "green")
            # adds the question to found list
            found.append(asked)
        # if we failed
        else:
            # show the answer if --show-answer-in-testing-mode allows it
            if flags.show_answer_in_testing_mode:
                cprint("The correct answer was: {}".format(answer), 'red')
            # or just simply print "Wrong"
            else:
                cprint("Wrong", 'red')
            # adds the question to notfound list
            notfound.append(asked)

        # if --always-show-grade allows it, calculate and print the grade after each answer
        if flags.always_show_grade:
            show_grade(found, data, flags)
    return found, notfound


def show_grade(found, data: collections.OrderedDict, flags: parser.FlagsParser) -> float:
    # get grade: the number of questions found (correctly answered) divided by --grade-max,
    # rounded to --grade-precision digits
    grade = round(len(found) / flags.grade_max, flags.grade_precision)
    # get color based on the threshold (--grade-max * --good-grade)
    # if the calculated grade is higher or equal to that threshold, set the text to green
    # else set it to red
    color = 'green' if grade >= flags.grade_max * flags.good_grade else 'red'
    # show values, with converted grade, and original grade (correctly answered / total number of learndata items)
    cprint('Your grade: {}/{} ({}/{})'.format(grade, int(flags.grade_max), len(found), len(data)), color)
    # returns the grade in case we want to use the value for further processing
    # todo if we ever need this, we should add a "no_print" argument to the function
    return grade


def recap(data: collections.OrderedDict) -> None:
    cprint("You need to learn about:", 'red')
    # prints nicely the items provided
    helpers.pprint_dict(data)


def header(flags: parser.FlagsParser, custom_text: str = None):
    # if a title is set (not to its default value, untitled)
    # or we provided a custom_text argument (useful for the "Debug info" header,
    # prevents duplicate code by re-using the same function, and respecting
    # --header and --header-color)
    if flags.title != 'untitled' or custom_text:
        # set the flag to the custom_text
        # if custom_text is not provided, use --title
        text = custom_text or flags.title
        # prints the header with the appropriate color and style
        cprint(flags.header.replace('<>', text), flags.header_color)

# todo fix the color, its based on LOGGING_LEVEL, it should be based on %(levelname)s .
def get_logging_props(level: str) -> tuple:
    level = level.upper() if level in LOGGING_LEVELS else "WARNING"
    termcolor_attrs = LOGGING_LEVELS_FORMATTING[level].split(', ')

    return getattr(logging, level), colored('%(levelname)s: %(message)s', *termcolor_attrs)


def main(sys_argv) -> int:

    try:
        # ---logging config---
        # we need to get level and debug flags before anything else because
        # flag parsing can output logs, and we need to decide whether we want
        # to show those. So we *have* to get the desired log level and debug mode (because debug
        # mode affects the selected log level) *before* parsing anything else.
        # This is far from elegant.
        # This is also a problem because setting --log-level or --debug via a --preset is not possible,
        # since the preset is parsed *after* this.
        #
        # POSSIBLE SOLUTIONS
        # (1) remove --log-level, only set it via a const in consts.py
        # (2) change logging basicConfig after flags parsing
        # (3) change logging basicConfig as soon as the --log-level flag is parsed
        # (4) A mix of #1 and #2, set the basicConfig according to a const,
        #     and change it after flags parsing
        #
        # currently, the solution 1 has been applied
        logging_level, logging_format = get_logging_props(LOG_LEVEL)
        logging.basicConfig(level=logging_level, format=logging_format)

        # the first sys.argv is "run.py", the hypothetical second item
        # is going to be the learndata file's path.

        # check if any filepath was specified
        if len(sys_argv) < 2:
            # fall back to DATA_FILE
            learndata_file = DATA_FILE
        else:
            # get filepath
            data_file_maybe = helpers.get_absolute_path(sys_argv[1])
            # check file existance
            if os.path.isfile(data_file_maybe):
                # set it as the learndata_file
                learndata_file = data_file_maybe
            else:
                # raise error and fall back to DATA_FILE
                logging.error(f"File {data_file_maybe} not found. \nFalling back to {DATA_FILE}")
                learndata_file = DATA_FILE

        # parse the flags and data from the text file
        data, flags = parser.parse_file(learndata_file)
        # convert the flags into a parser.FlagsParser object, and clean up flags by:
        # - adding non-declared flags with their default values
        # - removing unknown flags
        flags = parser.FlagsParser(flags)
        # transform learndata according to the flags
        data = parser.transform_learndata(data, flags)

        # debug
        if flags.debug:
            header(flags, custom_text='Debug info')
            print(flags)
            helpers.pprint_dict(data, sep='', column_names=('KEYS', 'VALUES'))

        # print header
        header(flags)

        # print loaded items count
        if flags.show_items_count:
            cprint('Loaded {} item{} from {}'.format(len(data), 's' if len(data) != 1 else '', DATA_FILE), 'green')

        # choose testing or training mode
        training_mode = ask.selection(MESSAGES['choose_mode'], list(MODES_PRETTY.values())) == MODES_PRETTY['testing']

        if training_mode:
            found, notfound = testing_loop(data, flags)
            show_grade(found, data, flags)
        else:
            # in training mode, all items are always found
            notfound = list()
            train_loop(data, flags)

        if len(notfound):
            recap(data)
    except KeyboardInterrupt:
        cprint("\nProcess closed by user.", 'red')
        return 1

