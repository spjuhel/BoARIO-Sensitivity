import sys, os
import logging, traceback
import pandas as pd
import numpy as np

logging.basicConfig(
    filename=snakemake.log[0],
    level=logging.INFO,
    format="%(asctime)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())

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
    logger.info(f"Will drop these levels: { [df.index.levels[i].name for i, mask in enumerate(masks) if (mask and not df.index.levels[i].name in ['mrio','variable'] )] }")
    df = df.droplevel(level=[i for i, mask in enumerate(masks) if (mask and not df.index.levels[i].name in ['mrio','variable','psi','alpha_tau'] )])

    return df

def drop_xps(df, drop_dict):
    _df = df.copy()
    for key,val in drop_dict.items():
        if isinstance(val,str):
            val=[val]
        for v in val:
            try:
                _df.drop(index=str(v), level=key,inplace=True,axis=0)
            except KeyError:
                logger.warning(f"You ask to remove rows where {key} = {val}, but none were found in the dataframe.")
    return _df

def prepare_df_1(inpt, drop_dict=None, drop_unused=True):
    """
    Prepare DataFrame for analysis.

    Args:
        inpt (str): Path to parquet file.
        drop_dict (dict): Dictionary of columns to drop.

    Returns:
        res_df (pandas.DataFrame): Prepared DataFrame.
    """
    res_df = pd.read_parquet(inpt)
    logger.info("Melting")
    res_df = res_df.melt(ignore_index=False).reset_index(level=["mrio", "mrio year"])
    logger.info("Joining mrio with year")
    res_df["mrio"] = res_df[["mrio", "mrio year"]].agg("_".join, axis=1)
    res_df.drop("mrio year", axis=1, inplace=True)
    res_df.set_index("mrio", append=True, inplace=True)

    if drop_dict:
        logger.info("Dropping xps to drop")
        res_df = drop_xps(res_df, drop_dict)

    if drop_unused:
        logger.info("Droping unused index levels")
        res_df = drop_levels_with_identical_values(res_df)

    logger.info("Reindexing")
    res_df = res_df.reset_index().set_index(["step", "region", "sector", "variable"]).sort_index()

    col_var = list(res_df.columns[res_df.columns != "value"])
    logger.info("Experience naming")
    res_df["Experience"] = res_df[col_var].agg("~".join, axis=1)
    res_df.drop(col_var, axis=1, inplace=True)
    res_df = res_df.reset_index().set_index(["variable", "region", "sector", "step"]).sort_index()

    return res_df

def prepare_df_2(df, neg_bins, pos_bins):
    def pct_change(x):
        return ((x - x.iloc[0]) / x.iloc[0]) * 100

    def yearly_pct_change_cumsum(x):
        return (x / 365).cumsum()

    max_neg_bins = list(neg_bins.values())
    max_neg_bins.append(np.inf) #   # Define the bin edges
    max_neg_labels = neg_bins.keys() #   # Define the bin labels
    max_pos_bins = list(pos_bins.values())
    max_pos_bins.append(np.inf) # [-np.inf, 0, 2, 5, 10, 15, 20, 25, np.inf]  # Define the bin edges
    max_pos_labels = pos_bins.keys() # ["no gains", "0%>G>2%", "2%>G>5%", "5%>G>10%", "10%>G>15%", "15%>G>20%", "20%>G>25%", "G>25%"]  # Define the bin labels

    _df = df.copy().reset_index()
    cols_to_groupby = list(_df.columns[(_df.columns != "value") & (_df.columns != "step")])
    #_df.reset_index(inplace=True)
    #_df.set_index("step", inplace=True)
    #display(_df)
    _df["value_pct"] = _df.groupby(cols_to_groupby,axis=0,group_keys=False)["value"].apply(pct_change)
    _df["value_cumsum_pct"] = _df.groupby(cols_to_groupby,axis=0,group_keys=False)["value_pct"].apply(yearly_pct_change_cumsum)
    _df["max_neg_impact_value_pct"] = _df.groupby("Experience")["value_pct"].transform(min)
    _df["max_neg_impact_class"] = _df.groupby("Experience")[["max_neg_impact_value_pct"]].transform(lambda x: pd.cut(x, bins=max_neg_bins, labels=max_neg_labels))
    _df["max_pos_impact_value_pct"] = _df.groupby("Experience")["value_pct"].transform(max)
    _df["max_pos_impact_class"] = _df.groupby("Experience")[["max_pos_impact_value_pct"]].transform(lambda x: pd.cut(x, bins=max_pos_bins, labels=max_pos_labels))
    return _df

drop_dict = snakemake.params.get("drop_dict")
res_df = prepare_df_1(snakemake.input[0], drop_dict=drop_dict)
res_df = prepare_df_2(res_df, neg_bins=snakemake.config["impacts_bins"], pos_bins=snakemake.config["gains_bins"])
res_df.to_parquet(snakemake.output[0])
