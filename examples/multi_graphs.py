"""This example illustrates a multi-plot."""
import pandas as pd
import numpy as np
import altair as alt

import pyreball as pb

pb.set_title("Multi-graph Plots")

pb.print_h1("Data Preparation")

df1 = pd.DataFrame({'x': np.array([1, 2, 3]), 'y': np.array([4, 3, 6])})
df2 = pd.DataFrame({'x': np.array([1, 2, 3]), 'y': np.array([5, 3, 4])})
df3 = pd.DataFrame({'x': np.array([1, 2, 3]), 'y': np.array([1, 3, 3])})
pb.print_table(df1, caption="Data table 1.")
pb.print_table(df2, caption="Data table 2.")
pb.print_table(df3, caption="Data table 3.")


def prepare_altair_barchart(data):
    return alt.Chart(data).mark_bar().encode(
        x=alt.X('x', type='nominal', sort=None, title='x'),
        y=alt.Y('y', type='quantitative', title='y'),
        tooltip=['x', 'y']
    ).configure_axisX(
        labelAngle=-45
    ).properties(
        width=800,
        height=480,
    )


fig1 = prepare_altair_barchart(df1)
fig2 = prepare_altair_barchart(df2)
fig3 = prepare_altair_barchart(df3)

pb.print_h2("Three Plots")

pb.print_div(f"The plot below illustrates {pb.code('plot_multi_graph')} function. "
             f"Note that currently it's only a prototype. For example, it cannot use references.\n")
pb.print_html("<br>")

pb.plot_multi_graph([fig1, fig2, fig3], captions=["Altair barchart 1.", "Altair barchart 2.", "Altair barchart 3."])

pb.print_h2("Single Plot")

pb.plot_multi_graph([fig1], captions=["Altair barchart 1."])
