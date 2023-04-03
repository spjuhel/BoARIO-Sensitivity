import sys, os
import logging, traceback
import pandas as pd
import numpy as np

logging.basicConfig(
    filename=snakemake.log[0],
    level=logging.INFO,
    format="%(asctime)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())

variable_name = snakemake.config["plot config"]["plot variable name mapping"]


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

header = """******************
RESULTS
******************


General overview
==================

Comparison of indirect impacts for each variable in a facet format
with sectors as columns and regions as row.

"""

var_name_dict = snakemake.config["a"]

def generate_var_class(impact_class, variable, variable_name, focus):
    return f"""Results on {variable_name}
-----------------------

Change from initial level
^^^^^^^^^^^^^^^^^^^^^^^^^

.. image:: ../../../results/figs/sectors_regions_grids/{focus}/{impact_class}/{variable}_classic.svg

Cumulative change (expressed as percentage of yearly total)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. image:: ../../../results/figs/sectors_regions_grids/{focus}/{impact_class}/{variable}_cumsum.svg

"""

def generate_class(impact_class, variables, focus):
    res = f"""Regrouping results such that {impact_class}:\n
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    """
    res += "\n".join([generate_var_class(impact_class, var, var_name_dict[var], focus) for var in variables])
    return res


def generate_focus(focus, classes, variables):
    res = f"""Regrouping results for focus == {focus} :\n
..........................................................
    """
    res += "\n".join([generate_class(impact_class, variables, focus) for impact_class in classes])
    return res
