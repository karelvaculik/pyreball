"""Simple report showing various features of Pyreball."""
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import pyreball as pb
import seaborn as sns

pb.set_title("Sample Report")

pb.print_h1("Displaying Texts")

pb.print("<div>We can always start inserting custom raw HTML code.</div>")
pb.print("<br>")
pb.print_div(
    "However, we can use special function to write text into a &lt;br&gt; element."
)
pb.print("<br>")
pb.print_div(
    "It is possible to pass several values and optionally a separator.",
    "The values will be joined and automatically converted to strings, as with the following number and list.",
    42,
    [11, 13, 19],
    "Newline characters can be converted to &lt;br&gt; elements by using replace_newlines_with_br parameter.",
    sep="\n",
)

pb.print_h2("Basic String-wrapping Formatting Functions")
pb.print_div(
    f"This is a text with {pb.bold('bold')} word and with {pb.em('emphasised')} word.",
    f"You can also use {pb.code('inline code formatting')}.",
)

pb.print_div(
    "In the previous section, we pasted string values on separate lines. "
    "Let's use lists instead:",
    pb.ulist(
        "Each argument is one element in the list",
        "We can even make nested lists as with the following ordered list:",
        pb.olist("First", "Second"),
        "And we can of course mix the lists:",
        pb.ulist("Nested list again, but now an unordered one."),
    ),
)

pb.print_h2("Other Special Functions")
pb.print_div(
    f"We can also add a link to {pb.link('Python documentation', 'https://www.python.org/doc/')} "
    f"if necessary. Talking about links, note that each heading has a clickable anchor."
)
pb.print("<br>")
pb.print_div(
    f"We already used {pb.code('code')} function for inline formatting. There is also {pb.code('print_code')} "
    f"function that creates a text block formatted as code, "
    f"which can be useful when we want to print various data structures, such as matrices:"
)

np.random.seed(1)
array = np.random.random((3, 3))
pb.print_code_block(str(array))

pb.print_div("... or even a piece of code:")


def factorial(n):
    result = 1
    for i in range(1, n + 1):
        result *= i
    return result


import inspect

pb.print_code_block(inspect.getsource(factorial))

pb.print_div(
    f"Before going further, let's return to the very first function we used: {pb.code('set_title')}. "
    f"As the name suggests, it sets the title of the HTML page. It is optional and can be actually placed "
    f"in any part of the report."
)

pb.print_h1("Inspecting Data")

pb.print_h2("Tables and Plots")

# Print a table
N = 10
df = pd.DataFrame({"x": np.arange(1, N + 1), "y": np.random.random(N) * 4 + 3})
pb.print_table(df, caption="A data table.", index=False)

# Plot a graph
fig, ax = plt.subplots()
sns.lineplot(x="x", y="y", ax=ax, data=df)
ax.set(xlabel="x", ylabel="y")
pb.plot_graph(fig, caption="The first plot.")

pb.print_h2("References to Plots and Tables")

# Creating a reference to a graph and a table:
img_reference = pb.Reference()
table_ref = pb.Reference()
pb.print_div(
    f"It is also possible to create references to tables and figures. "
    f"For example Table {table_ref} shows sortable columns and Fig. {img_reference} displays a scatterplot."
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
fig, ax = plt.subplots()
sns.scatterplot(x="x", y="y", ax=ax, data=df)
ax.set(xlabel="x", ylabel="y")
pb.plot_graph(fig, caption="A plot with a reference.", reference=img_reference)


pb.print_div(
    f"Note that you can use the references in your text multiple times, "
    f"see again the reference to Table {table_ref} and Fig. {img_reference}. "
    f"Of course, we cannot use a single reference for multiple tables or figures."
)
