# Snakemake workflow: `BoARIO-Sensitivity-Analysis`

[![Snakemake](https://img.shields.io/badge/snakemake-≥8.0.0-brightgreen.svg)](https://snakemake.github.io)

A Snakemake workflow for deploying a sensitivity analysis for the BoARIO economic model.

## Usage

The usage of this workflow is described in the [Snakemake Workflow Catalog](https://snakemake.github.io/snakemake-workflow-catalog/?usage=spjuhel%2FBoARIO-Sensitivity).

Deploying with snakedeploy is not required, you can simply clone the repository and configure it by yourself.

If you use this workflow in a paper, don't forget to give credits to the authors by citing the URL of this (original) repository.

It is HIGHLY recommended that you read the [Snakemake documentation](https://snakemake.readthedocs.io/en/stable/index.html)
if you intend to use this pipeline.

(You may also contact me with a cool project idea if you struggle to run the pipeline :wink:)

### Experience configuration

[Specific README](config/README.md) in config subfolder.

### MRIOTs data handling

Downloading, parsing and aggregating MRIOTs is done using the [BoARIO-MRIOT-Tools](https://github.com/spjuhel/BoARIO-MRIOT-Tools)
pipeline which itself uses the [BoARIO-Tools](https://github.com/spjuhel/BoARIO-Tools) library.

The pipeline is automatically imported and if you use snakemake with `--software-deployment-method conda` (recommended), then you don't need to install anything. Otherwise you need to install the required dependencies of the different environments of both pipelines (located in `workflow/envs/`)

The BoARIO-MRIOT-Tools pipeline is configured inside the `config.yaml` under the `data-mriot` key. See [Specific README](config/README.md).

### Requirements

#### Python environments

We highly recommend the use of conda (or mamba) which is the preferred way of installing and using snakemake.
Creation of required environments is done automatically in this case (with the `--software-deployment-method conda` flag).

#### MRIOTs

Most MRIOTs used can be downloaded automatically, but EORA26 requires an account.
Thus you need to download the zip files from their [website](https://worldmrio.com/eora26/)
and put them in the `mriot_data/downloaded/` folder for each year you are using.

Everything else should be already present or automatically downloaded by default.

#### Computing power

Depending on the simulation length and the MRIOT used, computing requirement vary a lot.
But using the default values/scenario present in this repository (for the non-test case)
requires a cluster of at the very least a computing server.

A simulation with a complete MRIOT takes around 45 minutes and require 12-24Go of RAM.
The `germany21` scenario amounts to ~2000 simulations, and about 500Go of output files.

Resources requirements specification are very conservative so it is possible some simulation
fail due to too high memory requirements. You may want to use the flag `--set-resources rule:mem_mb_per_cpu=<higher amount or ram>` in
such case (for instance `--set-resources simulate:mem_mb_per_cpu=24000`).

For high number of runs, this can also be a problem for the collection, aggregation and
treatment of results. I use `--set-resources prep_plot_df:mem_mb_per_cpu=128000 regroup_parquet_to_common_aggreg:mem_mb_per_cpu=128000` for the `germany21` scenario.

### Outputs

#### Output folder

By default every files produced by the pipeline are stored within the root folder of the pipeline or in a sub-directory (`results` for instance).
You can change this behavior by telling snakemake to output to another place:

`snakemake <rule> --directory /path/to/whereever/`

Due to the way Snakemake works, it will also look for configuration in that folder
so you have to use the `--configfile ./config/config.yaml` flag in this case.

Note that in this case, the MRIOTs data will also be stored relative to this path. And you have to put the EORA26 zip in this path.

#### Simulation space

The simulation space created based on the configuration files is saved in a `simulation_space.csv` file in the output folder.
You should not edit this file, but it may be used to keep track of what simulations are required.

Likewise the pipeline also creates a `flood_scenarios.csv` file.

#### Raw simulation outputs

Simulation results are stored under `results/simulations/` and follow a folder pattern corresponding to the different variable part of the simulations:

`"results/simulations/flood_scenario~germany21/mriot~euregio_2010_full_sectors_full_regions/sectors_scenario~default/recovery_scenario~reclin_730/order~alt_psi~0.95_base_alpha~1_max_alpha~1.25_tau_alpha~365/"`

In these folders are:

- a `parquets` sub-folder which contains each saved variable timeseries as parquet files such as `production_realised.parquet`.
- a `jsons` sub-folder which notably contains json files with the event actually simulated, and the parameters used (for consistency check).
- a `sim.done` empty flag file only relevant to the pipeline

#### Aggregated results

The raw outputs are processed to first generate a `results/common_aggreg.parquet`. This file regroups results from **ALL** simulations
after having aggregated them to a common aggregation. It is a DataFrame with all variable parts / scenarios / MRIOTs as index in addition to each time-step, and all (region,sectors) as columns.

This file is then post-processed (basically renaming/restructuring and some indicator computing) to create
`results/general-plot_df.parquet` (global) and `results/local-plot_df.parquet` (per region), which are easier to use for plotting.

#### Post pipeline processing and plotting

Two notebooks are included which can be used to further process the results and plots graphs:

- `Treat_raw_data.ipynb`
- `Plot_figures`

Their content should be self-explanatory.

### Overall pipeline structure

The pipeline mostly follows conventional snakemake structure:

```
├── .gitignore
├── README.md
├── LICENSE.md
├── workflow
│   ├── rules                        # Pipeline recipe files
|   │   ├── prepare_simspace.smk     #   Rules to create simulation space
|   │   ├── simulations.smk          #   Rules to run simulations
|   │   ├── treat_results.smk        #   Rules to collect and aggregate results
|   │   └── report.smk               #   [WIP] Rules to put results online
│   ├── envs
|   │   ├── global.yml               # Dependencies for global pipeline
|   │   ├── BoARIO-sensi.yml         # Dependencies for most rules
|   │   └── BoARIO-sensi-report.yaml # Dependencies for the put results online part
│   ├── scripts                      # Scripts called by the pipeline
|   │   ├── create_flood_scenarios_csv.py
|   │   ├── create_simspace_csv.py
|   │   ├── generate_local_results_rst.py
|   │   ├── generate_mrio_compare.py
|   │   ├── generate_results_index_rst.py
|   │   ├── generate_results_rst.py
|   │   ├── plot_results.py
|   │   ├── prep_plot_df.py
|   │   ├── regroup_aggreg.py
|   │   └── simulate.py
│   ├── Snakefile                    # Pipeline entrypoint
├── config
│   ├── config.yaml
└── results                          # Where results are stored
```

### Example of use

Run a dry-run:

- `snakemake results/general-plot_df.parquet -cores 1 --sdm conda --config testing=False --dry-run`

Test pipeline with one core:

- `snakemake results/general-plot_df.parquet -cores 1 --sdm conda  --config testing=False`

Run for intermediate files/rule:

- `snakemake create_simspace_csv -c1 --sdm conda --config testing=False` to build the simulation space csv file
- `snakemake all_mriots -c1 --sdm conda --config testing=False` to download/parse/aggregate all MRIOTs
- `snakemake "results/simulations/flood_scenario~germany21/mriot~euregio_2010_full_sectors_full_regions/sectors_scenario~default/recovery_scenario~reclin_730/order~alt_psi~0.95_base_alpha~1_max_alpha~1.25_tau_alpha~365/parquets/production_realised.parquet" -c1 --sdm conda --config testing=False` to run one specific simulation

Run on a cluster, assuming you have a snakemake profile configuration named `slurm` (and the cluster runs SLURM):

`sbatch --time=2-1 --wrap "snakemake results/general-plot_df.parquet --profile slurm --config testing=False --directory <wherever> --configfile ./config/config.yaml --set-resources prep_plot_df:mem_mb_per_cpu=128000 regroup_parquet_to_common_aggreg:mem_mb_per_cpu=128000 regroup_parquet_to_common_aggreg:runtime=240 simulate:mem_mb_per_cpu=32000 --cores 1"`

Here the command is wrapped in a 2 days job to avoid having to keep an active session.
