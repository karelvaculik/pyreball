import inspect

import pyreball as pb


def add(x, y):
    return x + y


pb.print("An example of a source code printed in HTML:")
pb.print_code_block(inspect.getsource(add))
