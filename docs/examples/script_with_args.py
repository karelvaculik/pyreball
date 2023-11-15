import argparse

import pyreball as pb

pb.set_title("Custom Arguments")

# based on https://docs.python.org/3/library/argparse.html#example
parser = argparse.ArgumentParser(description="Process some integers.")
parser.add_argument(
    "integers",
    metavar="N",
    type=int,
    nargs="+",
    help="an integer for the accumulator",
)
parser.add_argument(
    "--sum",
    dest="accumulate",
    action="store_const",
    const=sum,
    default=max,
    help="sum the integers (default: find the max)",
)

args = parser.parse_args()
pb.print_div(
    f"The {args.accumulate.__name__} of the arg values is "
    f"{args.accumulate(args.integers)}."
)
