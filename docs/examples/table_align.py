import pandas as pd

import pyreball as pb

df = pd.DataFrame(
    {
        "name": ["Bob", "Carol", "Alice", "Dave"],
        "age": [23, 5, 22, 54],
    }
)
pb.print_table(df, caption="Left align.", align="left")
pb.print_table(df, caption="Center align.", align="center")
pb.print_table(df, caption="Right align.", align="right")
