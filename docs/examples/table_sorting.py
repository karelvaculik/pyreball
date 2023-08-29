import pandas as pd

import pyreball as pb

df = pd.DataFrame(
    {
        "name": ["Bob", "Carol", "Alice", "Dave"],
        "age": [23, 5, 22, 54],
    }
)
pb.print_table(df, caption="Sortable table", sortable=True)
pb.print_table(
    df,
    caption="Table sorted by name (ASC).",
    sorting_definition=("name", "asc"),
)
pb.print_table(
    df,
    caption="Table sorted by age (DESC).",
    sorting_definition=("age", "desc"),
)
