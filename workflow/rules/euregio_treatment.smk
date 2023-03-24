import os
import zipfile
import shutil
from snakemake.remote.HTTP import RemoteProvider as HTTPRemoteProvider

HTTPS = HTTPRemoteProvider()

OFFICE_BIN = shutil.which("libreoffice")
if OFFICE_BIN is not None:
    OFFICE_EXISTS = True
else:
    OFFICE_EXISTS = False

if shutil.which("unoserver") is not None:
    UNOSERVER_EXISTS = False
else:
    UNOSERVER_EXISTS = False

rule start_unoserver:
    params:
        office = OFFICE_BIN
    log:
        "logs/unoserver.log"
    output:
        service("unoserver")
    shell:
        "unoserver --executable {params.office} 2> {log}; sleep 10000"

rule preparse_euregio:
    input:
        "mrio-files/csvs/euregio/euregio_{year}.csv"
    output:
        "mrio-files/pkls/euregio/euregio_full_{year}.pkl"
    conda:
        "../envs/BoARIO-sensi.yml"
    log:
        "logs/preparse_euregio/preparse_euregio_{year}.log"
    script:
        "../scripts/preparse_euregio.py"

rule create_euregio_xlsx:
    input:
        inp_file = "autodownloads/euregio/EURegionalIOtable_{year}.ods"
    params:
        folder = "autodownloads/euregio",
        office_exists = OFFICE_EXISTS,
        uno_exists = UNOSERVER_EXISTS
    resources:
        libre_office_instance=1
    output:
        "autodownloads/euregio/EURegionalIOtable_{year}.xlsx"
    log:
        "logs/preparse_euregio/convert_euregio_xlsx_{year}.log"
    script:
        "../scripts/euregio_convert_xlsx.py"

rule create_euregio_csvs:
    input:
        "autodownloads/euregio/EURegionalIOtable_{year}.xlsx"
    output:
        "mrio-files/csvs/euregio/euregio_{year}.csv"
    shell:
        """
        xlsx2csv -s 3 {input} {output}
        """

rule download_extract_euregio:
    input:
        first = HTTPS.remote("dataportaal.pbl.nl/downloads/PBL_Euregio/PBL-EUREGIO-2000-2005-ODS.zip", keep_local=True),
        second = HTTPS.remote("dataportaal.pbl.nl/downloads/PBL_Euregio/PBL-EUREGIO-2006-2010-ODS.zip", keep_local=True)
    params:
        folder = "autodownloads/euregio/"
    output:
        expand("autodownloads/euregio/EURegionalIOtable_{years}.ods",years=[2000,2001,2002,2003,2004,2005,2006,2007,2008,2009,2010])
    log:
        "logs/download_euregio/download_euregio.log"
    run:
        for inp in input:
            with zipfile.ZipFile(inp, 'r') as zip_ref:
                zip_ref.extractall(params.folder)

rule euregio_sector_config:
    input:
        exio3_sectors_config="config/exiobase3_full_sectors.csv",
        aggregation_master="config/exiobase3_to_other_mrio_sectors.ods"
    output:
        "config/euregio_full_sectors.csv"
    conda:
        "../envs/BoARIO-sensi.yml"
    params:
        mrio_type="euregio"
    script:
        "../scripts/params_gen_from_exiobase3_full.py"
