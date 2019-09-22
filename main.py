import yaml
import random
from termcolor import colored, cprint
import click
import time
import os


class Learn_it:

    # ----------------
    # >  CONSTANTS   <
    # ----------------

    _FLAGS = {
        'whitelist': {
            'allow-types': [list],
            'default': [],
        },
        'blacklist': {
            'allow-types': [list],
            'default': [],
        },
        'ask-sentence': {
            'allow-types': [str],
            'default': "<>",
        },
        'ask-for': {
            'allow-values': ['questions', 'answers', 'both'],
            'default': 'answers',
        },
        'ask-order': {
            'allow-values': ['random', 'inverted', 'normal'],
            'default': 'random',
        },
        'allow-typos': {
            'allow-types': [bool],
            'default': True,
        },
        'grade-max': {
            'allow-types': [float, int],
            'default': 20,
        },
        'good-grade': {
            'allow-types': [float],
            'default': 0.5,
        },
        'title': {
            'allow-types': [str],
            'default': "",
        },
        'show-items-count': {
            'allow-types': [bool],
            'default': True,
        },
        'debug': {
            'allow-types': [bool],
            'default': False,
        },
        'success-sentence': {
            'allow-types': [str],
            'default': '✓ Success!',
        },
        'fail-sentence': {
            'allow-types': [str],
            'default': '✕ Fail',
        },
        'hide-timeout': {
            'allow-types': [int],
            'default': 0,
        },
        'math-delimiter': {
            'allow-types': [str],
            'default': '$$',
        },
    }

    FLAGS_KEY_NAME = 'options'

    def __init__(self, file_paths, mode, **cli_flags):
        self._raws = []
        self._datas = []

        for file_path in file_paths:
            with open(file_path, 'r') as f:
                raw = f.read()
                self._raws.append(raw)
                self._datas.append(yaml.load(raw, Loader=yaml.SafeLoader))
        
        # Get options for the FIRST data set
        self.flags = self._datas[0].get(self.FLAGS_KEY_NAME, {})
        # Compute title from titles of each file, if the file's _data contains a self.FLAGS_KEY_NAME key, that contains a 'title' key
        self.flags['title'] = ', '.join(_data[self.FLAGS_KEY_NAME]['title'] for _data in self._datas if _data.get(self.FLAGS_KEY_NAME, None).get('title', None) is not None)
        # Merge the data
        self._data = {}
        for dataset in self._datas:
            self._data.update(dataset)
        
        self._cli_flags = cli_flags
        self.mode = mode

    # -----------------------
    # >  FLAGS PROCESSING   <
    # -----------------------

    def add_cli_flags(self):
        for flag, value in self._cli_flags.items():
            flag = flag.replace('_', '-')
            self.flags[flag] = value

    def strip_flags(self):
        valid_flags = dict()
        for name, value in self.flags.items():
            # Flag name verification
            if name not in self._FLAGS.keys():
                continue

            # Check for values
            validator = self._FLAGS[name]
            if 'allow-types' in validator.keys():
                if type(value) not in validator['allow-types']: 
                    continue
            
            if 'allow-values' in validator.keys():
                if value not in validator['allow-values']: 
                    continue

            # if we've made it here, the flag is legit.
            valid_flags[name] = value

        self.flags = valid_flags

    def add_default_flags(self):
        new_flags = dict()
        for flag, flagdata in self._FLAGS.items():
            default_value = flagdata['default']
            if flag not in self.flags.keys():
                new_flags[flag] = default_value

        self.flags.update(new_flags)

        # Take filename as a title
        if not self.flags['title']:
            filepath = self._cli_flags['file']
            parent_path, filename = os.path.split(filepath)
            filename, _ = os.path.splitext(filename)
            direct_folder = os.path.basename(parent_path)
            self.flags['title'] = direct_folder + '/' + filename.title()

    def process_flags(self):
        self.add_cli_flags()
        self.strip_flags()
        self.add_default_flags()

    # --------------------------
    # >  ASK DATA PROCESSING   <
    # --------------------------

    def process_math_answer(self, answer):
        from sympy.parsing.latex import parse_latex
        from sympy.simplify import simplify
        from sympy import oo
        # LaTeX --> SymPy
        expr = parse_latex(answer)
        # Simplify the expression
        expr = simplify(expr, ratio=oo)
        # SymPy --> unicode string
        return str(expr)

    def process_answer(self, answer):
        answer = str(answer)

        delimiter = self.flags['math-delimiter']
        if answer.startswith(delimiter) and answer.endswith(delimiter):
            return self.process_math_answer(answer.replace('$$', ''))
        else:
            return answer

    def process_learndata(self):
        self.askdata = list()
        for question, answer in self._data.items():
            if question == self.FLAGS_KEY_NAME:
                continue

            if type(answer) is not list:
                answer = [answer]

            answer = [self.process_answer(ans) for ans in answer]

            # remove duplicates while maintaining order
            from collections import OrderedDict
            answer = list(OrderedDict.fromkeys(answer))

            self.askdata.append(
                (question, answer)
            )

    def get_flipped_askdata(self):
        flipped = list()
        for question, answers in self.askdata:
            for answer in answers:
                # this question has already been added
                # that happens if two questions have the same answer
                # in the learndata
                if answer in [answer for answer, question in flipped]:
                    # get item of flipped that already has that
                    idx = flipped.index([
                        i for i in flipped
                        if i[0] == answer
                    ][0])

                    answer, questions = flipped[idx]
                    questions.append(question)
                    flipped[idx] = (answer, questions)
                    continue

                flipped.append(
                    (answer, [question])
                )

        return flipped

    def process_ask_order(self, ask_order=None):
        if ask_order is None:
            ask_order = self.flags['ask-order']

        if ask_order == 'random':
            random.shuffle(self.askdata)
        elif ask_order == 'inverted':
            self.askdata = list(reversed(self.askdata))
        elif ask_order == 'alphabetical':
            self.askdata = list(sorted(self.askdata))

    def process_askdata(self):
        self.process_learndata()
        self.process_ask_order()

    # ------------------------
    # >  CLI-RELATED STUFF   <
    # ------------------------

    def get_largest_key_length(self):
        return max(len(k) for k, v in self.askdata)

    def compute_score(self):
        grade_max      = self.flags['grade-max']
        total          = len(self.askdata)
        success_count  = total - len(self.fails)

        grade = success_count / total * grade_max

        disp_total = '%' if grade_max == 100 else f'/{grade_max}'
        # if the grade is in x.000 (no decimal part)
        if int(grade) == grade:
            disp_grade = str(int(grade))
        else:
            disp_grade = '{:.2f}'.format(grade)

        return f"{disp_grade}{disp_total}"

    def get_ask_sentence(self, asked):
        return self.flags['ask-sentence'].replace('<>', asked)

    def format_answers_list(self, answers_list):
        if len(answers_list) == 1:
            return answers_list[0]
        else:
            return colored(' or ', color="cyan").join(answers_list)

    def list_fails(self):
        import funcy
        if not self.fails: return []

        max_len = max([len(e) for e in self.fails])
        def padding(k): return ' ' * (max_len - len(k))

        print_fmt = '{question}{padding}: {answer}'
        failed_items = {k: v for k, v in self.askdata if k in self.fails}
        ret = list()
        for i, (q, a) in enumerate(failed_items.items()):
            string = print_fmt.format(
                question=q, answer=self.format_answers_list(a), padding=padding(q))
            # FIXME: Currently the commented-out code below breaks Learn_it.box alignement (all ANSI Escapes are considered chars)
            # if i % 2 == 0:
            #     string = colored(string, attrs=["dark"])
            ret.append(string)

        return ret

    def icon(self, name:str, right_margin:int=0):
        return colored({
            'question': '?',
            'error'   : '✕',
            'success' : '✓',
            'info'    : 'i',
        }[name], {
            'question': 'blue',
            'error'   : 'red',
            'success' : 'green',
            'info'    : 'blue',
        }[name]) + ' ' * right_margin

    def aligned(self, string:str, align:str="center", width:int=0):
        if width == 0: width = len(string)

        if align == 'center':
            return '{:^{w}}'.format(string, w=width)
        elif align == 'right':
            return '{:>{w}}'.format(string, w=width)
        else:
            return '{:{w}}' .format(string, w=width)


    def box(self, content:str, color:str='white', pad:int=1, align:str="center", width:int=0, first_line_is_title:bool=True, margin:int=1):
        from math import ceil
        lines = content.split('\n')
        width = width or max(len(l) for l in lines)
        boxed = []
        if first_line_is_title:
            title = lines[0]
            lines = lines[1:] # Blank line jump + all other lines
            title = colored(title, 'cyan', attrs=['bold']) + ' '  * (width - len(title))

        boxed.append('╭' + '─' * (width+pad*2) + '╮')
        if first_line_is_title:
            boxed.append('│' + ' ' * pad + title + ' ' * pad + '│')
            boxed.append('│' + '-' * (width+pad*2) + '│')
        for l in lines: boxed.append('│' + ' ' * pad + self.aligned(l, align, width) + ' ' * pad + '│')
        boxed.append('╰' + '─' * (width+pad*2) + '╯')

        print('\n' * margin + '\n'.join(boxed) + '\n' * margin)

    def question_msg(self, *args, **kwargs):
        print(self.icon('question'), *args, **kwargs)
    def error_msg(self, *args, **kwargs):
        print(self.icon('error'), *args, **kwargs)
    def success_msg(self, *args, **kwargs):
        print(self.icon('success'), *args, **kwargs)

    # The same as idea as self.process_answer, except this runs every time on user input
    def normalize_answer(self, answer):
        import re
        lowered = str(answer).lower().strip()
        return re.sub(r'[  ]+', ' ', lowered) # Regular space & nbsp.

    def is_correct(self, user_answer, correct_answers):
        return self.normalize_answer(user_answer) in [self.normalize_answer(ans) for ans in correct_answers]

    def askloop(self, ask_for):
        import sys
        if ask_for == 'questions':
            askdata = self.get_flipped_askdata()
        else:
            askdata = self.askdata

        fails = list()
        for question, answers in askdata:
            whitespace = self.get_largest_key_length() - len(question)
            ask_sentence = self.get_ask_sentence(question) + ' ' * whitespace + " \033[1m\033[36m"
            self.question_msg(ask_sentence, end="")
            user_answer = input()

            sys.stdout.write('\033[0m\033[F')
            if self.is_correct(user_answer, answers):
                self.success_msg(ask_sentence + '\033[0m' + colored(user_answer, 'green'))
            else:
                fails.append(question)
                if self.mode == 'testing':
                    self.error_msg(ask_sentence + '\033[0m' + user_answer)
                else:
                    correct_answers = ' ou '.join(colored(ans, 'yellow') for ans in answers) + ' ' * len(user_answer)
                    censored_answers = colored('█' * len(', '.join(answers)), 'grey')
                    hide_timeout = self.flags['hide-timeout']

                    self.error_msg(ask_sentence + correct_answers)

                    if hide_timeout:
                        time.sleep(hide_timeout)
                    else:
                        input()
                        sys.stdout.write('\033[F')

                    sys.stdout.write('\033[F')
                    self.error_msg(ask_sentence + censored_answers)

        self.fails = fails

    def summary(self):
        fails = self.list_fails()
        if fails: 
            to_learn = 'To learn:\n'+'\n'.join(fails)
        else:
            to_learn = 'Nothing to learn'

        self.box(f"""{self.compute_score()}
{to_learn}""", align='left')
        

