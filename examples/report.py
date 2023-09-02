"""Simple report showing various features of Pyreball."""
import matplotlib.pyplot as plt
import pandas as pd
import pyreball as pb
import seaborn as sns

pb.set_title("Pyreball Illustration")

pb.print_h1("Introduction")

pb.print_div(
    "Pyreball has many features, among others:",
    pb.ulist(
        "Plots in altair, plotly, bokeh, and matplotlib (and thus also seaborn etc.).",
        "Sortable and scrollable tables from pandas DataFrame.",
        f'Basic text formatting such as {pb.bold("headings")}, {pb.em("emphasis")}, and {pb.code("lists")}.',
        f'{pb.link("hyperlinks", "https://www.python.org/")}, references and table of contents.',
    ),
)

pb.print_h1("Tables and Plots")

# Print a table
df = pd.DataFrame({"x": [1, 2, 3], "y": [4, 6, 5]})
pb.print_table(df, caption="A data table.")

# Plot a graph
fig, ax = plt.subplots()
sns.lineplot(x="x", y="y", ax=ax, data=df)
ax.set(xlabel="x", ylabel="y")
pb.plot_graph(fig, caption="The first plot.")
