rule aggregate_exiobase3:
    input:
        mrio_pkl="mrio-files/pkls/exiobase3/exiobase3_full_{year}_{system}.pkl",
        aggreg="aggregation-files/exiobase3/exiobase3_{aggregation}.csv",
    params:
        full_mrio_params="mrio-files/params/exiobase3/exiobase3_full_params.csv",
    output:
        "mrio-files/pkls/exiobase3/exiobase3_{aggregation}_{year}_{system}.pkl",
    conda:
        "../envs/BoARIO-sensi.yml"
    log:
        "logs/aggregate_exiobase3/aggregate_exiobase3_{aggregation}_{year}_{system}.log",
    benchmark:
        "benchmarks/mrios/aggregate_exiobase3_{aggregation}_{year}_{system}.log"
    script:
        "../scripts/aggregate_exiobase3.py"


rule preparse_exiobase3:
    input:
        "autodownloads/exiobase3/IOT_{year}_{system}.zip",
    output:
        "mrio-files/pkls/exiobase3/exiobase3_full_{year}_{system}.pkl",
    conda:
        "../envs/BoARIO-sensi.yml"
    log:
        "logs/preparse_exiobase3/preparse_exiobase3_{year}_{system}.log",
    resources:
        mem_mb=6000,
    benchmark:
        "benchmarks/mrios/preparse_exiobase3_{year}_{system}.log"
    script:
        "../scripts/preparse_exiobase3.py"


rule download_exiobase3_test:
    input:
        "autodownloads/exiobase3/IOT_1995_ixi.zip",


rule download_exiobase3:
    output:
        "autodownloads/exiobase3/IOT_{year}_{system}.zip",
    conda:
        "../envs/BoARIO-sensi.yml"
    log:
        "logs/download_exiobase3/download_exiobase3_{year}_{system}.log",
    script:
        "../scripts/download_exiobase3.py"
