import sys, os
import logging, traceback
import pandas as pd
import re
import collections

import sys
sys.path.append('../others')

import others.regex_patterns as regex_patterns

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

sectors_common_aggreg = {
    sheet_name: pd.read_excel(
        snakemake.config["sectors_common_aggreg"], sheet_name=sheet_name, index_col=0
    )
    for sheet_name in [
        "eora26_without_reexport_to_common_aggreg",
        "euregio_to_common_aggreg",
        "exiobase_full_to_common_aggreg",
        "icio2021_reworked_to_common_aggreg",
    ]
}

regions_common_aggreg = {
    sheet_name: pd.read_excel(
        snakemake.config["regions_common_aggreg"], sheet_name=sheet_name, index_col=0
    )
    for sheet_name in [
        "eora26_without_reexport_to_common_aggreg",
        "euregio_to_common_aggreg",
        "exiobase_full_to_common_aggreg",
        "icio2021_reworked_to_common_aggreg",
    ]
}


def load_regions_aggreg(mrio_name):
    if "eora26" in mrio_name:
        return regions_common_aggreg["eora26_without_reexport_to_common_aggreg"]
    elif "euregio" in mrio_name:
        return regions_common_aggreg["euregio_to_common_aggreg"]
    elif "exiobase" in mrio_name:
        return regions_common_aggreg["exiobase_full_to_common_aggreg"]
    elif "oecd" in mrio_name:
        return regions_common_aggreg["icio2021_reworked_to_common_aggreg"]
    else:
        raise ValueError(f"Invalid MRIO name: {mrio_name}")


def load_sectors_aggreg(mrio_name):
    if "eora26" in mrio_name:
        return sectors_common_aggreg["eora26_without_reexport_to_common_aggreg"]
    elif "euregio" in mrio_name:
        return sectors_common_aggreg["euregio_to_common_aggreg"]
    elif "exiobase" in mrio_name:
        return sectors_common_aggreg["exiobase_full_to_common_aggreg"]
    elif "oecd" in mrio_name:
        return sectors_common_aggreg["icio2021_reworked_to_common_aggreg"]
    else:
        raise ValueError(f"Invalid MRIO name: {mrio_name}")


def aggreg_df(df, mrio_name):
    regions_aggreg = load_regions_aggreg(mrio_name)
    _df = df.copy()
    regions_aggreg = load_regions_aggreg(mrio_name)
    _df.rename(regions_aggreg["new region"].to_dict(), axis=1, level=0, inplace=True)
    _df = _df.T.groupby(["region", "sector"]).sum().T
    sectors_aggreg = load_sectors_aggreg(mrio_name)
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
                df = aggreg_df(df, match.group("mrio_basename"))
                df = common_monetary_factor(df, match.group("mrio_basename"))
                res_dict[
                    (
                        key,
                        match.group("mrio_basename"),
                        match.group("mrio_year"),
                        match.group("mrio_aggreg"),
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
        "mrio_aggreg",
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
