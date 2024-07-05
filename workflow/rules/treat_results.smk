checkpoint prep_plot_df:
    input:
        "results/common_aggreg.parquet",
    output:
        "results/{scope}-plot_df.parquet",
    log:
        "logs/prep_{scope}-plot_df.log",
    threads: 4
    resources:
        mem_mb_per_cpu=3000,
    benchmark:
        "benchmarks/prep_{scope}-plot_df.log"
    conda:
        "../envs/BoARIO-sensi.yml"
    script:
        "../scripts/prep_plot_df.py"


def regroup_input(wildcards):
    dico = {
        var: expand(
            "results/simulations/{params}/parquets/" + var + ".parquet",
            params=paramspace.instance_patterns,
        )
        for var in config["variables"]
    }
    return dico


rule regroup_parquet_to_common_aggreg:
    input:
        unpack(regroup_input),
    output:
        "results/common_aggreg.parquet",
    log:
        f"logs/regroup_aggreg.log",
    params:
        alt_aggregation_master = None,
        sectors_aggreg_ods=None,
        regions_aggreg_ods=None,
        sheet_names={
            "regions":{
                "exiobase3_ixi":"exiobase3_ixi_full_regions_to_common_aggreg",
                "eora26":"eora26_full_regions_to_common_aggreg",
                "euregio":"euregio_full_regions_to_common_aggreg",
            },
            "sectors":{
                "exiobase3_ixi":"exiobase3_ixi_full_sectors_to_common_aggreg",
                "eora26":"eora26_full_no_reexport_sectors_to_common_aggreg",
                "euregio":"euregio_full_sectors_to_common_aggreg",
            }
        }

    threads: 4
    benchmark:
        f"benchmarks/regroup_aggreg.log"
    conda:
        "../envs/BoARIO-sensi.yml"
    script:
        "../scripts/regroup_aggreg.py"
