import pyreball as pb

pb.print(
    "Text with a ",
    pb.a("link", attrs={"href": "https://www.python.org/"}),
    " to the Python homepage.",
)
