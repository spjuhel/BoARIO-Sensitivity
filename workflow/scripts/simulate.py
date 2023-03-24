import sys
import re
import subprocess
import pathlib
import boario
from boario.event import EventKapitalRebuild, EventKapitalRecover
from boario.simulation import Simulation
from boario.extended_models import ARIOPsiModel
import pandas as pd
import logging, traceback
import pickle
import pymrio as pym

logging.basicConfig(
    filename=snakemake.log[0],
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

boario.logger.addHandler(logging.StreamHandler())

logger = boario.logger

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


def load_mrio(filename: str) -> pym.IOSystem:
    """
    Loads the pickle file with the given filename.

    Args:
        filename: A string representing the name of the file to load (without the .pkl extension).
                  Valid file names follow the format <prefix>_full_<year>, where <prefix> is one of
                  'oecd_v2021', 'euregio', 'exiobase3', or 'eora26', and <year> is a four-digit year
                  such as '2000' or '2010'.

    Returns:
        The loaded pickle file.

    Raises:
        ValueError: If the given filename does not match the valid file name format, or the file doesn't contain an IOSystem.

    """
    filepath = "./mrio-files/pkls/"  # the path to the pickle files
    regex = re.compile(
        r"^(oecd_v2021|euregio|exiobase3|eora26)_full_(\d{4})"
    )  # the regular expression to match filenames

    match = regex.match(filename)  # match the filename with the regular expression

    if not match:
        raise ValueError(f"The file name {filename} is not valid.")

    prefix, year = match.groups()  # get the prefix and year from the matched groups

    fullpath = filepath + prefix + "/" + filename + ".pkl"  # create the full file path

    logger.info(f"Loading {filename} mrio")
    with open(fullpath, "rb") as f:
        mrio = pickle.load(f)  # load the pickle file

    if not isinstance(mrio, pym.IOSystem):
        raise ValueError(f"{filename} was loaded but it is not an IOSystem")

    return mrio


def create_event(
    flood_scenario,
    recovery_scenario,
    region_affected: str,
    gva_df,
    sectors_df,
    smk_config,
):
    intensity = float(smk_config["impact_intensity"][flood_scenario[0]])
    duration = flood_scenario[1]
    impact = intensity * gva_df[region_affected]
    aff_sectors = sectors_df.loc[sectors_df.affected == 1].index
    rebuilding_sectors = sectors_df.loc[sectors_df.rebuilding_factor > 0].to_dict()
    sce_tuple = recovery_scenario
    if sce_tuple[0] == "recovery":
        event = EventKapitalRecover(
            impact,
            recovery_function=sce_tuple[1],
            recovery_time=sce_tuple[2],
            aff_regions=[region_affected],
            aff_sectors=aff_sectors,
            impact_sectoral_distrib_type="gdp",
            duration=duration,
        )
    elif sce_tuple[0] == "rebuilding":
        event = EventKapitalRebuild(
            impact,
            rebuilding_sectors=rebuilding_sectors,
            rebuild_tau=sce_tuple[2],
            aff_regions=[region_affected],
            aff_sectors=aff_sectors,
            impact_sectoral_distrib_type="gdp",
            duration=duration,
            rebuilding_factor=sce_tuple[1],
        )
    else:
        raise ValueError(
            f'Invalid event type: {sce_tuple[0]} (expected "recovery" or "rebuilding")'
        )

    return event


def run(
    mrio_name,
    region_affected,
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
    sectors_df
):

    mrio = load_mrio(mrio_name)

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
        kapital_to_VA_dict=sectors_df.kapital_to_va_ratio.to_dict(),
        psi_param=psi_param,
        inventory_restoration_tau=sectors_df.inventory_tau.to_dict(),
        inventory_dict=sectors_df.inventory_size.to_dict()
    )
    value_added = mrio.x.T - mrio.Z.sum(axis=0)
    value_added = value_added.reindex(sorted(value_added.index), axis=0)  # type: ignore
    value_added = value_added.reindex(sorted(value_added.columns), axis=1)
    value_added[value_added < 0] = 0.0
    gva_df = value_added.groupby("region", axis=1).sum().T["indout"]
    if mrio.unit.unit.unique()[0] != "M.EUR":
        logger.warning(
            "MRIO unit appears to not be 'M.EUR'; but {} instead, which is not yet implemented. Contact the dev !\n Continuing assuming monetary factor is million".format(
                mrio.unit.unit.unique()[0]
            )
        )
        gva_df = gva_df * (10**6)
    else:
        gva_df = gva_df * (10**6)

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
        flood_scenario,
        recovery_scenario,
        region_affected,
        gva_df,
        sectors_df,
        smk_config
    )

    sim.add_event(event)
    try:
        logger.info("Model ready, looping")
        sim.loop(progress=False)
    except Exception:
        logger.exception("There was a problem:")

    output_parquets.mkdir(exist_ok=True, parents=True)

    sim.production_realised.to_parquet(
        output_parquets / "production_realised.parquet"
    )
    sim.production_capacity.to_parquet(
        output_parquets / "production_capacity.parquet"
    )
    sim.overproduction.to_parquet(
        output_parquets / "overproduction.parquet"
    )
    sim.rebuild_prod.to_parquet(output_parquets / "rebuild_prod.parquet")
    sim.final_demand.to_parquet(output_parquets / "final_demand.parquet")
    sim.intermediate_demand.to_parquet(
        output_parquets / "intermediate_demand.parquet"
    )
    sim.rebuild_demand.to_parquet(
        output_parquets / "rebuild_demand.parquet"
    )
    sim.kapital_to_recover.to_parquet(
        output_parquets / "kapital_to_recover.parquet"
    )


# conf = load_config(snakemake.config, snakemake.wildcards, snakemake.input, snakemake.output.output_dir, snakemake.params)

simulation_params = snakemake.params.simulation_params
sectors_df = pd.read_csv(snakemake.input.sectors_config, index_col=0, decimal=",")
smk_config = snakemake.config
output_dir = pathlib.Path(snakemake.output.output_dir).resolve()
output_parquets = pathlib.Path(snakemake.output.parquet_files).resolve()
flood_scenario = smk_config["flood_scenarios"][simulation_params["flood_scenario"]]
recovery_scenario = smk_config["recovery_scenarios"][simulation_params["recovery_scenario"]]

logger.info(f"Running simulation for {output_parquets}")

logger.info(
    "You are running the following version of BoARIO : {}".format(boario.__version__)
)
logger.info(
    "You are using BoARIO in editable install mode : {}".format(dist_is_editable())
)
logger.info("BoARIO's location is : {}".format(boario.__path__))

run(
    mrio_name=simulation_params["mrio"],
    region_affected=simulation_params["region_affected"],
    order_type=simulation_params["order"],
    psi_param=simulation_params["psi"],
    tau_alpha=simulation_params["tau_alpha"],
    base_alpha=simulation_params["base_alpha"],
    max_alpha=simulation_params["max_alpha"],
    recovery_scenario=recovery_scenario,
    flood_scenario=flood_scenario,
    output_dir=output_dir,
    output_parquets=output_parquets,
    monetary_factor=smk_config["monetary_factor"],
    sim_length=smk_config["sim_length"],
    register_stocks=smk_config["register_stocks"],
    sectors_df=sectors_df
)
