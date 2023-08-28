import pyreball as pb

pb.set_title("Pyreball Illustration")

pb.print_div(
    "Pyreball has many features, among others:",
    pb.ulist(
        "Plots in altair, plotly, bokeh, and matplotlib (and thus also seaborn etc.).",
        "Sortable and scrollable tables from pandas DataFrame.",
        f'Basic text formatting such as {pb.bold("headings")}, {pb.em("emphasis")}, and {pb.code("lists")}.',
        f'{pb.link("hyperlinks", "https://www.python.org/")}, references and table of contents.',
    ),
)
