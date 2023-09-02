import inspect

import pyreball as pb


def add(x, y):
    return x + y


pb.print(f"The sum of {pb.code([1, 2, 3])} is {pb.code(sum([1, 2, 3]))}.")
pb.print(f"The source code of {pb.code('add')} function is:")
pb.print(pb.code_block(inspect.getsource(add)))
