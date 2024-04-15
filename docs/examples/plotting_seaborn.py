import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

import pyreball as pb

df = pd.DataFrame({"x": [1, 2, 3], "y": [4, 3, 6]})

fig, ax = plt.subplots()
sns.barplot(x="x", y="y", data=df, ax=ax, color=sns.xkcd_rgb["windows blue"])
ax.set(xlabel="x", ylabel="y")
pb.print_figure(
    fig,
    caption="Seaborn barchart as png.",
    matplotlib_format="png",
    embedded=False,
)
