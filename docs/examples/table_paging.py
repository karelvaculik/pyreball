import pandas as pd

import pyreball as pb

df = pd.DataFrame(
    [[row * 20 + col for col in range(20)] for row in range(40)],
    columns=[f"col_{i}" for i in range(20)],
)
pb.print_table(
    df,
    caption="Larger table with paging.",
    display_option="paging",
    paging_sizes=[5, 10, "All"],
)
