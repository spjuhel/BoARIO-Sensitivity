import ast
import sys
import re
import subprocess
import pathlib
from boario_tools.mriot import load_mrio
from boario_tools.regex_patterns import MRIOT_FULLNAME_REGEX
import pandas as pd
import logging, traceback
import pickle
import pymrio as pym
from boario import logger

import sys
sys.path.append('../others')

formatter = logging.Formatter('%(levelname)s - %(lineno)d : %(message)s')
handler = logging.FileHandler(snakemake.log[0])
handler.setFormatter(formatter)
logger.addHandler(handler)


import boario
from boario.event import EventKapitalRebuild, EventKapitalRecover
from boario.simulation import Simulation
from boario.extended_models import ARIOPsiModel

import others.regex_patterns as regex_patterns

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


def dist_is_editable():
    """Is distribution an editable install?"""
    for pth in boario.__path__:
        if "site-packages" in pth:
            return False
    return True


def get_git_describe() -> str:
    return (
        subprocess.check_output(["git", "describe", "--tags"]).decode("ascii").strip()
    )


def get_flood_scenario(mrio_name, flood_scenario):
    regex = MRIOT_FULLNAME_REGEX
    match = regex.match(mrio_name)  # match the filename with the regular expression
    if not match:
        raise ValueError(f"The file name {mrio_name} is not valid.")
    flood_scenarios = pd.read_csv(
        snakemake.input.flood_scenarios,
        index_col=[1, 3],
        converters={
            "regions_affected": ast.literal_eval,
            "productive_capital_impact_regional_distrib": ast.literal_eval,
        },
    )
    scenar = flood_scenarios.loc[(mrio_name, flood_scenario)]
    return scenar


def create_event(
    mrio_name,
    flood_scenario,
    recovery_scenario,
    sectors_df,
):
    aff_sectors = sectors_df.loc[sectors_df.affected == 1].index
    rebuilding_sectors = sectors_df.loc[
        sectors_df.rebuilding_factor > 0, "rebuilding_factor"
    ].to_dict()
    scenar = get_flood_scenario(mrio_name, flood_scenario)
    logger.debug(
        f"Creating event from : productive_capital_impact {scenar.productive_capital_impact} ; households_impact {scenar.households_impact} ; duration {scenar.duration} ; aff_sectors {aff_sectors} ; reb_sectors {rebuilding_sectors}"
    )
    sce_tuple = recovery_scenario

    aff_regions = scenar.regions_affected

    productive_capital_impact = scenar.productive_capital_impact
    households_impact = scenar.households_impact

    duration = scenar.duration
    productive_capital_impact_regional_distrib = scenar.productive_capital_impact_regional_distrib
    productive_capital_impact_sectoral_distrib_type = scenar.productive_capital_impact_sectoral_distrib_type
    if sce_tuple[0] == "rec":
        event = EventKapitalRecover.from_scalar_regions_sectors(
            impact=productive_capital_impact,
            recovery_function="linear",
            recovery_time=int( sce_tuple[1] ),
            regions=aff_regions,
            impact_regional_distrib=productive_capital_impact_regional_distrib,
            sectors=aff_sectors,
            impact_sectoral_distrib=productive_capital_impact_sectoral_distrib_type,
            duration=duration,
            #event_monetary_factor=10**6,
        )
    elif sce_tuple[0] == "reb":
        event = EventKapitalRebuild.from_scalar_regions_sectors(
            impact=productive_capital_impact,
            households_impact=households_impact,
            rebuilding_sectors=rebuilding_sectors,
            rebuild_tau=int( sce_tuple[1] ),
            regions=aff_regions,
            impact_regional_distrib=productive_capital_impact_regional_distrib,
            sectors=aff_sectors,
            impact_sectoral_distrib=productive_capital_impact_sectoral_distrib_type,
            duration=duration,
            rebuilding_factor=1.0,
            #event_monetary_factor=10**6,
        )
    else:
        raise ValueError(
            f'Invalid event type: {sce_tuple[0]} (expected "rec" or "reb")'
        )

    return event


