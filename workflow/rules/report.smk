localrules:
    make_rst_report,

rule make_rst_report:
    input:
        expand(
            "report/source/results-pages/{focus}-results.rst",
            focus=config["focus"].keys(),
        ),
    output:
        touch("report/report_pushed"),
    conda:
        "../envs/boario-sensi-report.yml"
    shell:
        """
        git add report/source;
        git add report/images;
        git commit -m "update results from workflow";
        git push;
        """


rule make_all_focus_results:
    input:
        local_rst=expand(
            "report/source/results-pages/results-contents/local-{{focus}}-{selection_type}-{faceting}-results.rst",
            selection_type=["recovery_sce"],
            faceting=["Experience~mrio"],
        ),
        general_rst=expand(
            "report/source/results-pages/results-contents/general-{{focus}}-{selection_type}-{faceting}-results.rst",
            selection_type=["cumsum_impact_class"],
            faceting=["sectorXregion~Experience"],
        ),
    params:
        variables=config["variables"],
    output:
        "report/source/results-pages/{focus}-results.rst",
    log:
        "logs/make_rst_{focus}-results.log",
    conda:
        "../envs/boario-sensi-report.yml"
    script:
        "../scripts/generate_results_index_rst.py"


def get_grids(wildcards):
    grids = []
    df_path = checkpoints.prep_plot_df.get(**wildcards).output[0]
    plot_df = pd.read_parquet(df_path)
    if config["focus"][wildcards.focus] != "all":
        plot_df.query(config["focus"][wildcards.focus], inplace=True)
    selections = plot_df[wildcards.selection_type].sort_values().unique()
    grids += expand(
        "{dirs}/{scope}/{focus}/{selection_type}~{selection}/{faceting}/{variable}_{plot_type}.{ext}",
        dirs=["results/figs", "report/images/figs"],
        scope=wildcards.scope,
        selection_type=wildcards.selection_type,
        selection=selections,
        focus=wildcards.focus,
        faceting=wildcards.faceting,
        variable=config["variables"],
        plot_type=config["plot config"]["plot types"],
        ext="svg",
    )
    return grids


rule make_rst_result:
    input:
        plot_df="results/{scope}-plot_df.parquet",
        grids=get_grids,
    output:
        res_rst="report/source/results-pages/results-contents/{scope}-{focus}-{selection_type}-{faceting}-results.rst",
    params:
        variables=config["variables"],
    log:
        "logs/make_rst_results-{scope}-{focus}-{selection_type}-{faceting}.log",
    conda:
        "../envs/boario-sensi-report.yml"
    script:
        "../scripts/generate_results_rst.py"


rule plot_grid:
    input:
        plot_df="results/{scope}-plot_df.parquet",
    output:
        expand(
            "{dirs}/{{scope}}/{{focus}}/{{selection_type}}~{{selection}}/{{faceting}}/{{variable}}_{{plot_type}}.{{ext}}",
            dirs=["results/figs", "report/images/figs"],
        ),
    params:
        sharey=config["plot config"]["grid"]["sharey"],
        row_order=config["plot config"]["grid"]["row order"],
    log:
        "logs/plot_results-{scope}-{focus}-{selection_type}-{selection}-{faceting}-{variable}-{plot_type}_{ext}.log",
    threads: 4
    resources:
        mem_mb_per_cpu=4000,
    benchmark:
        "benchmarks/plot_results-{scope}-{focus}-{selection_type}-{selection}-{faceting}-{variable}-{plot_type}_{ext}.log"
    conda:
        "../envs/BoARIO-sensi.yml"
    script:
        "../scripts/plot_results.py"
