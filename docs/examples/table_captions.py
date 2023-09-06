import pandas as pd
import pyreball as pb

df = pd.DataFrame(
    {
        "name": ["Bob", "Carol", "Alice", "Dave"],
        "age": [23, 5, 22, 54],
    }
)
pb.print_table(df, caption="People with their age.")
pb.print_table(df, caption="People with their age.", numbered=False)
pb.print_table(df, numbered=False)
pb.print_table(
    df,
    caption="The table with numbering again. But much bigger caption.",
)
