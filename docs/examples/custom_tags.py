import pyreball as pb

pb.set_title("Custom Tags")

pb.print_html(pb.tag("Text displayed in a fixed-width font.", name="pre"))

hr_tag = pb.tag(name="hr")

pb.print_html(hr_tag)
