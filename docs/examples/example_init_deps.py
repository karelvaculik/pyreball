import matplotlib.pyplot as plt
import pandas as pd
import pyreball as pb
import seaborn as sns

pb.set_title("Tables and Plots")

# Print a table
df = pd.DataFrame({"x": [1, 2, 3], "y": [4, 6, 5]})
pb.print_table(df, caption="A data table.")

# Plot a graph
fig, ax = plt.subplots()
sns.lineplot(x="x", y="y", ax=ax, data=df)
ax.set(xlabel="x", ylabel="y")
pb.plot_graph(fig, caption="A line plot.")
