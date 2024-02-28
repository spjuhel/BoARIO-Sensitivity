# Snakemake workflow: `BoARIO-Sensitivity-Analysis`

[![Snakemake](https://img.shields.io/badge/snakemake-≥8.0.0-brightgreen.svg)](https://snakemake.github.io)

A Snakemake workflow for deploying a sensitivity analysis for the BoARIO economic model.

## Usage

The usage of this workflow is described in the [Snakemake Workflow Catalog](https://snakemake.github.io/snakemake-workflow-catalog/?usage=spjuhel%2FBoARIO-Sensitivity).

If you use this workflow in a paper, don't forget to give credits to the authors by citing the URL of this (original) repository.

### Experience configuration

The pipeline is mainly configured by three files, that can be configured inside `config/config.yaml`:

- `parameters space` (`config/parameters_space.csv` by default)
- `flood_scenarios` (`config/flood_scenarios.csv` by default)
- `sectors_scenario` (`config/<mriot_name>_<aggregation_name>.csv`)

Some of the configuration is also directly handled inside `config/config.yaml` (See its specific README).

#### Parameters space

We highly recommend to generate the file using the Notebook `Notebooks/parameter_space_generation.ipynb`.

Each line in the file defines a simulation to run and requires the following columns:

- `mrio` : the MRIOT to use, in the format `<mriot_basename>_<aggregation_name>_<year>`
- `order`, `psi`, `base_alpha`, `max_alpha`, `tau_alpha` : the value for the corresponding parameters that the `BoARIO` model should use (see [Model parameters](https://spjuhel.github.io/BoARIO/boario-quickstart.html#model-parameters))
- `sectors_scenario` : the name of the "sector scenario" to use, that is, the parameters specific to sectors. The pipeline looks up the file corresponding to the given name inside `config.yaml`
- `recovery_scenario` : the name of the "recovery scenario" to use (see `config.yaml`)
- `flood_scenario` : the name of the "flood scenario" to use. The pipeline looks up the corresponding line in the `flood_scenarios` file specified in `config.yaml`.

#### Sector scenario

A "sector scenario" defines values for sectors for a specific MRIOT, possibly aggregated to new set of sectors. We use `csv` files with the following naming scheme: `<mriot_basename>_<aggregation_name>` ("eora26_full_sectors" for instance).

This file has to contain the following columns:

- a sector columns

### Regular Expressions
