import matplotlib.pyplot as plt
import pandas as pd
import pyreball as pb
import seaborn as sns

pb.set_title("Tables and Figures")

df = pd.DataFrame({"x": [1, 2, 3], "y": [4, 6, 5]})
pb.print_table(df, caption="A data table.")

fig, ax = plt.subplots()
sns.lineplot(x="x", y="y", ax=ax, data=df)
ax.set(xlabel="x", ylabel="y")
pb.print_figure(fig, caption="A line chart.")
