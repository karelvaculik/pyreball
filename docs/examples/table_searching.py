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
    caption="Table with a search box.",
    search_box=True,
)
