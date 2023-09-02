import pyreball as pb

pb.print(
    pb.div("Centered block of text", cl="text-centered"),
    pb.div(
        "Highlighted block of text",
        "<br>",
        "Another line",
        attrs={"style": "background-color: yellow;"},
        sep="\n",
    ),
    sep="\n",
)
