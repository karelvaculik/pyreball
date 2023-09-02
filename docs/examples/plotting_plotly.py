import pandas as pd
import plotly.express as px
import pyreball as pb

df = pd.DataFrame({"x": [1, 2, 3], "y": [4, 3, 6]})

fig = px.bar(df, x="x", y="y")
pb.plot_graph(fig, caption="Plotly graph.")
