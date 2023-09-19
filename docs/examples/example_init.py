import pyreball as pb

pb.set_title("Pyreball Illustration")

pb.print_div(
    "Pyreball has many features, among others:",
    pb.ulist(
        "Creating charts.",
        "Sortable and scrollable tables.",
        f'Basic text formatting such as {pb.em("emphasis")}.',
        f'Also {pb.link("hyperlinks", "https://www.python.org/")}.',
    ),
)
