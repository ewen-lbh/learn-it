import yaml
import random
import os
from termcolor import colored


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
            'default': "What is <> ?",
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
    }

    FLAGS_KEY_NAME = 'flags'

    def __init__(self, file_path, mode, cli_flags):
        with open(file_path, 'r') as f:
            self._raw = f.read()
        self._data = yaml.load(self._raw, Loader=yaml.SafeLoader)
        self.flags = self._data[self.FLAGS_KEY_NAME]
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

    def process_flags(self):
        self.add_cli_flags()
        self.strip_flags()
        self.add_default_flags()

    # --------------------------
    # >  ASK DATA PROCESSING   <
    # --------------------------

    def process_learndata(self):
        self.askdata = list()
        for question, answer in self._data.items():
            if question == self.FLAGS_KEY_NAME:
                continue

            if type(answer) is not list:
                answer = [answer]

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
        max_len = max([len(e) for e in self.fails])
        def padding(k): return ' ' * (max_len - len(k))

        print_fmt = '{question}{padding}: {answer}'
        failed_items = {k: v for k, v in self.askdata if k in self.fails}
        ret = list()
        for i, (q, a) in enumerate(failed_items.items()):
            string = print_fmt.format(
                question=q, answer=self.format_answers_list(a), padding=padding(q))
            if i % 2 == 0:
                string = colored(string, attrs="dark")
            ret.append(string)

        return ret

    def askloop(self, ask_for):
        if ask_for == 'questions':
            askdata = self.get_flipped_askdata()
        else:
            askdata = self.askdata

        fails = list()
        for question, answers in askdata:
            print(self.get_ask_sentence(question))
            user_answer = input('>')

            if user_answer in answers:
                print(self.flags['success-sentence'])
            else:
                print(self.flags['fail-sentence'])
                if self.mode == 'training':
                    print(f"Correct answer(s): {answers}")
                fails.append(question)

        self.fails = fails


def mainloop(file=None, mode=None, flags={}):
    if mode is None:
        while mode not in {'training', 'testing'}:
            mode = input("Mode ? (training|testing) >")

    learn_it = Learn_it(file, mode, flags)
    learn_it.process_flags()
    learn_it.process_askdata()

    if learn_it.flags['ask-for'] in {'answers', 'both'}:
        learn_it.askloop(ask_for='answers')
        print('Your score     : ' + learn_it.compute_score())
        print('Things to learn:\n\t'+'\n\t'.join(learn_it.list_fails()))

    if learn_it.flags['ask-for'] in {'questions', 'both'}:
        learn_it.askloop(ask_for='questions')
        print('Your score     : ' + learn_it.compute_score())
        print('Things to learn:\n\t'+'\n\t'.join(learn_it.list_fails()))


if __name__ == "__main__":
    mainloop()
