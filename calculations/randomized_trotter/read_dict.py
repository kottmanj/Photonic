def read_dictionary(filename:str, d:dict=None):
    if d is None:
        d = {}
    with open(filename, 'r') as f:
        for line in f:
            (key, val) = line.split()
            d[str(key)] = int(val)

    return d

