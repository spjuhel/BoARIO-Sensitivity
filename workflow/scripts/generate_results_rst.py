import sys, os
import logging, traceback
import pandas as pd

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

def generate_plot_var(scope, focus, selection_type, selection, faceting, variable) -> str:
    return f"""Variable is: {variable}
---------------------------------------

Change from initial level
^^^^^^^^^^^^^^^^^^^^^^^^^

.. image:: ../images/figs/{scope}/{focus}/{selection_type}~{selection}/{faceting}/{variable}_classic.svg
    :alt: No data to plot (possibly because no simulation correspond to this scope/selection)

Cumulative change (expressed as percentage of yearly total)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. image:: ../images/figs/{scope}/{focus}/{selection_type}~{selection}/{faceting}/{variable}_cumsum.svg
    :alt: No data to plot (possibly because no simulation correspond to this scope/selection)

"""


def generate_plot_selection(scope, focus, selection_type, selection, faceting, variables) -> str:
    res = f"""Simulation regrouped such that {selection_type}=={selection} :
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
    res = res + "\n".join(
        [
            generate_plot_var(scope, focus, selection_type, selection, faceting, var)
            for var in variables
        ]
    )
    return res


def generate_all_selections(scope, focus, selection_type, selections, faceting, variables) -> str:
    res = "\n".join(
        [
            generate_plot_selection(scope, focus, selection_type, selec, faceting, variables)
            for selec in selections
        ]
    )
    return res

variables_to_plot = snakemake.params.variables
focus = snakemake.wildcards.focus
scope = snakemake.wildcards.scope
selection_type = snakemake.wildcards.selection_type
faceting = snakemake.wildcards.faceting
plot_df = pd.read_parquet(snakemake.input.plot_df)
selections = plot_df[selection_type].sort_values().unique()

header_sec_reg = f"""**********************************************************
Comparing by resulting impact (sector,region facets) ({focus})
**********************************************************

Comparison of indirect impacts for each variable in a facet format
with sectors as columns and regions as row. Regrouping plots by maximum size of indirect impact.

"""

header_recov_local = f"""***************************************************************
Comparing by params for the affected region (recover scenario facets) ({focus})
***************************************************************

Comparison of indirect impacts for each variable in a facet format
based on recovery scenario. Regrouping plot by common parameters.

"""


lines = header_sec_reg + generate_all_selections(scope, focus, selection_type, selections, faceting, variables_to_plot)

with open(snakemake.output.res_rst, "w") as f:
    f.writelines(lines)
