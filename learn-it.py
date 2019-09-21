#!/usr/bin/python3
import subprocess
import sys
import os
import funcy
import argparse

try:
    import termcolor
    from termcolor import cprint
except ModuleNotFoundError:
    print('Trying to install dependencies automatically...')
    print('If this fails, install them manually by doing')
    print('pip3 install -r requirements.txt')
    print('\n' * 2)

    import subprocess
    import os.path

    requirements_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'requirements.txt'))
    subprocess.call(['pip3', 'install', '-r', requirements_path])

commands_help = """R|test: Ask about each item only once, and tell you what you got wrong at the end.
train: Ask you about every item until you've got them all right.
extract: Extract learndata from markdown or asciidoc definition lists"""

class SmartFormatter(argparse.HelpFormatter):
    def _split_lines(self, text, width):
        if text.startswith('R|'):
            return text[2:].splitlines()  
        # this is the RawTextHelpFormatter._split_lines
        return argparse.HelpFormatter._split_lines(self, text, width)

parser = argparse.ArgumentParser(description='Learn stuff efficiently with two different modes, to learn and validate your knowledge.', formatter_class=SmartFormatter)
parser.add_argument('command', choices=["test", "train", "extract"], help=commands_help)
parser.add_argument('file', metavar='PATH', help="The path of the file on which you will apply the command.")
parser.add_argument('-B','--no-blacklist', help='Bypass the blacklist and ask for everything.', action='store_true')
flags = parser.parse_args()

def custom_keyboardinterrupt_message(function):
    try:
        function()
    except KeyboardInterrupt:
        cprint("\nAnnulé", 'red')

if not os.path.isfile(flags.file):
    exit("The provided file does not exist.")

if flags.command == 'test':
    from main import mainloop
    custom_keyboardinterrupt_message(lambda: mainloop(flags.file, 'test', vars(flags)))

elif flags.command == 'train':
    from main import mainloop
    custom_keyboardinterrupt_message(lambda: mainloop(flags.file, 'train', vars(flags)))

elif flags.command == 'extract':
    from extract import Extractor
    extractor = Extractor(flags.file)
    extractor.extract()

else:
    exit('FUEEE! (Unreachable code)')
