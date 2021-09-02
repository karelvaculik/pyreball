"""This report shows how to work with larger tables."""
import pandas as pd
import numpy as np

import pyreball as pb

pb.set_title("Large Tables Report")

# Print headers
pb.print_h1(f"Illustration of {pb.code('full_table')} parameter.")

pb.print_div("Note that the second table is not shown whole and is therefore scrollable.")

# Print a table
df = pd.DataFrame({'x': np.arange(0, 20), 'y': np.arange(100, 120)})

pb.print_table(df, caption="Data table with full_table=True.", full_table=True)

pb.print_table(df, caption="Data table with full_table=False.", full_table=False)

small_df = pd.DataFrame({'x': np.arange(0, 10), 'y': np.arange(100, 110)})

pb.print_table(small_df, caption="Small data table with full_table=True.", full_table=True)

pb.print_table(small_df, caption="Small data table with full_table=False.", full_table=False)
