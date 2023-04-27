import sys, os
import logging, traceback
import pandas as pd
import pathlib

logging.basicConfig(
    filename=snakemake.log[0],
    level=logging.INFO,
    format="%(asctime)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())

variable_names = snakemake.config["plot config"]["plot variable name mapping"]
impact_names = snakemake.config["impacts_bins_name"]


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

    #max_neg_impact_class
#{{scope}}/{{selection_type}}~{{selection}}/{{faceting}}/{{variable}}_{{plot_type}}.

# Install exception handler
sys.excepthook = handle_exception

lines=f"""Results {snakemake.wildcards.focus}
=============================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   results-contents/"""+"\n   results-contents/".join([pathlib.Path(f).stem for f in snakemake.input.local_rst])+"\n   "+"\n   ".join([pathlib.Path(f).stem for f in snakemake.input.general_rst])+"\n"

with open(snakemake.output[0], "w") as f:
    f.writelines(lines)
