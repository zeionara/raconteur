def one_is_not_none(message: str, *args: str):
    n_args = 0
    last_index = None

    for i, arg in enumerate(args):
        if arg is not None:
            n_args += 1
            last_index = i

    assert n_args == 1, message

    return last_index
