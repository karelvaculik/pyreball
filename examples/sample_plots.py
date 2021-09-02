"""This example shows different libraries used for plotting."""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import altair as alt
import plotly.express as px
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource

import pyreball as pb

pb.set_title("Sample Plots")

pb.print_div("All supported plots are embedded directly into the final HTML file, except matplotllib plots "
             "with png format. For such plots, a folder with png images is created.")

df = pd.DataFrame({'x': np.array([1, 2, 3]), 'y': np.array([4, 3, 6])})
pb.print_table(df, caption="Data table.")

# seaborn
fig, ax = plt.subplots()
sns.barplot(x='x', y='y', data=df, ax=ax, color=sns.xkcd_rgb["windows blue"])
ax.set(xlabel='x', ylabel='y')
pb.plot_graph(fig, caption="Seaborn barchart as png.", matplotlib_format="png", embedded=False)

fig, ax = plt.subplots()
sns.barplot(x='x', y='y', data=df, ax=ax, color=sns.xkcd_rgb["windows blue"])
ax.set(xlabel='x', ylabel='y')
pb.plot_graph(fig, caption="Seaborn barchart as embedded svg.")

# altair
fig = alt.Chart(df).mark_bar().encode(
    x=alt.X('x', type='nominal', sort=None, title='x'),
    y=alt.Y('y', type='quantitative', title='y'),
    tooltip=['x', 'y']
).configure_axisX(
    labelAngle=-45
).properties(
    width=800,
    height=480,
)
pb.plot_graph(fig, caption="Altair barchart.")

# plotly
fig = px.bar(df, x='x', y='y')
pb.plot_graph(fig, caption="Plotly graph.")

# bokeh
df_bokeh = df.copy()
df_bokeh['x'] = df_bokeh['x'].astype(str)
fig = figure(x_range=df_bokeh['x'])
fig.vbar(x='x', top='y', width=0.9, source=ColumnDataSource(data=df_bokeh))
pb.plot_graph(fig, caption="Bokeh barchart.")
