from src.helpers import cprint

from src.consts import *


def yesno(msg) -> bool:
    return input('(y/n) ' + msg + '\n>').lower().strip().startswith(('y','ы','я'))


def get_ans(asked, answer, flags) -> bool:
    def ask(asked):
        sentence = flags.ask_sentence.replace('<>', asked)
        return input(sentence + '\n>') if not AUTO_ANSWER else ''

    # ans is the *user's* answer
    # answer is the *correct* answer
    ans = ask(asked).strip()

    if not flags.case_sensitive:
        ans = ans.lower()
        answer = answer.lower()

    if ans == answer:
        return True
    else:
        if flags.ask_for_typos and not AUTO_ANSWER and ans:
            if yesno("Was this a typo ?"):
                return get_ans(asked, answer, flags)
        return False


def selection(msg: str, choices: list or tuple, shortcuts=True, shortcuts_level: int = 1) -> str:
    """
    Ask the user to select a choice in a given choices list. This is NOT case sensitive.
    :param msg: message to display.
    The list of choices is generated automatically, insert it in your message by adding "<choices>" in it.
    :param choices: list of choices to choose from
    :param shortcuts: whether to use shortcuts or not
    :param shortcuts_level: shortcuts lengths (>= 1)
    This is useful when your choices list have choices that start with the same letter(s)
    :return: a string that is in choices
    """

    # todo auto-detect shortcuts_level

    if shortcuts_level < 1: shortcuts_level = 1

    # HANDLING SHORTCUTS {
    if shortcuts:
        shortcuts_map = {choice[:shortcuts_level].lower(): choice for choice in choices}
        # remove duplicates from the list of shortcuts, and get the length
        deduped = list(set(list(shortcuts_map.keys())))
        # see if shortcuts are unambiguous by seeing if we removed any duplicates
        # if we removed any, the deduplicated list is shorter than the original shortcut map
        # this will also be considered ambiguous if deduped_len is greater than original_len, tho
        # this case should be unreachable.
        ambiguous_shortcuts = len(choices) != len(deduped)
        # if shortcuts are indeed ambiguous, use numbers instead, starting at one.
        if ambiguous_shortcuts:
            shortcuts_map = {str(i + 1): choice for i, choice in enumerate(choices)}
    else:
        shortcuts_map = {choice: choice for choice in choices}
    # }

    # HANDLING INPUT MESSAGE {
    choicelist = list()
    for shortcut, choice in shortcuts_map.items():
        if not shortcuts:
            choicelist.append('- {}'.format(choice))
        elif ambiguous_shortcuts:
            choicelist.append('{}: {}'.format(shortcut, choice))
        else:
            choicelist.append('[{}]{}'.format(shortcut.upper(), choice[len(shortcut):]))

    msg = msg.replace('<choices>', '\n'.join(choicelist)) + '\n>'
    # }

    ans = input(msg).strip().lower()
    while ans not in [e.lower() for e in shortcuts_map.keys()]:
        cprint('"{}" is not a valid choice. Please try again'.format(ans), 'red')
        ans = input('>').strip().lower()

    return shortcuts_map[ans]
