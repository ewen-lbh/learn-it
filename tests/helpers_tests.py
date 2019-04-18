from helpers import *

def test_strip_list_normal():
    return strip_list(['', None, '', 'hello','', 'world', '', False, '']) == ['hello', '' ,'world']


def test_strip_list_empty_list():
    return strip_list([False, '']) == []



if __name__ == '__main__':
    tests = {k.replace('test_', ''): v for k, v in globals().items() if k.startswith('test_')}
    faileds = []
    passeds = []
    for testname, test in tests.items():
        if test():
            print('.', end='')
            passeds.append(testname)
        else:
            print('F', end='')
            faileds.append(testname)
    print('')
    if not len(faileds):
        print('No fails :D')
    else:
        print(f'{len(faileds)} test{"s" if len(faileds) != 1 else ""} failed:')
    for fail in faileds:
        print(f'{fail}')

