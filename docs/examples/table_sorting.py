import pandas as pd

import pyreball as pb

df = pd.DataFrame(
    {
        "name": ["Bob", "Carol", "Alice", "Dave", "Alice"],
        "age": [23, 5, 2, 54, 18],
    }
)
pb.print_table(df, caption="Sortable table", sortable=True)
pb.print_table(
    df,
    caption="Table sorted by age (ASC).",
    sorting_definition=[(df.columns.get_loc("age") + 1, "asc")],
)
pb.print_table(
    df,
    caption="Table sorted by name (ASC) and age (DESC).",
    sorting_definition=[(1, "asc"), (2, "desc")],
)
pb.print_table(
    df,
    caption="The same table, but without the index.",
    index=False,
    sorting_definition=[(0, "asc"), (1, "desc")],
)
