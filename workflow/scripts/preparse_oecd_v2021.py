import sys, os
import logging, traceback
import pymrio as pym
import pathlib
import pickle as pkl

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


def preparse_oecd_v2018(mrio_zip: str, output: str):
    logger.info(
        "Make sure you use the same python environment as the one loading the pickle file (especial pymrio and pandas version !)"
    )
    logger.info("Your current environment is: {}".format(os.environ["CONDA_PREFIX"]))
    mrio_path = pathlib.Path(mrio_zip)
    mrio_pym = pym.parse_oecd(path=mrio_path)
    logger.info("Removing unnecessary IOSystem attributes")
    attr = [
        "Z",
        "Y",
        "x",
        "A",
        "L",
        "unit",
        "population",
        "meta",
        "__non_agg_attributes__",
        "__coefficients__",
        "__basic__",
    ]
    tmp = list(mrio_pym.__dict__.keys())
    for at in tmp:
        if at not in attr:
            delattr(mrio_pym, at)
    assert isinstance(mrio_pym, pym.IOSystem)
    logger.info("Done")
    logger.info("Computing the missing IO components")
    mrio_pym.calc_all()
    logger.info("Done")
    logger.info("Re-indexing lexicographicaly")
    mrio_pym = lexico_reindex(mrio_pym)
    logger.info("Done")
    save_path = pathlib.Path(output)
    logger.info("Saving to {}".format(save_path.absolute()))
    save_path.parent.mkdir(parents=True, exist_ok=True)
    with open(save_path, "wb") as f:
        pkl.dump(mrio_pym, f)


preparse_oecd_v2018(snakemake.input[0], snakemake.output[0])
