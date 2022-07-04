def save_labber_file(
    parent_file=None, path=None, name=None, parameter=None, number=None, overwrite=False
):
    import os

    def _get_file_tail_and_head_from_path(path):
        head, tail_filetype = os.path.split(path)
        tail, filetype = os.path.splitext(tail_filetype)
        return head, tail, filetype

    def _uniquify(path):
        filename, extension = os.path.splitext(path)
        counter = 1

        while os.path.exists(path):
            path = f"{filename}_{str(counter)}{extension}"
            counter += 1

        return path

    if parent_file:
        parent_head, parent_tail, parent_filetype = _get_file_tail_and_head_from_path(
            parent_file
        )

    # Headpath
    if path:
        path_head = path
    else:
        path_head = f"{parent_head}/{parent_tail}_files/"

    if not os.path.isdir(path_head):
        os.makedirs(path_head)

    # Filename
    if name:
        filename = name
    else:
        filename = parent_tail

    if parameter:
        parameter = f"_{parameter}"
    else:
        parameter = ""

    if number:
        number = f"_{number}"
    else:
        number = ""

    full_path = f"{path_head}/{filename}{parameter}{number}{parent_filetype}"

    if overwrite:
        return full_path
    else:
        return _uniquify(full_path)


def print_all_done(statement):
    all_done = '"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""\n                          ALL DONE!\n"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""\n'
    print(all_done)
    print(statement, "\n")
    print(all_done)


def round_on_error(value, error):
    import math

    significant_digits = 10 ** math.floor(math.log(error, 10))
    return value // significant_digits * significant_digits


def prettyprint(x, baseunit):
    import decimal

    prefix = "yzafpnµm kMGTPEZY"
    shift = decimal.Decimal("1E24")

    d = (decimal.Decimal(str(x)) * shift).normalize()
    m, e = d.to_eng_string().split("E")
    return f"{m} {prefix[int(e)//3]}{baseunit}"


if __name__ == "__main__":
    parent_file = "/Users/malthenielsen/Desktop/test/q5_SS_drive_onoff_19_test.hdf5"
    path = save_labber_file(
        parent_file=parent_file, parameter="param", number=10, overwrite=False
    )

    import os

    os.makedirs(path)
