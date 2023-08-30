import pandas as pd
import pyreball as pb
from bokeh.models import ColumnDataSource, HoverTool
from bokeh.plotting import figure

df = pd.DataFrame({"x": [1, 2, 3], "y": [4, 3, 6]})
df["x"] = df["x"].astype(str)
fig = figure(x_range=df["x"])
fig.vbar(x="x", top="y", width=0.9, source=ColumnDataSource(data=df))
fig.add_tools(HoverTool(tooltips=[("x", "@x"), ("y", "@y")]))
pb.plot_graph(fig, caption="Bokeh barchart.")
