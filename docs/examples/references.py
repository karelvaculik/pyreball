import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import pyreball as pb
import seaborn as sns

pb.set_title("References to Figures and Tables")

ref_ch_1 = pb.Reference()

pb.print_h1("Tables", reference=ref_ch_1)

N = 10
np.random.seed(1)
df = pd.DataFrame({"x": np.arange(1, N + 1), "y": np.random.random(N) * 4 + 3})
pb.print_table(df, caption="A data table.", index=False)

img_reference = pb.Reference()
table_ref = pb.Reference()
pb.print_div(
    f"It is also possible to create references to tables and figures. "
    f"For example Table {table_ref} shows sortable columns and "
    f"Fig. {img_reference} displays a scatterplot. "
    f"Each reference has a default text to be displayed, "
    f"but this text can be overriden by using {pb.code('__call__()')} "
    f"method on the reference when pasting it into the text. "
    f"For example, here is a link to {img_reference('Scatterplot')}."
)
pb.print_table(
    df,
    caption="A sortable table with a reference",
    reference=table_ref,
    sortable=True,
    index=False,
)

pb.print_table(
    df,
    caption="A table sorted by y column",
    sorting_definition=[(df.columns.get_loc("y"), "asc")],
    index=False,
)

pb.print_h1("Charts")

fig, ax = plt.subplots()
sns.scatterplot(x="x", y="y", ax=ax, data=df)
ax.set(xlabel="x", ylabel="y")
pb.print_figure(fig, caption="A figure with a reference.", reference=img_reference)

pb.print_div(
    f"Note that you can use the references in your text multiple times, "
    f"see again the reference to Table {table_ref} and Fig. {img_reference}. "
    f"Of course, we cannot assign a single reference to multiple tables or figures. "
    f"Last, but not least, one can use reference to Chapter {ref_ch_1}. "
    f"Again, we can override the text and create a link to {ref_ch_1('First Chapter')}."
)
