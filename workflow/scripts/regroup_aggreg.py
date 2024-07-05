import sys
import logging, traceback
import pandas as pd

import sys

sys.path.append("../others")

import others.regex_patterns as regex_patterns

from importlib import resources

logging.basicConfig(
    filename=snakemake.log[0],
    level=logging.INFO,
    format="%(asctime)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())


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

if snakemake.params["sectors_aggreg_ods"] is not None:
    sectors_aggregation_dict = {
        sheet_name: pd.read_excel(
            snakemake.params["sectors_aggreg_ods"], sheet_name=sheet_name, index_col=0
            )
            for sheet_name in snakemake.params["sheet_names"]["sectors"].values()
}
else:
    with resources.path("boario_tools.data.aggregation_files","sectors_common_aggreg.ods") as agg_path:
        sectors_aggregation_dict = {
            sheet_name: pd.read_excel(
                agg_path, sheet_name=sheet_name, index_col=0
            )
            for sheet_name in snakemake.params["sheet_names"]["sectors"].values()
}

if snakemake.params["regions_aggreg_ods"] is not None:
    regions_aggregation_dict = {
        sheet_name: pd.read_excel(
            snakemake.params["regions_aggreg_ods"], sheet_name=sheet_name, index_col=0
            )
            for sheet_name in snakemake.params["sheet_names"]["regions"].values()
}
else:
    with resources.path("boario_tools.data.aggregation_files","regions_common_aggreg.ods") as agg_path:
        regions_aggregation_dict = {
            sheet_name: pd.read_excel(
                agg_path, sheet_name=sheet_name, index_col=0
            )
            for sheet_name in snakemake.params["sheet_names"]["regions"].values()
}


def aggreg_df(df, mrio_name, orig_sec_agg, orig_reg_agg):

    _df = df.copy()
    if orig_reg_agg != "common_regions":
        regions_aggreg = regions_aggregation_dict[snakemake.params["sheet_names"]["regions"][mrio_name]]
        _df.rename(regions_aggreg["new region"].to_dict(), axis=1, level=0, inplace=True)
        _df = _df.T.groupby(["region", "sector"]).sum().T

    if orig_sec_agg != "common_sectors":
        sectors_aggreg = sectors_aggregation_dict[snakemake.params["sheet_names"]["sectors"][mrio_name]]
        _df.rename(sectors_aggreg["new sector"].to_dict(), axis=1, level=1, inplace=True)
        _df = _df.T.groupby(["region", "sector"]).sum().T

    return _df


def common_monetary_factor(df, mrio_basename):
    _df = df.copy()
    _df = _df * (snakemake.config["monetary_factor"][mrio_basename] / 10**6)
    return _df


def create_result_dict(inputs):
    xp_regex = regex_patterns.SIMULATION_PATH_REGEX
    res_dict = {}
    for key, val in inputs.items():
        for xp_file in val:
            match = xp_regex.match(xp_file)
            if match:
                df = pd.read_parquet(xp_file)
                mriot_basename = match.group("mrio_basename")
                mriot_sectors_agg = match.group("mrio_aggreg_sectors")
                mriot_regions_agg = match.group("mrio_aggreg_regions")
                df = aggreg_df(df, mriot_basename, mriot_sectors_agg, mriot_regions_agg)
                df = common_monetary_factor(df, match.group("mrio_basename"))
                res_dict[
                    (
                        key,
                        match.group("mrio_basename"),
                        match.group("mrio_year"),
                        match.group("mrio_aggreg_sectors"),
                        match.group("mrio_aggreg_regions"),
                        match.group("sectors_scenario"),
                        match.group("recovery_scenario"),
                        match.group("flood_scenario"),
                        match.group("order"),
                        match.group("psi"),
                        match.group("base_alpha"),
                        match.group("max_alpha"),
                        match.group("tau_alpha"),
                    )
                ] = df
            else:
                ValueError(
                    f"Unmatched file, verify regex ?\n {val} to match with {xp_regex}"
                )

    return res_dict


logger.info(f"Starting creation of all results dictionary.")
res = create_result_dict(snakemake.input)
logger.info(f"Saving to {snakemake.output[0]}")
pd.concat(
    res,
    keys=res.keys(),
    names=[
        "variable",
        "mrio_basename",
        "mrio_year",
        "mrio_aggreg_sectors",
        "mrio_aggreg_regions",
        "sectors_sce",
        "recovery_sce",
        "flood_sce",
        "order type",
        "psi",
        "alpha_base",
        "alpha_max",
        "alpha_tau",
    ],
).to_parquet(snakemake.output[0])
