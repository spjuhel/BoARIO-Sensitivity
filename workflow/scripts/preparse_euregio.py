import sys, os
import logging, traceback
import pymrio as pym
import pathlib
import pickle as pkl
import pandas as pd

REGIONS_RENAMING = {"DEE1": "DEE0", "DEE2": "DEE0", "DEE3": "DEE0"}

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


def lexico_reindex(mrio: pym.IOSystem) -> pym.IOSystem:
    """Re-index IOSystem lexicographicaly

    Sort indexes and columns of the dataframe of a :ref:`pymrio.IOSystem` by
    lexical order.

    Parameters
    ----------
    mrio : pym.IOSystem
        The IOSystem to sort

    Returns
    -------
    pym.IOSystem
        The sorted IOSystem

    """
    for attr in ["Z", "Y", "x", "A"]:
        if getattr(mrio, attr) is None:
            raise ValueError(
                "Attribute {} is None, did you forget to calc_all() the MRIO ?".format(
                    attr
                )
            )
    mrio.Z = mrio.Z.reindex(sorted(mrio.Z.index), axis=0)  # type: ignore
    mrio.Z = mrio.Z.reindex(sorted(mrio.Z.columns), axis=1)  # type: ignore
    mrio.Y = mrio.Y.reindex(sorted(mrio.Y.index), axis=0)  # type: ignore
    mrio.Y = mrio.Y.reindex(sorted(mrio.Y.columns), axis=1)  # type: ignore
    mrio.x = mrio.x.reindex(sorted(mrio.x.index), axis=0)  # type: ignore
    mrio.A = mrio.A.reindex(sorted(mrio.A.index), axis=0)  # type: ignore
    mrio.A = mrio.A.reindex(sorted(mrio.A.columns), axis=1)  # type: ignore

    return mrio


def correct_regions(euregio: pym.IOSystem):
    euregio.rename_regions(REGIONS_RENAMING).aggregate_duplicates()
    return euregio


def build_from_csv(csv_file, inv_treatment=True):
    cols_z = [2, 5] + [i for i in range(6, 3730, 1)]
    ioz = pd.read_csv(
        csv_file,
        index_col=[0, 1],
        usecols=cols_z,
        engine="c",
        names=None,
        header=None,
        skiprows=8,
        nrows=3724,
        decimal=".",
        low_memory=False,
    )
    ioz.rename_axis(index=["region", "sector"], inplace=True)
    ioz.columns = ioz.index
    ioz.fillna(value=0.0, inplace=True)

    cols_y = [3733, 3736] + [i for i in range(3737, 3737 + 1064, 1)]
    fd_index = pd.read_csv(
        csv_file, usecols=[3737, 3738, 3739, 3740], skiprows=7, header=0, nrows=0
    ).columns
    ioy = pd.read_csv(
        csv_file,
        index_col=[0, 1],
        usecols=cols_y,
        engine="c",
        names=None,
        header=None,
        skiprows=8,
        nrows=3724,
        decimal=".",
        low_memory=False,
    )
    ioy.rename_axis(index=["region", "sector"], inplace=True)
    ioy.columns = pd.MultiIndex.from_product(
        [ioy.index.get_level_values(0).unique(), fd_index]
    )
    ioy.fillna(value=0.0, inplace=True)

    iova = pd.read_csv(
        csv_file,
        index_col=[5],
        engine="c",
        header=[0, 3],
        skiprows=3735,
        nrows=6,
        decimal=".",
        low_memory=False,
    )
    iova.rename_axis(index=["va_cat"], inplace=True)
    iova.fillna(value=0.0, inplace=True)
    iova.drop(iova.iloc[:, :5].columns, axis=1, inplace=True)
    iova.drop(iova.iloc[:, 3724:].columns, axis=1, inplace=True)

    # ioz = ioz.rename_axis(["region","sector"])
    # ioz = ioz.rename_axis(["region","sector"],axis=1)

    ioy = ioy.rename_axis(["region", "sector"])
    ioy = ioy.rename_axis(["region", "category"], axis=1)
    if inv_treatment:
        #invs = ioy.loc[:, (slice(None), "Inventory_adjustment")].sum(axis=1)
        #invs.name = "Inventory_use"
        #invs_neg = pd.DataFrame(-invs).T
        #invs_neg[invs_neg < 0] = 0
        #iova = pd.concat([iova, invs_neg], axis=0)
        ioy = ioy.clip(lower=0)

    return ioz, ioy, iova


def preparse_euregio(mrio_csv: str, output: str, year):
    logger.info(
        "Make sure you use the same python environment as the one loading the pickle file (especial pymrio and pandas version !)"
    )
    logger.info("Your current environment is: {}".format(os.environ["CONDA_PREFIX"]))
    ioz, ioy, iova = build_from_csv(mrio_csv, inv_treatment=True)
    euregio = pym.IOSystem(
        Z=ioz,
        Y=ioy,
        year=year,
        unit=pd.DataFrame(
            data=["2010_€_MILLIONS"] * len(iova.index),
            index=iova.index,
            columns=["unit"],
        ),
    )
    logger.info(f"Correcting germany regions : {REGIONS_RENAMING}")
    euregio = correct_regions(euregio)
    logger.info("Computing the missing IO components")
    euregio.calc_all()
    euregio.meta.change_meta("name", f"euregio {year}")

    assert isinstance(euregio, pym.IOSystem)
    logger.info("Re-indexing lexicographicaly")
    euregio = lexico_reindex(euregio)
    logger.info("Done")
    save_path = pathlib.Path(output)
    logger.info("Saving to {}".format(save_path.absolute()))
    save_path.parent.mkdir(parents=True, exist_ok=True)
    setattr(euregio, "monetary_factor", 1000000)
    with open(save_path, "wb") as f:
        pkl.dump(euregio, f)


preparse_euregio(snakemake.input[0], snakemake.output[0], snakemake.wildcards.year)
