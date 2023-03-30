import sys, os
import logging, traceback
import pandas as pd
import seaborn as sns

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


def subselect_var(df: pd.DataFrame, var: str) -> None:
    """
    Given a pandas DataFrame with a multi-level index and a multi-level column index,
    sub-selects a DataFrame based on "var", "region" and "sector" and normalize its values
    by the values of the first row (which are the value of the first step).
    """
    _df = df.copy()
    # Sub-select the DataFrame based on "var", "region" and "sector"
    _df = _df.xs(var, level="variable")

    # Group the DataFrame by mrio, rec_sce, psi and alpha_t
    return _df


def subselect_region(df: pd.DataFrame, region: str) -> None:
    """
    Given a pandas DataFrame with a multi-level index and a multi-level column index,
    sub-selects a DataFrame based on "var", "region" and "sector" and normalize its values
    by the values of the first row (which are the value of the first step).
    """
    _df = df.copy()
    # Sub-select the DataFrame based on "var", "region" and "sector"
    _df = _df.xs(region, level="region")

    # Group the DataFrame by mrio, rec_sce, psi and alpha_t
    return _df


def subselect_sector(df: pd.DataFrame, sector: str) -> None:
    """
    Given a pandas DataFrame with a multi-level index and a multi-level column index,
    sub-selects a DataFrame based on "var", "region" and "sector" and normalize its values
    by the values of the first row (which are the value of the first step).
    """
    _df = df.copy()
    # Sub-select the DataFrame based on "var", "region" and "sector"
    _df = _df.xs(sector, level="sector")

    # Group the DataFrame by mrio, rec_sce, psi and alpha_t
    return _df


def plot_variable_grid(
    plot_df,
    variable,
    plot_type="classic",
    hue="Experience",
    col="sector",
    row="region",
    sharey=True,
    row_order=None,
    aspect=1.7,
    output=None,
):
    def pct_change(x):
        return ((x - x.loc[0]) / x.loc[0]) * 100

    def pct_change_cumsum(x):
        return (((x - x.loc[0]) / (x.loc[0] * 365)) * 100).cumsum()

    if plot_type == "cumsum":
        plot_fun = pct_change_cumsum
    elif plot_type == "classic":
        plot_fun = pct_change
    else:
        raise ValueError(f"Invalide plot_type : {plot_type}")

    df_to_plot = subselect_var(plot_df, variable)
    df_to_plot.reset_index(inplace=True)
    df_to_plot.set_index("step", inplace=True)
    df_to_plot.loc[:, "value_n"] = df_to_plot.groupby(
        list(df_to_plot.columns[df_to_plot.columns != "value"])
    ).transform(lambda x: plot_fun(x))

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
    grid.map_dataframe(sns.lineplot, x="step", y="value_n", linewidth=3, alpha=0.9)
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
    snakemake.wildcards.plot_type,
    sharey=snakemake.params.sharey,
    row_order=snakemake.params.row_order,
    output=snakemake.output[0],
)
