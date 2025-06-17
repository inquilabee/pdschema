def is_positive(x):
    return x > 0


def is_nonempty_string(x):
    return isinstance(x, str) and len(x.strip()) > 0
