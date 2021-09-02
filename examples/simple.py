"""This is a trivial example that does need any 3rd party dependencies."""
import pyreball as pb

pb.set_title("Simple report")

pb.print_h1("Heading")

pb.print_div(f"This is my div with {pb.bold('important')} text.")
