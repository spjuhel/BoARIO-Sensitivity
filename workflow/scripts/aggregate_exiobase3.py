import sys, os
import logging, traceback
from typing import Optional, Union
import pathlib
import json
import pandas as pd
import numpy as np
import pickle as pkl
import pymrio as pym

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


def aggreg(
    mrio_path: Union[str, pathlib.Path],
    sector_aggregator_path: Union[str, pathlib.Path],
    save_path=None,
):
    logger.info("Loading region aggregator")
    logger.info(
        "Make sure you use the same python environment as the one loading the pickle file (especial pymrio and pandas version !)"
    )
    logger.info("Your current environment is: {}".format(os.environ["CONDA_PREFIX"]))

    mrio_path = pathlib.Path(mrio_path)
    if not mrio_path.exists():
        raise FileNotFoundError("MRIO file not found - {}".format(mrio_path))

    if mrio_path.suffix == ".pkl":
        with mrio_path.open("rb") as f:
            logger.info("Loading MRIO from {}".format(mrio_path.resolve()))
            mrio = pkl.load(f)
    else:
        raise TypeError(
            "File type ({}) not recognize for the script (must be zip or pkl) : {}".format(
                mrio_path.suffix, mrio_path.resolve()
            )
        )

    assert isinstance(mrio, pym.IOSystem)

    sec_agg_vec = pd.read_csv(sector_aggregator_path, index_col=0)
    sec_agg_vec.sort_index(inplace=True)

    logger.info("Done")
    logger.info(
        "Reading aggregation from {}".format(
            pathlib.Path(sector_aggregator_path).absolute()
        )
    )
    logger.info(
        "Aggregating from {} to {} sectors".format(
            len(mrio.get_sectors()), len(sec_agg_vec.group.unique())
        )
    )  # type:ignore
    mrio.aggregate(sector_agg=sec_agg_vec.name.values)
    mrio.calc_all()
    logger.info("Done")
    logger.info(f"Saving to {save_path}")
    with open(str(save_path), "wb") as f:
        pkl.dump(mrio, f)


logger.info(
    f"Starting mrio aggregation to {snakemake.wildcards.aggregation} for: {snakemake.input.mrio_pkl}"
)

aggreg(
    mrio_path=snakemake.input.mrio_pkl,
    sector_aggregator_path=snakemake.input.aggreg,
    save_path=snakemake.output,
)