def run(
        mrio_name,
        pkl_filepath,
    order_type,
    psi_param,
    tau_alpha,
    base_alpha,
    max_alpha,
    recovery_scenario,
    flood_scenario,
    output_dir,
    output_parquets,
    monetary_factor,
    sim_length,
    register_stocks,
    sectors_df,
):

    mrio = load_mrio(filename=mrio_name, pkl_filepath=pkl_filepath)

    model = ARIOPsiModel(
        pym_mrio=mrio,
        order_type=order_type,
        alpha_base=base_alpha,
        alpha_max=max_alpha,
        alpha_tau=tau_alpha,
        rebuild_tau=1,
        monetary_factor=monetary_factor,
        temporal_units_by_step=1,
        iotable_year_to_temporal_unit_factor=365,
        productive_capital_to_VA_dict=sectors_df.productive_capital_to_va_ratio.to_dict(),
        psi_param=psi_param,
        inventory_restoration_tau=sectors_df.inventory_tau.to_dict(),
        inventory_dict=sectors_df.inventory_size.to_dict(),
    )

    sim = Simulation(
        model=model,
        register_stocks=register_stocks,
        n_temporal_units_to_sim=sim_length,
        boario_output_dir=output_dir,
        save_events=True,
        save_params=True,
        save_index=True,
        save_records=[],
    )

    logger.info(f"Building event from:\n {flood_scenario}")
    event = create_event(
        mrio_name,
        flood_scenario,
        recovery_scenario,
        sectors_df,
    )

    sim.add_event(event)
    try:
        logger.info("Model ready, looping")
        sim.loop(progress=False)
    except Exception:
        logger.exception("There was a problem:")

    output_parquets.mkdir(exist_ok=True, parents=True)

    sim.production_realised.to_parquet(output_parquets / "production_realised.parquet")
    sim.production_capacity.to_parquet(output_parquets / "production_capacity.parquet")
    sim.overproduction.to_parquet(output_parquets / "overproduction.parquet")
    sim.rebuild_prod.to_parquet(output_parquets / "rebuild_prod.parquet")
    sim.final_demand.to_parquet(output_parquets / "final_demand.parquet")
    sim.final_demand_unmet.to_parquet(output_parquets / "final_demand_unmet.parquet")
    sim.intermediate_demand.to_parquet(output_parquets / "intermediate_demand.parquet")
    sim.rebuild_demand.to_parquet(output_parquets / "rebuild_demand.parquet")
    sim.productive_capital_to_recover.to_parquet(output_parquets / "productive_capital_to_recover.parquet")


# conf = load_config(snakemake.config, snakemake.wildcards, snakemake.input, snakemake.output.output_dir, snakemake.params)

simulation_params = snakemake.params.simulation_params
sectors_df = pd.read_csv(snakemake.input.sectors_config, index_col=0, decimal=".")
smk_config = snakemake.config
output_dir = pathlib.Path(snakemake.output.output_dir).resolve()
output_parquets = output_dir / "parquets"
flood_scenario = simulation_params["flood_scenario"]
recovery_scenario = simulation_params["recovery_scenario"].split("_")

logger.info(f"Running simulation for {output_parquets}")

logger.info(
    "You are running the following version of BoARIO : {}".format(boario.__version__)
)
logger.info(
    "You are using BoARIO in editable install mode : {}".format(dist_is_editable())
)
logger.info("BoARIO's location is : {}".format(boario.__path__))

mrio_regex = MRIOT_FULLNAME_REGEX
mrio_match = mrio_regex.match(simulation_params["mriot"])
if not mrio_match:
    raise ValueError(f"The file name {simulation_params['mrio']} is not valid.")

(
    mrio_basename,
    mrio_year,
    mrio_sectors_aggreg,
    mrio_regions_aggreg,
) = mrio_match.groups()  # get the mrio_basename and mrio_year from the matched groups


run(
    mrio_name=simulation_params["mriot"],
    pkl_filepath=snakemake.config["data-mriot"]["prefix"] + snakemake.config["data-mriot"]["parsed_mriot_dir"],
    order_type=simulation_params["order"],
    psi_param=simulation_params["psi"],
    tau_alpha=simulation_params["tau_alpha"],
    base_alpha=simulation_params["base_alpha"],
    max_alpha=simulation_params["max_alpha"],
    recovery_scenario=recovery_scenario,
    flood_scenario=flood_scenario,
    output_dir=output_dir,
    output_parquets=output_parquets,
    monetary_factor=smk_config["monetary_factor"][mrio_basename],
    sim_length=smk_config["sim_length"],
    register_stocks=smk_config["register_stocks"],
    sectors_df=sectors_df,
)
