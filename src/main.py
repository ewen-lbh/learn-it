import collections
import logging
import random
import tkinter as tk
from tkinter import filedialog

from src import ask, parser
from src.consts import *
from src.helpers import cprint, colored


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
            cprint(T['correct'], "green")
        else:
            cprint(T['correct_answer'].format(answer), 'red')


def testing_loop(data: collections.OrderedDict, flags: parser.FlagsParser) -> tuple:
    # init lists
    found = list()
    notfound = list()
    # for each learndata item
    for asked, answer in data.items():
        # if we found the correct answer
        if ask.get_ans(asked, answer, flags):
            # displays the message
            cprint(T['correct'], "green")
            # adds the question to found list
            found.append(asked)
        # if we failed
        else:
            # show the answer if --show-answer-in-testing-mode allows it
            if flags.show_answer_in_testing_mode:
                cprint(T['correct_answer'].format(answer), 'red')
            # or just simply print "Wrong"
            else:
                cprint(T['wrong'], 'red')
            # adds the question to notfound list
            notfound.append(asked)

        # if --always-show-grade allows it, calculate and print the grade after each answer
        if flags.always_show_grade:
            show_grade(found, data, flags)
    return found, notfound


def show_grade(found, data: collections.OrderedDict, flags: parser.FlagsParser) -> float:
    # get grade: the number of questions found (correctly answered) divided by the total number of questions
    # rounded to --grade-precision digits and converted to fit --grade-max
    grade = round(len(found) / len(data) * flags.grade_max, flags.grade_precision)
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
    lines = helpers.pprint_dict(data, return_str=True).split('\n')
    lines = [e.strip() for e in lines]
    # function to determinate if the terminal is big enough to show N lines
    has_enough_space_for = lambda n:shutil.get_terminal_size().columns >= maxlinelen * n
    # get maximum length of one line
    maxlinelen = max([len(e) for e in lines]) + 2  # padding
    # determine number of columns based on number of lines
    if len(lines) >= 16:
        cols = 4
    elif len(lines) >= 8:
        cols = 2
    else:
        cols = 1

    while not has_enough_space_for(cols):
        cols -= 1
    if cols < 1: cols = 1

    columns = list()
    col_idx = -1
    for i, line in enumerate(lines):
        if i % cols == 0:
            columns.append([line])
            col_idx += 1
        else:
            columns[col_idx].append(line)

    helpers.colprint(columns, pad=2)


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

    return getattr(logging, level), colored('%(levelname)s: %(message)s', 'yellow')


def auto_blacklist(to_blacklist: list, flags: parser.FlagsParser, learndata_file: str):
    with open(learndata_file, 'r', encoding='utf8') as f:
        lines = f.read().split('\n')
    newlines = list()
    # removes blacklist declaration if found
    for line in lines:
        if SYNTAX['flags'].match(line):
            flag = SYNTAX['flags'].search(line).group(1)
            if flag == 'blacklist':
                continue
        newlines.append(line)

    # adds items to the blacklist
    blacklist = flags.blacklist + to_blacklist
    # removes duplicates in list
    blacklist = list(set(blacklist))
    # todo implement this better, if SYNTAX['list'] changes, this doesn't.
    declaration_line = '--blacklist [' + ', '.join(blacklist) + ']'
    # prepends the blacklist declaration to the lines
    newlines = [declaration_line] + newlines
    with open(learndata_file, 'w', encoding='utf8') as f:
        f.write('\n'.join(newlines))


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

        # check if any filepath was specified...
        # via command-line argument
        fallback = False
        if len(sys_argv) >= 2:
            data_file_maybe = helpers.get_absolute_path(sys_argv[1])
            # check file existence
            if os.path.isfile(data_file_maybe):
                # set it as the learndata_file
                learndata_file = data_file_maybe
            else:
                # try changing the dir for the filepath with LEARNDATA_ROOT...
                logging.info(T['assuming_learndata_root'].format(file=helpers.path_contract_user(data_file_maybe),
                    directory=helpers.path_contract_user(LEARNDATA_ROOT)))
                data_file_maybe = os.path.abspath(os.path.join(LEARNDATA_ROOT, sys_argv[1]))
                if os.path.isfile(data_file_maybe):
                    learndata_file = data_file_maybe
                else:
                    # try adding .txt at the end...
                    logging.info(T["appending_.txt"].format(helpers.path_contract_user(data_file_maybe)))
                    data_file_maybe += '.txt'
                    if os.path.isfile(data_file_maybe):
                        learndata_file = data_file_maybe
                    else:
                        fallback = True
        # or via GUI
        if ALWAYS_USE_DATA_FILE:
            learndata_file = DATA_FILE
        else:
            root = tk.Tk()
            root.withdraw()
            data_file_maybe = filedialog.askopenfilename()
            if os.path.isfile(data_file_maybe):
                learndata_file = data_file_maybe
            else:
                # fall back to DATA_FILE
                fallback = True

        if fallback:
            # raise error and fall back to DATA_FILE
            logging.error(T["using_fallback_learndata"].format(file=helpers.path_contract_user(data_file_maybe),
                fallback=helpers.path_contract_user(DATA_FILE)))
            learndata_file = DATA_FILE

        # parse the flags and data from the text file
        data, flags = parser.parse_file(learndata_file)
        # convert the flags into a parser.FlagsParser object, and clean up flags by:
        # - adding non-declared flags with their default values
        # - removing unknown flags
        flags = parser.FlagsParser(flags)
        # keep the original data's length (used for --show-items-count)
        full_data_count = len(data)
        # transform learndata according to the flags
        data = parser.transform_learndata(data, flags)

        # debug
        if flags.debug:
            header(flags, custom_text='Debug info')
            helpers.pprint_dict(data, sep='', column_names=('KEYS', 'VALUES'))
            print('')
            print(flags)
            print('')

        # print header
        header(flags)

        # print loaded items count
        if flags.show_items_count:
            display_path = learndata_file.replace(LEARNDATA_ROOT, '').lstrip('\\').lstrip('/')
            cprint(T['loaded_items'].format(count=len(data), o_count=full_data_count, s='s' if len(data) != 1 else '',
                                            file=display_path), 'green')

        # choose testing or training mode
        training_mode = ask.selection(T['choose_mode'], (T['testing'], T['training'])) == T['testing']

        def main_loop(training_mode: bool, data, flags, no_recap: bool = False):
            if training_mode:
                found, notfound = testing_loop(data, flags)
                show_grade(found, data, flags)
            else:
                # in training mode, all items are always found
                notfound = list()
                train_loop(data, flags)

            if len(notfound) and not no_recap:
                recap(collections.OrderedDict({k:v for k, v in data.items() if k in notfound}))
                if flags.auto_blacklist:
                    auto_blacklist(data, flags)

        # if we ask for keys AND values, execute main_loop (without showing a recap, it would give away the answers),
        # invert the dict's mapping and execute main_loop again.
        if flags.ask_for == 'both':
            main_loop(training_mode, data, flags, no_recap=True)
            data = helpers.invert_dict_mapping(data)
            main_loop(training_mode, data, flags)
        else:
            main_loop(training_mode, data, flags)

    except KeyboardInterrupt:
        cprint("\n" + T['process_closed_by_user'], 'red')
        return 1
