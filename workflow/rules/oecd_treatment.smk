ruleorder: preparse_oecd_v2021 > aggregate_oecd


rule aggregate_oecd:
    input:
        mrio_pkl="mrio-files/pkls/oecd_v2021/oecd_v2021_full_{year}.pkl",
        aggreg="aggregation-files/oecd_v2021/oecd_v2021_{aggregation}.csv",
    output:
        "mrio-files/pkls/oecd_v2021/oecd_v2021_{aggregation}_{year}.pkl",
    conda:
        "../envs/BoARIO-sensi.yml"
    log:
        "logs/aggregate_oecd_v2021/aggregate_oecd_v2021_{aggregation}_{year}.log",
    script:
        "../scripts/aggregate_oecd_v2021.py"


rule preparse_oecd_v2021:
    input:
        "mrio-files/csvs/oecd_v2021/ICIO2021_{year}.csv",
    output:
        "mrio-files/pkls/oecd_v2021/oecd_v2021_full_{year}.pkl",
    conda:
        "../envs/BoARIO-sensi.yml"
    log:
        "logs/preparse_oecd_v2021/preparse_oecd_v2021_{year}.log",
    resources:
        mem_mb=6000,
    benchmark:
        "benchmarks/mrios/preparse_oecd_v2021_{year}.log"
    script:
        "../scripts/preparse_oecd_v2021.py"


rule download_oecd_v2018_test:
    input:
        "autodownloads/oecd/ICIO2021_2006.zip",


# rule download_oecd_v2018:
#     output:
#         "autodownloads/oecd_v2018/ICIO2018_{year}.zip"
#     conda:
#         "../envs/BoARIO-sensi.yml"
#     log:
#         "logs/download_oecd_v2018/download_oecd_v2018_{year}.log"
#     script:
#         "../scripts/download_oecd_v2018.py"


rule extract_oecd2021_2000_2004:
    input:
        zipfile="autodownloads/oecd/ICIO_2000-2004.zip",
    params:
        folder="mrio-files/csvs/oecd_v2021/",
    output:
        expand(
            "mrio-files/csvs/oecd_v2021/ICIO2021_{years}.csv",
            years=[2000, 2001, 2002, 2003, 2004],
        ),
    log:
        "logs/download_euregio/download_euregio_2000-2004.log",
    run:
        with zipfile.ZipFile(input.zipfile, "r") as zip_ref:
            zip_ref.extractall(params.folder)


rule extract_oecd2021_1995_1999:
    input:
        zipfile="autodownloads/oecd/ICIO_1995-1999.zip",
    params:
        folder="mrio-files/csvs/oecd_v2021/",
    output:
        expand(
            "mrio-files/csvs/oecd_v2021/ICIO2021_{years}.csv",
            years=[1995, 1996, 1997, 1998, 1999],
        ),
    log:
        "logs/download_euregio/download_euregio_1995-1999.log",
    run:
        with zipfile.ZipFile(input.zipfile, "r") as zip_ref:
            zip_ref.extractall(params.folder)


rule extract_oecd2021_2005_2009:
    input:
        zipfile="autodownloads/oecd/ICIO_2005-2009.zip",
    params:
        folder="mrio-files/csvs/oecd_v2021/",
    output:
        expand(
            "mrio-files/csvs/oecd_v2021/ICIO2021_{years}.csv",
            years=[2005, 2006, 2007, 2008, 2009],
        ),
    log:
        "logs/download_euregio/download_euregio_2005-2009.log",
    run:
        with zipfile.ZipFile(input.zipfile, "r") as zip_ref:
            zip_ref.extractall(params.folder)


# For the year range 2010-2014
rule extract_oecd2021_2010_2014:
    input:
        zipfile="autodownloads/oecd/ICIO_2010-2014.zip",
    params:
        folder="mrio-files/csvs/oecd_v2021/",
    output:
        expand(
            "mrio-files/csvs/oecd_v2021/ICIO2021_{years}.csv",
            years=[2010, 2011, 2012, 2013, 2014],
        ),
    log:
        "logs/download_euregio/download_euregio_2010-2014.log",
    run:
        with zipfile.ZipFile(input.zipfile, "r") as zip_ref:
            zip_ref.extractall(params.folder)


# For the year range 2015-2018
rule extract_oecd2021_2015_2018:
    input:
        zipfile="autodownloads/oecd/ICIO_2015-2018.zip",
    params:
        folder="mrio-files/csvs/oecd_v2021/",
    output:
        expand(
            "mrio-files/csvs/oecd_v2021/ICIO2021_{years}.csv",
            years=[2015, 2016, 2017, 2018],
        ),
    log:
        "logs/download_euregio/download_euregio_2015-2018.log",
    run:
        with zipfile.ZipFile(input.zipfile, "r") as zip_ref:
            zip_ref.extractall(params.folder)


rule download_extract_oecd2021:
    input:
        zipfile=HTTPS.remote(
            "stats.oecd.org/wbos/fileview2.aspx",
            keep_local=True,
            additional_request_string="?IDFile=8adf89dd-18b4-40fe-bc7f-c822052eb961",
        ),
    params:
        folder="autodownloads/oecd/",
    output:
        expand(
            "autodownloads/oecd/ICIO2021_{years}.csv",
            years=[2000, 2001, 2002, 2003, 2004],
        ),
    log:
        "logs/download_euregio/download_euregio.log",
    run:
        for inp in input:
            with zipfile.ZipFile(inp, "r") as zip_ref:
                zip_ref.extractall(params.folder)


rule oecd_sector_config:
    input:
        exio3_sectors_config="config/exiobase3_full_sectors.csv",
        aggregation_master="config/exiobase3_to_other_mrio_sectors.ods",
    output:
        "config/oecd_v2021_full_sectors.csv",
    conda:
        "../envs/BoARIO-sensi.yml"
    params:
        mrio_type="oecd_v2021",
    script:
        "../scripts/params_gen_from_exiobase3_full.py"
