import pandas as pd

import pyreball as pb

df = pd.DataFrame(
    {
        "name": ["Bob", "Carol", "Alice", "Dave"],
        "age": [23, 5, 22, 54],
    }
)
pb.print_table(df, caption="Top caption.", caption_position="top")
pb.print_table(df, caption="Bottom caption.", caption_position="bottom")
