*************************
Simulations Report
*************************

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
   :file: ../../config/flood_scenarios_readable.csv
   :widths: 10 10 10 10 30 30
   :header-rows: 1

Recovery/rebuilding scenarios
--------------------------------

Here are the different scenarios for recovery/rebuilding we test. The term ``recovery`` means that reconstitution
of productive capital is not accompanied by a corresponding demand in the model, whereas ``rebuilding`` means
productive capital is regained via the answer to a ``rebuilding demand``, governed by a characteristic time.

.. note::
   The choice of the sectors answering rebuilding demand is part of the "sectors scenario"

.. csv-table:: List of the flood scenarios tested
   :file: ../../config/recovery_scenarios_readable.csv
   :widths: 10 40 10 40
   :header-rows: 2


Sectors scenarios
-------------------

Here are the configuration for the sectors we use across the different MRIOT. The initial choices are made on Exiobase3 and the values for Eora26 and Euregio are according to sectors correspondence.

- If ``affected`` is true/1, then the sectors loses productive capital following the flood.

- ``rebuilding_factor`` denotes which share of the rebuilding demand the sector will have to answer

- ``inventory_size`` denotes the initial size of the inventory of inputs of the specified sector (e.g. if ``Agriculture`` is 90, then all sectors will store 90 days worth of inputs of ``Agriculture`` )

- ``kapital_to_va_ratio`` is the factor used to estimate productive capital from the VA of the sector

- ``inventory_tau`` is the inventory restoration characteristic time

Note that default values are from Hallegatte2013

.. collapse:: Exiobase3 default configuration

  .. csv-table::
     :file: ../../config/exiobase3_full_sectors.csv
     :widths: 50 5 10 10 15 10
     :header-rows: 1

.. collapse:: Eora26 default configuration

  .. csv-table::
     :file: ../../config/eora26_full_sectors.csv
     :widths: 50 5 10 10 15 10
     :header-rows: 1

.. collapse:: Euregio default configuration

  .. csv-table::
     :file: ../../config/euregio_full_sectors.csv
     :widths: 50 5 10 10 15 10
     :header-rows: 1

Simulation names scheme
--------------------------

We use the following naming scheme for simulations in the results.

    {sector scenario}~{recovery scenario}~{flood scenario}~{order parameter}~{psi parameter value}~{alpha max value}~{alpha tau value}~{mriot used}

For example:

    reb15~0.5~30~eora26_full_2000

    is the simulation using ``reb15`` rebuilding scenario, ``psi=0.5``, ``alpha_tau=30`` and the year 2000 Eora26 table. (At the moment sector and flood scenario, as well as order, alpha max do not vary across simulations)

.. important::
   As these name can be long and we often compare simulations sharing the same value for one or more of these part, we often show just the
   part that differs between simulations.
