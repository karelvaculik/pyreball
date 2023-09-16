import pandas as pd
import pyreball as pb

df = pd.DataFrame(
    {
        "name": ["Bob", "Carol", "Alice", "Dave"],
        "age": [23, 5, 22, 54],
    },
    index=[1, 10, 100, 1000],
)
pb.print_table(df, caption="Default alignment.")
pb.print_table(df, caption="Identical alignment.", col_align="left")
pb.print_table(
    df,
    caption="Heterogeneous alignment.",
    col_align=["center", "right", "left"],
)
