import altair as alt
import pandas as pd
import pyreball as pb

df = pd.DataFrame({"x": [1, 2, 3], "y": [4, 3, 6]})

fig = (
    alt.Chart(df)
    .mark_bar()
    .encode(
        x=alt.X(
            "x",
            type="nominal",
            sort=None,
            title="x",
            axis=alt.Axis(labelAngle=0),
        ),
        y=alt.Y("y", type="quantitative", title="y"),
        tooltip=["x", "y"],
    )
    .properties(
        width=540,
        height=400,
    )
)
pb.plot_graph(fig, caption="Vega-Altair barchart.")
