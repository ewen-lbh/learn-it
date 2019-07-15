import yaml
import random

class Learn_it:

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
    }

    FLAGS_KEY_NAME = 'flags'

    def __init__(self, file_path, **cli_flags):

        with open(file_path, 'r') as f:
            self._raw = f.read()
        self._data = yaml.load(self._raw, Loader=yaml.SafeLoader)
        self._flags = self._data[self.FLAGS_KEY_NAME]
        self._cli_flags = cli_flags

    def add_cli_flags(self):
        for flag, value in self._cli_flags.items():
            flag = flag.replace('_','-')
            self._flags[flag] = value

    def strip_flags(self):
        valid_flags = dict()
        for name, value in self._flags.items():
            # Flag name verification
            if name not in self._FLAGS.keys():
                continue

            # Check for values
            validator = self._FLAGS[name]
            if 'allow-types' in validator.keys():
                allowed_types = validator['allow-types']
                if type(value) not in allowed_types:
                    continue
            if 'allow-values' in validator.keys():
                allowed_values = validator['allow-values']
                if value not in allowed_values:
                    continue

            # if we've made it here, the flag is legit.
            valid_flags[name] = value

        self._flags = valid_flags

    def add_default_flags(self):
        new_flags = dict()
        for flag, flagdata in self._FLAGS.items():
            default_value = flagdata['default']
            if flag not in self._flags.keys():
                new_flags[flag] = default_value

        self._flags.update(new_flags)

    def process_flags(self):
        self.add_cli_flags()
        self.strip_flags()
        self.add_default_flags()

    def get_ask_sentence(self, asked):
        return self._flags['ask-sentence'].replace('<>', asked)

    def process_learndata(self):
        self._askdata = list()
        for question, answer in self._data.items():
            if question == self.FLAGS_KEY_NAME:
                continue

            if type(answer) is not list:
                answer = [answer]

            # remove duplicates while maintaining order
            from collections import OrderedDict
            answer = list(OrderedDict.fromkeys(answer))

            self._askdata.append(
                (question, answer)
            )

    def process_ask_for(self, ask_for=None):
        if ask_for is None:
            ask_for = self._flags['ask-for']
        
        # No need to do processing if we aren't going to change
        # anything.
        if ask_for not in ('both','questions'):
            return None

        flipped = list()
        for question, answers in self._askdata:
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

        if ask_for == 'questions':
            self._askdata = flipped

        elif ask_for == 'both':
            self._askdata += flipped

    def process_ask_order(self, ask_order=None):
        if ask_order is None:
            ask_order = self._flags['ask-order']

        if ask_order == 'random':
            random.shuffle(self._askdata)
        elif ask_order == 'inverted':
            self._askdata = list(reversed(self._askdata))
        elif ask_order == 'alphabetical':
            self._askdata = list(sorted(self._askdata))

    def process_askdata(self):
        self.add_cli_flags()
        self.strip_flags()
        self.add_default_flags()
        self.process_learndata()
        self.process_ask_for()
        self.process_ask_order()

    def compute_score(self, failed:int):
        max_val = self._flags['grade-max']
        ratio = failed / len(self._askdata)
        return '{grade:.1f}/{total}'.format(grade=ratio * max_val, total=max_val)

if __name__ == "__main__":
    learn_it = Learn_it('./learndata-example.yaml')
    learn_it.process_askdata()

    fails = list()
    for question, answers in learn_it._askdata:
        print(learn_it.get_ask_sentence(question))
        user_answer = input('>')

        if user_answer in answers:
            print('wohoo!')
        else:
            print('failed :/')
            fails.append(question)

    print(learn_it.compute_score(len(fails)))
    print('\n'.join([f'{q}:{a}' for q,a in learn_it._askdata if q in fails]))

    