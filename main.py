import random
import collections
import re
from termcolor import cprint, colored

DATA_FILE = 'learndata/russe.txt'
SYNTAX = {
    'flags': r'--([\w\-]+) (\w+)'
}
# flag-name: default value
AVAILABLE_FLAGS = {
    'whitelist': [],
    'ask-sentence':'<>',
    'case-sensitive':False,
    'ask-for':'values',
    'ask-order':'random',
    'ask-for-typos':False
}

def parse(lines:list) -> tuple:

    def parse_flags(lines):
        def _list(flag_val:str) -> list:
            _list = str[1:-1].split(',')
            return [e.strip() for e in _list]

        patt = re.compile(SYNTAX['flags'])
        flags = dict()
        other_lines = list()
        for line in lines:
            if patt.match(line):
                flag = patt.search(line).group(1)
                val  = patt.search(line).group(2)
                # automatic types
                if val.lower() in ('true','false'):
                    val = bool(val)
                elif val.startswith('[') and val.endswith(']'):
                    val = _list(val)

                flags[flag] = val
            else:
                other_lines.append(line)
        return flags, other_lines

    def cleanup(lines:list):
        # removes comments and ending \n in lines list
        ret = list()
        for line in lines:
            line.replace('\\n','')
            if not line.startswith(('#','//')):
                ret.append(line)
        return ret

    def parse_data(lines:list):
        data = dict()
        for i, line in enumerate(lines):
            if i > 0:
                prevline = lines[i-1]
            else:
                prevline = ''
            try:
                nextline = lines[i+1]
            except IndexError:
                nextline = ''

            if not prevline:
                data[line] = nextline
            else:
                continue
        return data
    
    print('--RAW--')
    for line in lines:print(line)
    
    lines = cleanup(lines)
    print('--CLEANED--')
    for line in lines:print(line)
    
    flags, lines = parse_flags(lines)
    print('--PARSED--')
    data = parse_data(lines)
    for k, v in data.items():
        print(f'{k}:{v}')
    return data, flags
        
def parse_file(filepath:str) -> tuple:
    with open(filepath, 'r', encoding='utf8') as f:
        lines = f.readlines()
    return parse(lines)

class FlagsParser:
    def __init__(self, flags:dict):
        real_flags = dict()
        for flag, default in AVAILABLE_FLAGS.items():
            real_flags[flag] = flags.get(flag, default)

        for flag, val in real_flags.items():
            setattr(self, flag.replace('-','_'), val)

def handle_flags(data, flags:object):
    # --case-sensitive
    if not flags.case_sensitive:
        data = {k.lower():v.lower() for k, v in data.items()}
    
    # --whitelist
    if len(flags.whitelist):
        data = {k:v for k, v in data.items() if k in flags.whitelist}

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
    return input(msg+'\n(y/n)>').lower().strip().startswith('y')

def get_ans(asked, answer, flags) -> bool:
    def ask(asked):
        sentence = flags.ask_sentence.replace('<>',asked)
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

def mainloop(data, flags) -> None:
    for asked, answer in data.items():
        if get_ans(asked, answer, flags):
            cprint("Trouvé !","green")
        else:
            cprint("La réponse était : {}".format(answer), 'red')


def main():
    DATA, FLAGS = parse_file(DATA_FILE)
    FLAGS = FlagsParser(FLAGS)
    DATA  = handle_flags(DATA, FLAGS)
    print('===FLAGS===')
    print(FLAGS)
    print('===DATA===')
    print(DATA)
    mainloop(DATA, FLAGS)

if __name__ == '__main__':
    main()