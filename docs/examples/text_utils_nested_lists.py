import pyreball as pb

pb.print(
    "Nested list: ",
    pb.ulist(
        "A",
        (
            "B",
            pb.olist("X", "Y"),
        ),
        (
            "C",
            pb.ulist("Z"),
        ),
        (
            "D",
            "",
        ),
    ),
)
