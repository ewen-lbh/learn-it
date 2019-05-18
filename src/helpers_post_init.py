from src.helpers import cprint
from src.consts import TIME_TO_READ_LETTER, T
import os
import time

def clear_screen(wait=True, mode='confirm', delay=5):
    if wait:
        if mode == 'confirm':
            input(T['press_enter_to_continue'])  # press enter to get to the next ask
        elif mode == 'delay':
            time.sleep(delay)
        else:
            cprint(f"Unreachable code! helpers_post_init.clear_screen's 'mode' argument is set to {mode}", 'red')
    os.system('clear')

def get_reading_time(word, time_to_read_letter=TIME_TO_READ_LETTER, time_to_learn_word=2):
    # ignore whitespace
    word = word.replace(' ','')
    # time to read word + learn it
    return time_to_read_letter * len(word) + time_to_learn_word