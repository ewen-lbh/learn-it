import random
import collections
from termcolor import cprint
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
    found = list()
    notfound = list()
    for asked, answer in data.items():
        if ask.get_ans(asked, answer, flags):
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


def show_grade(found, data: collections.OrderedDict, flags: parser.FlagsParser) -> float:
    grade = round(len(found) / flags.grade_max, flags.grade_precision)
    color = 'green' if grade >= flags.grade_max * flags.good_grade else 'red'
    cprint('Your grade: {}/{} ({}/{})'.format(grade, int(flags.grade_max), len(found), len(data)), color)
    return grade


def recap(data: collections.OrderedDict) -> None:
    cprint("You need to learn about:", 'red')
    maxlen = max([len(e) for e in data.keys()])
    for asked, answer in data.items():
        sp = ' ' * (3 + (maxlen - len(asked)))
        print('{}{}:{}'.format(asked, sp, answer))


def header(flags: parser.FlagsParser, custom_text: str = None):
    if flags.title != 'untitled' or custom_text:
        text = custom_text or flags.title
        cprint(flags.header.replace('<>', text), flags.header_color)


def main(learndata_file=DATA_FILE):
    # parse the flags and data from the text file
    data, flags = parser.parse_file(learndata_file)
    # convert the flags into a parser.FlagsParser object, and clean up flags by:
    # - adding non-declared flags with their default values
    # - removing unknown flags
    flags = parser.FlagsParser(flags)
    # transform data according to the flags
    data = parser.handle_flags(data, flags)

    # debug
    header(flags, custom_text='Debug info')
    if flags.debug:
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


if __name__ == '__main__':
    main()
