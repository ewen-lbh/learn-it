#!/usr/bin/python3
import subprocess
import sys
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

parser = argparse.ArgumentParser(description='Learn stuff efficiently with two different modes that acquire (training) or validate (testing) knowledge.')
parser.add_argument('file', metavar='PATH', default=None)
parser.add_argument('-B','--no-blacklist', help='Bypass the blacklist option and ask for everything.', action='store_true')
group = parser.add_mutually_exclusive_group()
group.add_argument('-T', '--test', help="Engage testing mode", action="store_true")
group.add_argument('-t', '--train', help="Engage training mode", action="store_true")
flags = parser.parse_args()

if flags.test:
    mode = 'testing'
elif flags.train:
    mode = 'training'
else:
    mode = None

from main import mainloop
try:
    mainloop(flags.file, mode, funcy.project(vars(flags), {'file','test','train'}))
except KeyboardInterrupt:
    cprint("\nAnnulé", 'red')
