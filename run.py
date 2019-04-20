import subprocess
import sys

try:
    import termcolor
except ModuleNotFoundError:
    print('Trying to install dependencies automatically...')
    print('If this fails, install them manually by doing')
    print('pip3 install -r requirements.txt')
    print('\n' * 2)

    import subprocess
    import os.path

    requirements_path = os.path.abspath(os.path.join(os.getcwd(), 'requirements.txt'))
    subprocess.call(['pip3', 'install', '-r', requirements_path])

from src.main import main
from src.consts import DATA_FILE

if len(sys.argv) > 1:
    if sys.argv[1] == 'edit':
        subprocess.call(['vim', DATA_FILE])
main()
