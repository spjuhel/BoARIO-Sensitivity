**********************
Simulations Report
**********************

Simulations overview
==========================


MRIO Table tested
--------------------


.. list-table:: List of the MRIOT compared and their characteristics.
    :widths: 10 10 30 30 20
    :header-rows: 1

    * - Name
      - Number of sectors
      - Number of regions
      - Other characteristics
      - Source

    *  - Exiobase 3
       - 163
       - 49 = 44 Countries + 5 rest of the world regions
       - Basic prices, 10^6€
       - .. image:: https://zenodo.org/badge/DOI/10.5281/zenodo.5589597.svg
                      :target: https://doi.org/10.5281/zenodo.5589597

    *  - Euregio
       - 14
       - 264 = 247 UE NUTS2 regions + 16 Countries + 1 Rest of the world
       - WIOD based, with NUTS2 regional disagregation for EU, 10^6€
       - http://data.europa.eu/89h/84356c3b-104d-4860-8ce3-075d2eab37ab
    *
       - Eora 26
       - 26
       - 189
       - Basic prices, 10^3$
       - https://worldmrio.com/eora26/

Flood scenarios
------------------

.. csv-table:: List of the flood scenarios tested
   :file: tables/flood_scenarios.csv
   :widths: 10 10 10 10 30 30
   :header-rows: 1

Recovery/rebuilding scenarios
--------------------------------

.. csv-table:: List of the recovery/rebuilding scenarios tested
   :file: tables/recovery_scenarios.csv
   :widths: 10 10 10 10 30 30
   :header-rows: 1

Sectors scenarios
-------------------

.. csv-table:: List of the recovery/rebuilding scenarios tested
   :file: tables/recovery_scenarios.csv
   :widths: 10 10 10 10 30 30
   :header-rows: 1

Simulation names scheme
--------------------------

We use the following naming scheme for simulations.

    {sector scenario}~{recovery scenario}~{flood scenario}~{order parameter}~{psi parameter value}~{alpha max value}~{alpha tau value}~{mriot used}

.. important::
   As these name can be long and we often compare simulations sharing the same value for one or more of these part, we often show just the
   part that differs between simulations.

Comparison process
====================

*How we aggregate results to have them comparable*

We run the simulation with each MRIOT typology. But in order to compare readable results we aggregate
to a select set of regions and sectors. The reasoning behind the aggregation as well as the mapping for each MRIOT
is presented in the supplementary materials.

Region aggregation
----------------------

We aggregate/select to ``DEU, FRA, CHN, USA`` and a rest of the world ``ROW`` region.

Sector aggregation
----------------------

We aggregate the  to 6 sectors, namely:

- Agriculture and Other
- Construction
- Energy and Utilities and Mining
- Manufacture
- Sales, Transports and Services
- Others
