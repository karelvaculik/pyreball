import uuid

import altair as alt
import pandas as pd
import pyreball as pb

pb.set_title("Multi-figure Plots")

pb.print(
    """
<script>
    
    function next_fig(div_id, button_next_id, button_prev_id) {
        var qElems = document.querySelectorAll(div_id + '>div');
        for (var i = 0; i < qElems.length; i++) {
            if (qElems[i].style.display != 'none') {
                qElems[i].style.display = 'none';
                qElems[i + 1].style.display = 'block';
                if (i == qElems.length - 2) {
                    document.getElementById(button_next_id).disabled = true;
                }
                document.getElementById(button_prev_id).disabled = false;
                break;
            }
        }
    }

    function previous_fig(div_id, button_next_id, button_prev_id) {
        var qElems = document.querySelectorAll(div_id + '>div');
        for (var i = 0; i < qElems.length; i++) {
            if (qElems[i].style.display != 'none') {
                qElems[i].style.display = 'none';
                qElems[i - 1].style.display = 'block';
                if (i == 1) {
                    document.getElementById(button_prev_id).disabled = true;
                }
                document.getElementById(button_next_id).disabled = false;
                break;
            }
        }
    }

</script>
"""
)

df1 = pd.DataFrame({"x": [1, 2, 3], "y": [4, 3, 6]})
df2 = pd.DataFrame({"x": [1, 2, 3], "y": [5, 3, 4]})
df3 = pd.DataFrame({"x": [1, 2, 3], "y": [1, 3, 3]})


def prepare_altair_barchart(data):
    return (
        alt.Chart(data)
        .mark_bar()
        .encode(
            x=alt.X("x", type="nominal", sort=None, title="x"),
            y=alt.Y("y", type="quantitative", title="y"),
            tooltip=["x", "y"],
        )
        .configure_axisX(labelAngle=-45)
        .properties(
            width=400,
            height=300,
        )
    )


fig1 = prepare_altair_barchart(df1)
fig2 = prepare_altair_barchart(df2)
fig3 = prepare_altair_barchart(df3)


def print_multi_figure(figs, captions) -> None:
    multi_figure_id = uuid.uuid4()
    b_prev_id = f"button_prev_{multi_figure_id}"
    b_next_id = f"button_next_{multi_figure_id}"
    div_id = f"image-multi-panel-{multi_figure_id}"
    disable_next = "disabled " if len(figs) == 1 else ""

    button_prev_text = "&lt;"
    button_next_text = "&gt;"
    pb.print(
        f'<button id="{b_prev_id}" disabled onclick='
        f"\"previous_fig('#{div_id}', '{b_next_id}', '{b_prev_id}')\">"
        f"{button_prev_text}"
        "</button>"
    )
    pb.print(
        f'<button id="{b_next_id}" {disable_next}onclick='
        f"\"next_fig('#{div_id}', '{b_next_id}', '{b_prev_id}')\">"
        f"{button_next_text}"
        "</button>"
    )
    pb.print(f'<div id="{div_id}">')

    for i in range(len(figs)):
        if i > 0:
            pb.print('<div style="display: none;">')
        else:
            pb.print("<div>")
        pb.print_figure(fig=figs[i], caption=captions[i])
        pb.print("</div>")
    pb.print("</div>")


pb.print_h1("Three Plots")

print_multi_figure(
    [fig1, fig2, fig3],
    captions=["Barchart 1.", "Barchart 2.", "Barchart 3."],
)

pb.print_h1("Single Plot")

print_multi_figure([fig1], captions=["Barchart 1 again."])
