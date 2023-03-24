import sys, os
import logging, traceback
import pymrio as pym
import pathlib

logging.basicConfig(filename=snakemake.log[0],
                    level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    )

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())

def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    logger.error(''.join(["Uncaught exception: ",
                         *traceback.format_exception(exc_type, exc_value, exc_traceback)
                         ])
                 )
# Install exception handler
sys.excepthook = handle_exception

logger.info(f"Starting oecd_v2018 download for: {snakemake.wildcards.year}")

oecd_v2018_folder = pathlib.Path("autodownloads/oecd_v2018")
oecd_v2018_folder.mkdir(exist_ok=True)
exio_meta = pym.download_oecd(storage_folder=oecd_v2018_folder, years=[snakemake.wildcards.year])
logger.info("Downloaded !")
