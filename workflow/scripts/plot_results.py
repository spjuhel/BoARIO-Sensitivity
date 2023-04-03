import sys, os
import logging, traceback
import pandas as pd
import seaborn as sns
import numpy as np

logging.basicConfig(
    filename=snakemake.log[0],
    level=logging.INFO,
    format="%(asctime)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())

sns.set_theme()
sns.set_context(snakemake.config["plot config"].get("sns context", "paper"))
sns.set(font_scale=2.1)

variable_name = snakemake.config["plot config"]["plot variable name mapping"]


def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    logger.error(
        "".join(
            [
                "Uncaught exception: ",
                *traceback.format_exception(exc_type, exc_value, exc_traceback),
            ]
        )
    )


# Install exception handler
sys.excepthook = handle_exception

def make_selection(df, selection):
    selection_lists = {key: [value] if isinstance(value, str) else value for key, value in selection.items()}
    qry = ' and '.join(["{} == {}".format(k,v) for k,v in selection_lists.items()])
    return df.query(qry)

def make_exclusion(df, exclusion):
    exclusion_lists = {key: [value] if isinstance(value, str) else value for key, value in exclusion.items()}
    qry = ' and '.join(["{} != {}".format(k,v) for k,v in exclusion_lists.items()])
    return df.query(qry)

def plot_variable_grid(
    plot_df,
    variable,
    selection={},
    exclusion=None,
    plot_type="classic",
    hue="Experience",
    col="sector",
    row="region",
    sharey=True,
    row_order=None,
    aspect=1.7,
    output=None,
):
    selection["variable"] = variable# if isinstance(variable, list) else [variable]
    df_to_plot = make_selection(plot_df, selection)
    if exclusion:
        df_to_plot = make_exclusion(plot_df, exclusion)
    #df_to_plot = subselect_var(plot_df, variable)

    grid = sns.FacetGrid(
        data=df_to_plot,
        col=col,
        row=row,
        margin_titles=True,
        sharey=sharey,
        hue=hue,
        row_order=row_order,
        aspect=aspect,
    )
    grid.map_dataframe(sns.lineplot, x="step", y="value_pct", linewidth=3, alpha=0.9)
    grid.add_legend()
    grid.set_axis_labels(y_var="% change")
    grid.set_titles(row_template="{row_name}", col_template="{col_name}")
    #grid.fig.subplots_adjust(top=0.90)  # adjust the Figure in rp
    grid.fig.suptitle(
        f"{variable_name[variable].capitalize()} change from pre-shock level",
        y=1.05,
        x=0.4
    )
    sns.move_legend(
    grid.fig, "upper center",
    bbox_to_anchor=(.45, 0.0), ncol=4, title="Experiences", frameon=True,
    )
    if output:
        grid.savefig(output)

plot_df = pd.read_parquet(snakemake.input[0])
plot_variable_grid(
    plot_df,
    snakemake.wildcards.variable,
    plot_type=snakemake.wildcards.plot_type,
    sharey=snakemake.params.sharey,
    row_order=snakemake.params.row_order,
    output=snakemake.output[0],
    selection={"max_neg_impact_class":snakemake.wildcards.impact_class}
)
