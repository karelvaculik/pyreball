import inspect

import pyreball as pb


def add(x, y):
    return x + y


code_str = inspect.getsource(add)
pb.print_code_block(
    code_str, caption="My first function.", caption_position="top", align="left"
)
pb.print_code_block(code_str, numbered=False)
pb.print_code_block(
    code_str,
    caption="Third Time's the Charm.",
    caption_position="bottom",
    align="right",
    numbered=False,
)