from yaspin import yaspin
def mainloop(file=None, mode=None, flags={}):
    if mode is None:
        while mode not in {'training', 'testing'}:
            mode = input("Mode ? (training|testing) >")

    learn_it = Learn_it(file, mode, **flags)
    with yaspin().white.arc as spinner:
        spinner.text = "Processing options..."
        learn_it.process_flags()
        spinner.text = "Processing data..."
        learn_it.process_askdata()
        spinner.text = "Processing done."
        spinner.ok(learn_it.icon('success', right_margin=1))

    learn_it.box(f"""{learn_it.flags['title']}
{'Files'}  {len(learn_it._datas)}
{'Items'}  {len(learn_it.askdata)}
{'Mode'}   {mode}ing""", align='left')

    if learn_it.flags['ask-for'] in {'answers', 'both'}:
        learn_it.askloop(ask_for='answers')
        learn_it.summary()

    if learn_it.flags['ask-for'] in {'questions', 'both'}:
        learn_it.askloop(ask_for='questions')
        print('Your score     : ' + learn_it.compute_score())
        fails = learn_it.list_fails()
        if fails: 
            print('Things to learn:\n\t'+'\n\t'.join(fails))
        else:
            print('Nothing to learn 😉')


if __name__ == "__main__":
    mainloop(file="./russe.yaml")
