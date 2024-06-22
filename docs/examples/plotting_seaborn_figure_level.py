import seaborn as sns

import pyreball as pb

tips = sns.load_dataset("tips")
anscombe = sns.load_dataset("anscombe")
penguins = sns.load_dataset("penguins")

fig_facet_grid_lmplot = sns.lmplot(data=penguins, x="bill_length_mm", y="bill_depth_mm")
pb.print_figure(
    fig_facet_grid_lmplot,
    caption="Seaborn FacetGrid from lmplot.",
    matplotlib_format="png",
    embedded=False,
)

fig_facet_grid = sns.FacetGrid(tips, col="time", row="sex")
fig_facet_grid.map(sns.scatterplot, "total_bill", "tip")
pb.print_figure(
    fig_facet_grid,
    caption="Seaborn FacetGrid.",
    matplotlib_format="png",
    embedded=False,
)

fig_pair_grid = sns.PairGrid(penguins)
fig_pair_grid.map(sns.scatterplot)
pb.print_figure(
    fig_pair_grid,
    caption="Seaborn PairGrid.",
    matplotlib_format="png",
    embedded=False,
)

fig_joint_grid = sns.JointGrid(data=penguins, x="bill_length_mm", y="bill_depth_mm")
fig_joint_grid.plot_joint(sns.scatterplot, s=100, alpha=0.5)
fig_joint_grid.plot_marginals(sns.histplot, kde=True)
pb.print_figure(
    fig_joint_grid,
    caption="Seaborn JointGrid.",
    matplotlib_format="png",
    embedded=False,
)
