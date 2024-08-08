# Workflow configuration

Configuration is done via the `config` folder content.

It requires a `config.yaml` file, and at least one `flood_scenarios/<flood-scenario>.yaml` file and one `simulations/<simulation-scenario>.yaml`, which are described in following sections. The GitHub repository contains examples of such files that should be used as templates.

It also requires a `mriot_params` directory for the MRIOT handling sub-module for which you can find documentation [here](https://github.com/spjuhel/BoARIO-MRIOT-Tools).

## `config.yaml`

This file governs the high-level configuration of the pipeline (i.e. paths, notably to other configurations files, experiences to run, variables to store, etc.)

### Testing

To enforce testing before using the pipeline the file contains a `testing: True` statement, which we suggest you keep and override when running the pipeline by using the `--config testing=False` flag when invoking snakemake.


create_flood_scenarios_csv.py
create_simspace_csv.py
generate_local_results_rst.py
generate_mrio_compare.py
generate_results_index_rst.py
generate_results_rst.py
plot_results.py
prep_plot_df.py
regroup_aggreg.py
simulate.py

### MRIOT-Tools sub-module configuration

This part of the configuration give the required details for the MRIOTs-Tools sub-module and essentially governs
where MRIOTs data should be looked for and stored. We suggest to keep it as is in most cases.

- `prefix` is the sub-directory of the pipeline global output which contains everything related to the sub-module. This is where the sub-module looks for configuration files and where it store the MRIOTs data.
- `XXX_dir` are the sub-sub-folders where corresponding data is to be found/stored
- `common_aggreg` is the name of the aggregation common to all MRIOTs
- `mriot_base_aggreg` is the name of the initial, not aggregated MRIOT for each table type.

```
data-mriot:
  prefix: "mriot_data/"
  downloaded_mriot_dir: "downloaded"
  parsed_mriot_dir: "parsed"
  aggregated_mriot_dir: "parsed"
  mriot_params_dir: "config/mriot_params"

  common_aggreg: "common_sectors_common_regions"
  mriot_base_aggreg:
    exiobase3_ixi : "full_sectors_full_regions"
    exiobase3_pxp : "full_sectors_full_regions"
    eora26: "full_no_reexport_sectors_full_regions"
    euregio: "full_sectors_full_regions"

```

### Scenarios files

Next the file should define the scenarios to run, for instance:

```
flood scenario: flood_scenarios/germany21.yaml
simulation space test: simulations/test.yaml
simulation space: simulations/germany21.yaml
```

#### Flood scenarios

Flood scenarios define the direct impact for each MRIOTs. Format is the following:

```
name: <name of the scenario>

year: <year of the impact>
unit: <monetary unit> ("euro", "dollar", ...)
prod_cap_impact_unit: <unit value of impact on productive capital>
house_impact_unit:    <unit value of impact on households capital> (Can be 0)
estimated_gdp_unit:   <unit value of GDP of the whole region impacted> Used to translate the impact in relative terms

duration: <duration of the event>

# name of the country affected in each of the MRIOTs
countries_affected:
  exiobase3_ixi: "DE"
  eora26: "DEU"
  euregio: "DE"

# name of the regions affected in each of the MRIOTs : share of the impact
# this is mainly for euregio where there subregions are impacted
# should also have a "common" element if you wish to run simulation on
# the aggregated version of the MRIOTs
regions_affected:
  exiobase3_ixi:
    "DE": 1.
  eora26:
    "DEU" : 1.
  euregio:
    'DE21' : 0.00137977016177574
    'DE22' : 0.00137977016177574
    'DE23' : 0.00137977016177574
    [...]
  common:
    "DEU" : 1.

# How the impact is distributed towards the impacted sectors
productive_capital_impact_sectoral_distrib_type: gdp
```

#### Sector scenarios

Currently only one sector scenario can be run per pipeline run, in the future, multiple scenario will be possible.

The scenario is defined based on the `exiobase3_ixi_full_sectors.csv` file, located in the
`config/mriot_base_scenarios/` folder by default (which can be changed with the `mriot_base_config`
attribute in the `config.yaml` file). Note that for user-friendliness this file is automatically copied
to MRIOT-Tools sub-module data folder.

We use EXIOBASE 3 as a `baseline`, has it has the most sectors, then values for other tables are automatically computed
by following a consistent sector mapping. The aggregation mapping used can be found
[here](https://github.com/spjuhel/BoARIO-Tools/tree/main/boario_tools/data/aggregation_files/exiobase3_ixi).

This "main" csv file should contain:

- a first columns with all 163 sectors of EXIOBASE 3
- an `affected` column with 0 or 1 depending if the sector is impacted or not. Note that sectors in other MRIOTs that correspond to multiple sectors and where least one is affected, will be considered affected, which can produce inconsistencies. Refer to the aggregation file used.
- a `rebuilding_factor` column which states the contribution of the sector to the reconstruction effort (0 meaning it does not contribute). The column has to sum up to 1.0
- an `inventory_size` column with either a number of day or "Infinity". A number states the number of days worth, relative to production requirements, of input produced by the sector, that are aimed to be in the stocks of any industry. That is, `90` for `Cultivation of wheat` means all industries "store" the equivalent of 90 times what they requirefrom this sector to produce for one day. "Infinity" means that input from this sectors are not considered as a constraint to production.
- a `productive_capital_to_va_ratio` column which states how much productive capital to estimate from the Value Added of the sector.
- an `inventory_tau` column which state the characteristic time to resupply inputs from this sector.

#### Simulation scenarios

Defines the simulation space, which will be a Cartesian product of each possibility.

```

flood_scenario: # Flood scenarios to run (needs to match a yaml file in flood_scenarios/)
  - germany21

mriot: # The MRIOTs to run
  - exiobase3_ixi
  - eora26
  - euregio

mriot_year: # The MRIOTs years to run
  - 2000
  - 2010

# The type of aggregation to use (mostly full_sectors_full_regions is relevant,
# the two other possibilities are to evaluate the effect of differences in sector/region typologies)
mriot_aggreg:
  - full_sectors_full_regions
  - common_sectors_common_regions
  - common_sectors_full_regions

# Required but currently unused, placeholder for future use.
sectors_scenario:
  - default

# Recovery scenarios to run
recovery_scenario:
  - reclin
  - reb

recovery_tau:
  - 90
  - 180
  - 365
  - 545
  - 730

# Parameters used for the BoARIO model (see its documentation)

order:
  - alt

psi:
  - 0.5
  - 0.8
  - 0.85
  - 0.90
  - 0.95
  - 0.97
  - 1.0

base_alpha:
  - 1

max_alpha:
  - 1.25

tau_alpha:
  - 1
  - 90
  - 180
  - 365
  - 730

```
