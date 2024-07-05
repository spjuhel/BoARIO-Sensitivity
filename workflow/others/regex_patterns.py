import re
from boario_tools.regex_patterns import (
    BASE_ALPHA_REGEX,
    MAX_ALPHA_REGEX,
    MRIOT_AGGREG_REGEX,
    MRIOT_BASENAME_REGEX,
    ORDER_TYPE_REGEX,
    PSI_REGEX,
    MRIOT_YEAR_REGEX,
    TAU_ALPHA_REGEX
)

SIMULATION_PATH_REGEX = re.compile(r"""
results/simulations/                             #
flood_scenario~(?P<flood_scenario>[^/]+)         #
/                                                #
mriot~{MRIOT_BASENAME_REGEX}                     #
_                                                #
{MRIOT_YEAR_REGEX}                               #
_                                                #
{MRIOT_AGGREG_REGEX} # Aggregation specification #
/                                                #
sectors_scenario~(?P<sectors_scenario>[^/]+)     #
/                                                #
recovery_scenario~(?P<recovery_scenario>[^/]+)   #
/                                                #
order~{ORDER_TYPE_REGEX}                         #
_                                                #
psi~{PSI_REGEX}                                  #
_                                                #
base_alpha~{BASE_ALPHA_REGEX}                    #
_                                                #
max_alpha~{MAX_ALPHA_REGEX}                      #
_                                                #
tau_alpha~{TAU_ALPHA_REGEX}                      #
""".format(MRIOT_BASENAME_REGEX=MRIOT_BASENAME_REGEX,
           MRIOT_YEAR_REGEX=MRIOT_YEAR_REGEX,
           MRIOT_AGGREG_REGEX=MRIOT_AGGREG_REGEX,
           ORDER_TYPE_REGEX = ORDER_TYPE_REGEX,
           PSI_REGEX = PSI_REGEX,
           BASE_ALPHA_REGEX = BASE_ALPHA_REGEX,
           MAX_ALPHA_REGEX = MAX_ALPHA_REGEX,
           TAU_ALPHA_REGEX = TAU_ALPHA_REGEX
           ),re.VERBOSE)
