import sys
import logging, traceback
from boario_tools.mriot import load_mrio
from boario_tools.regex_patterns import MRIOT_FULLNAME_REGEX
import pandas as pd
import yaml
from itertools import product

import sys

sys.path.append("../others")

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

def init_imp(mrio_name,aff_country,impact_as_GVA_share):
    mrio = load_mrio(mrio_name, pkl_filepath=snakemake.params["pkl_dir"])
    aff_regions = mrio.get_regions()[mrio.get_regions().str.contains(aff_country)]
    return ((mrio.x.T - mrio.Z.sum(axis=0)).T.groupby("region").sum().T[aff_regions].sum() * impact_as_GVA_share).sum()

logger.info(f"Loading flood details from {snakemake.input.flood_scenario}")

with open(snakemake.input.flood_scenario) as stream:
    try:
        flood_details = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)

productive_impact_capital_share = (
    flood_details["prod_cap_impact_unit"] / flood_details["estimated_gdp_unit"]
)
house_impact_capital_share = (
    flood_details["house_impact_unit"] / flood_details["estimated_gdp_unit"]
)

df_floods = pd.DataFrame({"mrio": snakemake.input.mriots})
df_floods = df_floods["mrio"].str.extract(MRIOT_FULLNAME_REGEX)
df_floods["countries_affected"] = df_floods.apply(
    lambda row: flood_details["countries_affected"][row["mrio_basename"]], axis=1
)
df_floods.loc[
    df_floods["mrio_aggreg_regions"] == "full_regions", "regions_affected"
] = df_floods.loc[df_floods["mrio_aggreg_regions"] == "full_regions"].apply(
    lambda row: str(
        list(flood_details["regions_affected"][row["mrio_basename"]].keys())
    ),
    axis=1,
)
df_floods.loc[
    df_floods["mrio_aggreg_regions"] == "common_regions", "regions_affected"
] = str(list(flood_details["regions_affected"]["common"].keys()))
df_floods.loc[
    df_floods["mrio_aggreg_regions"] == "full_regions",
    "productive_capital_impact_regional_distrib",
] = df_floods.loc[df_floods["mrio_aggreg_regions"] == "full_regions"].apply(
    lambda row: str(
        list(flood_details["regions_affected"][row["mrio_basename"]].values())
    ),
    axis=1,
)
df_floods.loc[
    df_floods["mrio_aggreg_regions"] == "common_regions",
    "productive_capital_impact_regional_distrib",
] = str(list(flood_details["regions_affected"]["common"].values()))
df_floods["productive_capital_impact_GVA_share"] = productive_impact_capital_share
df_floods["households_impact_GVA_share"] = house_impact_capital_share
df_floods["duration"] = flood_details["duration"]
df_floods["mriot"] = df_floods[
    ["mrio_basename", "mrio_year", "mrio_aggreg_sectors", "mrio_aggreg_regions"]
].apply(lambda row: "_".join(row.values.astype(str)), axis=1)

df_floods["productive_capital_impact"] = df_floods.apply(
    lambda row: init_imp(
        row["mriot"],
        row["countries_affected"],
        row["productive_capital_impact_GVA_share"],
    ),
    axis=1,
)
df_floods["households_impact"] = df_floods.apply(
    lambda row: init_imp(
        row["mriot"], row["countries_affected"], row["households_impact_GVA_share"]
    ),
    axis=1,
)
df_floods["flood_scenario"] = "germany21"
df_floods["productive_capital_impact_sectoral_distrib_type"] = "gdp"
df_floods = df_floods[
    [
        "mriot",
        "mrio_basename",
        "flood_scenario",
        "mrio_year",
        "mrio_aggreg_sectors",
        "mrio_aggreg_regions",
        "countries_affected",
        "regions_affected",
        "productive_capital_impact_GVA_share",
        "households_impact_GVA_share",
        "productive_capital_impact_regional_distrib",
        "productive_capital_impact_sectoral_distrib_type",
        "duration",
        "productive_capital_impact",
        "households_impact",
    ]
]

logger.info(f"Saving flood scenarios csv to {snakemake.output[0]}")
df_floods.to_csv(snakemake.output[0])
