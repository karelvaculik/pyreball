import pyreball as pb

pb.set_title("Custom Tags")

pb.print(pb.tag("Text displayed in a fixed-width font.", name="pre"))
hr_tag = pb.tag(name="hr", paired=False)
pb.print(hr_tag)
