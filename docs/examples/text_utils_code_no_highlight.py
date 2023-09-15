import inspect

import pyreball as pb


def add(x, y):
    return x + y


pb.print(pb.code_block(inspect.getsource(add), syntax_highlight=None))
