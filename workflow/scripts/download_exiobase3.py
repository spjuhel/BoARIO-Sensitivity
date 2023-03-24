import sys, os
import logging, traceback
import pymrio as pym
import pathlib

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

logger.info(
    f"Starting exiobase3 download for: {snakemake.wildcards.year}, {snakemake.wildcards.system}"
)

exio3_folder = pathlib.Path("autodownloads/exiobase3")
exio3_folder.mkdir(exist_ok=True)
exio_meta = pym.download_exiobase3(
    storage_folder=exio3_folder,
    system={snakemake.wildcards.system},
    years=[snakemake.wildcards.year],
)
logger.info("Downloaded !")
