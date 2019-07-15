import subprocess
import sys

from src import helpers
import argparse

try:
    import termcolor
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
parser.add_argument('file', metavar='PATH', nargs='?', default=None)
parser.add_argument('-B','--no-blacklist', help='Bypass --blacklist and ask for everything.', action='store_true')
flags = parser.parse_args()

main(flags.file, {k:v for k,v in var(flags) if k != 'file'})
