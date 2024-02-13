import re

ORDER_TYPE_REGEX = r"(?P<order>alt|noalt)"
PSI_REGEX = r"(?P<psi>1|0\.\d+)"
BASE_ALPHA_REGEX = r"(?P<base_alpha>\d(?:\.\d+)?)"
MAX_ALPHA_REGEX = r"(?P<max_alpha>\d(?:\.\d+)?)"
TAU_ALPHA_REGEX = r"(?P<tau_alpha>\d+)"

MRIOT_BASENAME_REGEX = r"(?P<mrio_basename>icio2021|euregio|exiobase3_ixi|eora26)"
MRIOT_YEAR_REGEX = r"(?P<mrio_year>\d{4})"
MRIOT_AGGREG_REGEX = r"(?P<mrio_aggreg>full|\d+_sectors|common_aggreg)"
MRIOT_FULLNAME_REGEX = re.compile(r"""
{MRIOT_BASENAME_REGEX} # MRIOT basename
_ #
{MRIOT_YEAR_REGEX} # MRIOT year
_ #
{MRIOT_AGGREG_REGEX} # Aggregation specification
""".format(MRIOT_BASENAME_REGEX=MRIOT_BASENAME_REGEX,
           MRIOT_YEAR_REGEX=MRIOT_YEAR_REGEX,
           MRIOT_AGGREG_REGEX=MRIOT_AGGREG_REGEX),re.VERBOSE)

SIMULATION_PATH_REGEX = re.compile(r"""
results/simulations/mrio~{MRIOT_BASENAME_REGEX}  #
_                                                #
{MRIOT_YEAR_REGEX}                               #
_                                                #
{MRIOT_AGGREG_REGEX} # Aggregation specification #
/                                                #
sectors_scenario~(?P<sectors_scenario>[^/]+)     #
/                                                #
recovery_scenario~(?P<recovery_scenario>[^/]+)   #
/                                                #
flood_scenario~(?P<flood_scenario>[^/]+)         #
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
