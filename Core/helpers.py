def pprint_dict(data: dict, pad: int = 1, sep: str = ': ') -> None:
    maxlen = max([len(e) for e in data.keys()])
    for k, v in data.items():
        spaces = ' ' * (maxlen - len(k) + pad)
        print('{}{}{}{}'.format(k, spaces, sep, v))
