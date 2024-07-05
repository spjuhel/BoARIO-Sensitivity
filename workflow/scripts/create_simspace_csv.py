import sys
import logging, traceback
import pandas as pd
import yaml
from itertools import product

import sys
sys.path.append('../others')

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

logger.info(f"Loading simulation space from {snakemake.input[0]}")

with open(snakemake.input[0]) as stream:
    try:
        data = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)


keys = data.keys()
values = (data[key] if isinstance(data[key], list) else [data[key]] for key in keys)

# Generate all combinations
combinations = list(product(*values))

# Create a pandas DataFrame
df = pd.DataFrame(combinations, columns=keys)

df.loc[(df["mriot"]=="eora26") & (df["mriot_aggreg"]=="full_sectors_full_regions"),"mriot_aggreg"] = "full_no_reexport_sectors_full_regions"

logger.info(f"Saving simulation space csv to {snakemake.output[0]}")
df.to_csv(snakemake.output[0])
