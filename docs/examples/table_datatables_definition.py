import pandas as pd

import pyreball as pb

df = pd.DataFrame(
    [[row * 20 + col for col in range(20)] for row in range(40)],
    columns=[f"col_{i}" for i in range(20)],
)
datatables_definition = {
    "paging": False,
    "scrollCollapse": True,
    "scrollY": "400px",
    "searching": False,
    "order": [(1, "desc")],
}
pb.print_table(
    df,
    caption="Larger table with custom config.",
    datatables_definition=datatables_definition,
)
