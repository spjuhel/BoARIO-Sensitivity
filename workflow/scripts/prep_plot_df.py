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
sns.set_context(snakemake.config.get("sns context", "notebook"))

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

def drop_levels_with_identical_values(df: pd.DataFrame) -> pd.DataFrame:
    """
    Given a pandas DataFrame with a multi-level index, drop any levels for which all
    rows share the same index value.
    """
    # Get a list of the levels of the index
    levels = df.index.levels

    # Create a list of boolean masks indicating which levels should be dropped
    masks = [df.index.get_level_values(i).nunique() == 1 for i in range(len(levels))]

    # Drop the levels that should be dropped
    df = df.droplevel(level=[i for i, mask in enumerate(masks) if mask])

    return df


def drop_xps(df, drop_dict):
    _df = df.copy()
    for key, val in drop_dict.items():
        if isinstance(val, str):
            val = [val]
        for v in val:
            try:
                _df.drop(index=str(v), level=key, inplace=True, axis=0)
            except KeyError:
                logger.warning(
                    f"You ask to remove rows where {key} = {val}, but none were found in the dataframe."
                )
    return _df


def prepare_res_df(inpt, drop_dict=None):
    res_df = pd.read_parquet(inpt)
    res_df = res_df.melt(ignore_index=False)
    res_df.reset_index(level=["mrio", "mrio year"], inplace=True)
    res_df["mrio"] = res_df[["mrio", "mrio year"]].agg("_".join, axis=1)
    res_df.drop("mrio year", axis=1, inplace=True)
    res_df.set_index("mrio", append=True, inplace=True)
    if drop_dict:
        res_df = drop_xps(res_df, drop_dict)
    res_df = drop_levels_with_identical_values(res_df)
    res_df.set_index(["region", "sector"], append=True, inplace=True)
    res_df.reset_index(inplace=True)
    res_df.set_index(["step", "region", "sector", "variable"], inplace=True)
    col_var = list(res_df.columns[res_df.columns != "value"])
    res_df["Experience"] = res_df[col_var].agg("~".join, axis=1)
    res_df.drop(col_var, axis=1, inplace=True)
    res_df.reset_index(inplace=True)
    res_df.set_index(["variable", "region", "sector", "step"], inplace=True)
    return res_df

drop_dict = snakemake.params.get("drop_dict")
res_df = prepare_res_df(snakemake.input[0], drop_dict=drop_dict)
res_df.to_parquet(snakemake.output[0])
