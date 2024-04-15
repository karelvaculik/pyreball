import pandas as pd

import pyreball as pb

df = pd.DataFrame(
    [
        ("Bob", 2, 12, 23, 49),
        ("Carol", 54, 42, 2, 4),
        ("Alice", 20, 4, 18, 19),
        ("Dave", 42, 21, 43, 23),
        ("Eve", 7, 12, 55, 6),
        ("Frank", 1, 5, 48, 38),
    ],
    columns=pd.MultiIndex.from_tuples(
        [
            ("name", ""),
            ("current", "x"),
            ("current", "y"),
            ("previous", "x"),
            ("previous", "y"),
        ],
    ),
    index=pd.MultiIndex.from_tuples(
        [
            ("red", "dev"),
            ("red", "dev"),
            ("red", "qa"),
            ("blue", "dev"),
            ("blue", "dev"),
            ("blue", "qa"),
        ],
        names=["team", "role"],
    ),
)

pb.print_table(
    df,
    caption="With index.",
    sorting_definition=[(2, "asc")],
)
pb.print_table(
    df.reset_index(),
    caption="Without index.",
    index=False,
    sorting_definition=[(2, "asc")],
)
