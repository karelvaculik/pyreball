import pandas as pd

import pyreball as pb

df = pd.DataFrame(
    {
        "name": ["Bob", "Carol", "Alice", "Dave"],
        "age": [23, 5, 22, 54],
    }
)
pb.print_table(
    df,
    caption="Style set to 'compact'.",
    datatables_style="compact",
)
pb.print_table(
    df,
    caption="Style set to 'compact' and 'display'.",
    datatables_style=["compact", "display"],
)
