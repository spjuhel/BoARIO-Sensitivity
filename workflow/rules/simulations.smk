def inpt_all_parquets(wildcards):
    return expand(
            "results/simulations/{params}/parquets/{var}.parquet",
            params=paramspace.instance_patterns,
            var=config["variables"],
        )

rule all_parquets:
    input:
        inpt_all_parquets

def get_simulation_inputs(wildcards):
    mrio_name = wildcards.mriot
    sectors_scenario = wildcards.sectors_scenario
    filepath = (
        config["data-mriot"]["prefix"] + config["data-mriot"]["parsed_mriot_dir"]
    )  # the path to the pickle files
    regex = mriot_tools_snake.MRIOT_FULLNAME_REGEX
    match = regex.match(mrio_name)  # match the filename with the regular expression
    if not match:
        raise ValueError(f"The file name {mrio_name} is not valid.")
    mriot_prefix, year, aggreg_sectors, aggreg_regions = (
        match.groups()
    )  # get the prefix and year from the matched groups
    fullpath = (
        filepath + "/" + mriot_prefix + "/" + mrio_name + ".pkl"
    )  # create the full file path

    parsed=config["data-mriot"]["parsed_mriot_dir"]

    sectors_config_path = (
        config["data-mriot"]["prefix"] + config["data-mriot"]["mriot_params_dir"] +
        "/" + mriot_prefix + "_" + aggreg_sectors +
        ".csv")

    return {
        "flood_scenarios":"flood_scenarios.csv",
        "mrio": fullpath,
        "sectors_config": sectors_config_path
    }


rule simulate:
    input:
        unpack(get_simulation_inputs),
    output:
        # format a wildcard pattern like "alpha~{alpha}/beta~{beta}/gamma~{gamma}"
        # into a file path, with alpha, beta, gamma being the columns of the data frame
        output_dir=directory(f"results/simulations/{paramspace.wildcard_pattern}"),
        parquet_files=[
            f"results/simulations/{paramspace.wildcard_pattern}/parquets/"
            + var
            + ".parquet"
            for var in config["variables"]
        ],
        json_files=[
            f"results/simulations/{paramspace.wildcard_pattern}/jsons/"
            + json
            + ".json"
            for json in [
                "indexes",
                "equilibrium_checks",
                "simulated_events",
                "simulated_params",
            ]
        ],
        #.format(paramspace.wildcard_pattern,"{files}"), files=["indexes","equilibrium_checks","simulated_events","simulated_params"]),
        done=touch(f"results/simulations/{paramspace.wildcard_pattern}/sim.done"),
    params:
        # automatically translate the wildcard values into an instance of the param space
        # in the form of a dict (here: {"alpha": ..., "beta": ..., "gamma": ...})
        simulation_params=paramspace.instance,
        sim_length=config["sim_length"],
    log:
        f"logs/simulations/{paramspace.wildcard_pattern}.log",
    threads: 2
    benchmark:
        f"benchmarks/simulations/{paramspace.wildcard_pattern}.log"
    resources:
        mem_mb_per_cpu=10000,
        runtime=240,
    conda:
        "../envs/BoARIO-sensi.yml"
    script:
        "../scripts/simulate.py"
