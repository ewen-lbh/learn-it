def pprint_dict(data: dict, pad: int = 1, sep: str = ': ', column_names: tuple = None, return_str: bool = False):
    k_maxlen = max([len(str(e)) for e in data.keys()])
    v_maxlen = max([len(str(e)) for e in data.values()])
    ret = list()

    data = list(data.items())
    if column_names:
        data.insert(0, column_names)
        data.insert(1, ('-' * k_maxlen, '-' * v_maxlen))

    for k, v in data:
        spaces = ' ' * (k_maxlen - len(k) + pad)
        if return_str:
            ret.append(f'{k}{spaces}{sep}{v}')
        else:
            print(k, spaces, sep, v, sep='')

    if return_str: return '\n'.join(ret)


def strip_list(iterable: list) -> list:
    def _partial_strip(iterable: list) -> list:
        while iterable and not iterable[-1]:
            iterable.pop()
        return iterable

    iterable = _partial_strip(iterable)
    iterable = list(reversed(_partial_strip(list(reversed(iterable)))))

    return iterable
