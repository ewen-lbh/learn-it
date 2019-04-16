import random
import re
import shutil

from termcolor import cprint

DATA_FILE = 'learndata/russe.txt'
ANDLIST_SYNTAX = '<<AND>> '
FORMAT_NOT_SPECIFIED_MESSAGE : """
W: Format not specified, detecting automatically.
You should define it by adding %s at the start of the file.
"""



def handle_andlist(ans, v):
    if not re.match('^'+ANDLIST_SYNTAX, v, re.IGNORECASE):
        return ans == v

    v = v[len(ANDLIST_SYNTAX):]
    answers = {e:e for e in list(set(v.split(', ')))}
    answereds = {e:e for e in list(set(ans.split(', ')))}
    if len(answereds) > len(answers):
        cprint("Trop d'éléments", 'red')
        return False

    missings = list(dictdiff(plate=answers, delta=answereds).values())

    if len(missings):
        cprint("Il vous manque: \n"+"\n".join(missings), 'red')

    return not bool(len(missings))


def ask(k, v):
    ans = input(f"{ASK_SENTENCE.replace('<>', k)}\n>").strip()
    if RM_ALL_SPACES: ans = ans.replace(' ', '')
    if not CASE_SENSITIVE: ans = ans.lower()
    return handle_andlist(ans, v)


def notfound(k, v):
    cprint(f"{k} correspondait à {v}!", 'red')

def yesno(msg):
    return input(f"{msg}\n>").lower().strip().startswith('y')


def dictdiff(plate, delta):
    return {k: v for k, v in plate.items() if k not in delta.keys()}


def liststrip(iterable):
    if len(iterable) == 0:
        return iterable

    first = 0
    for i, e in enumerate(iterable):
        if bool(e):
            first = i
            break

    last = 0
    for i, e in reversed(list(enumerate(iterable))):
        if bool(e):
            last = i
            break

    return iterable[first:last + 1]


# todo!! accept or require multiple answers for one key
# |- eg. ||u||*||v||*cos(u;v) <and> xx'+yy'
# todo! accept regex patterns
# |- eg. ||[uv]||\*||[uv]||\*cos\([uv];[uv]\)
# todo!! add white & black lists

READ_DATA_FROM_FILE = True
RANDOMIZE_ASK_ORDER = True
RM_ALL_SPACES = False
ASK_SENTENCE = "<>"
CASE_SENSITIVE = False

# leave empty to disable whitelist
WHITELIST = []

mode = False
with open(DATA_FILE, 'r', encoding='utf8') as f:
    items = {}
    lines = []
    rawlines = f.read().replace('\ufeff', '').split('\n')

    # remove comments & empty lines at start & end
    # register format & sentence declarations

    for line in rawlines:
        sentence_patt = r'^--sentence (.+)'
        fmt_declaration_patt = r'^--format (.+)'
        if re.match(sentence_patt, line):
            ASK_SENTENCE = re.search(sentence_patt, line).group(1)

        elif re.match(fmt_declaration_patt, line):
            mode = re.search(fmt_declaration_patt, line).group(1)

        elif line.startswith(('#', '//')):
            continue
        else:
            lines.append(line)

    lines = liststrip(lines)

    fmt_notice_verb = 'found format declaration'
    if mode not in ('natural', 'reg', 'raw'):
        fmt_notice_verb = 'detected format'

        cprint(FORMAT_NOT_SPECIFIED_MESSAGE % fmt_declaration_patt[1:].replace('(.+)','<format>'))
        # determine file mode
        regpatt = r'"(.+)" *: *"(.+)",?'
        rawpatt = r'([^:]+):(.+)'

        mode = 'natural'
        for line in lines:
            if re.match(regpatt, line):
                mode = 'reg'
                break
            elif re.match(rawpatt, line):
                mode = 'raw'
                break

    print(f"{fmt_notice_verb} format for {DATA_FILE}: {mode}")

    for i, line in enumerate(lines):
        if i > 0:
            prevline = lines[i - 1]
        else:
            prevline = ''

        try:
            nextline = lines[i + 1]
        except IndexError:
            nextline = ''

        if mode == 'reg':
            k, v = re.search(regpatt, line).groups()

        elif mode == 'raw':
            colon_escape_temp_sub = "[" * 10 + "&colon;" + "]" * 10
            line = line.replace("\\:", colon_escape_temp_sub)
            k, v = re.search(rawpatt, line).groups()
            k = k.strip().replace(colon_escape_temp_sub, ':')
            v = v.strip()

        else:
            # if new item
            if not prevline:
                k = line
                v = nextline

            else:
                continue

        items[k] = v

DATA = items
if len(WHITELIST):
    DATA = {k: v for k, v in DATA.items() if k in WHITELIST}

if not CASE_SENSITIVE:
    DATA = {k.lower(): v.lower() for k, v in DATA.items()}

fromfile = 'from ' + str(DATA_FILE) if READ_DATA_FROM_FILE else ''
cprint(f"Successfully loaded {len(DATA)} item{'s' if len(DATA) else ''} {fromfile}", 'green')

separator_char = '-'

ctl_mode = yesno("Mode contrôle ?")
askfor_k = yesno("Demander les clés ?")
random_c = RANDOMIZE_ASK_ORDER


def action(k, v, notknown, mutate_notknown=True):
    if ask(k, v):
        cprint("Trouvé!", 'green')
        if mutate_notknown:
            notknown.pop(k)
        else:
            return True
    else:
        notfound(k, v)
        if not mutate_notknown:
            return False

    return notknown


def revdict(dikt):
    return {v: k for k, v in dikt.items()}


separator = separator_char * shutil.get_terminal_size((80, 20))[0]

if askfor_k:
    DATA = revdict(DATA)

if ctl_mode:
    note = 0
    notknown = {}
    access_order = list(DATA.keys())
    if random_c:
        random.shuffle(access_order)

    for k in access_order:
        v = DATA[k]
        if not action(k, v, notknown, mutate_notknown=False):
            notknown[k] = v

    known = dictdiff(DATA, notknown)
    grade = len(known) / len(DATA) * 20
    grade_treshold = 15
    print(separator)
    cprint(f"Ta note: {grade}/20 ({len(known)}/{len(DATA)})", ('red' if grade < grade_treshold else 'green'))
    if len(notknown):
        if len(notknown) > 1:
            cprint(f"Tu dois apprendres {len(notknown)} autres choses:", 'red')
        else:
            cprint("Tu dois encore apprendre:", 'red')
        maxlen = max([len(k) for k, v in notknown.items()])
        for k, v in notknown.items():
            spaces = ' ' * (maxlen - len(k))
            print(f"{k}{spaces} : {v}")

else:
    notknown = DATA
    initial_DATA_len = len(DATA)
    i = 0
    while len(notknown):
        if random_c:
            k = random.choice(list(notknown.keys()))
        else:
            k = notknown[list(notknown.keys())[i]]
            i += 1
        v = DATA[k]
        notknown = action(k, v, notknown)
        cprint(f"{initial_DATA_len - len(DATA)}/{initial_DATA_len}")
