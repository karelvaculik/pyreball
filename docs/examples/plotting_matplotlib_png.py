import matplotlib.pyplot as plt

import pyreball as pb

fig, ax = plt.subplots()
plt.bar([1, 2, 3], [4, 3, 6])
plt.xlabel("x")
plt.ylabel("y")
pb.print_figure(
    fig,
    caption="Matplotlib barchart as png.",
    matplotlib_format="png",
    embedded=False,
)
