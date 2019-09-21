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

parser = argparse.ArgumentParser(description='Learn stuff efficiently with two different modes, to learn and validate your knowledge.')
parser.add_argument('command', choices=["test", "train", "extract"])
parser.add_argument('file', metavar='PATH')
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
