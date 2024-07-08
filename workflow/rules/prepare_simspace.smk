from itertools import product

simspace_file = Path(f"{workflow.basedir}/../config/{config['simulation space test']}").resolve()
with open(simspace_file) as stream:
    try:
        data = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)

keys = data.keys()
values = (data[key] if isinstance(data[key], list) else [data[key]] for key in keys)

# Generate all combinations
combinations = list(product(*values))

# Create a pandas DataFrame
df = pd.DataFrame(combinations, columns=keys)

df.loc[(df["mriot"]=="eora26") & (df["mriot_aggreg"]=="full_sectors_full_regions"),"mriot_aggreg"] = "full_no_reexport_sectors_full_regions"

df["mriot"] = df[["mriot","mriot_year","mriot_aggreg"]].apply(
        lambda row: f'{"_".join(row.values.astype(str))}',
        axis=1
)
df["recovery_scenario"] = df[["recovery_scenario","recovery_tau"]].apply(
    lambda row: "_".join(row.values.astype(str)),
    axis=1
)
df = df[["flood_scenario","mriot","sectors_scenario","recovery_scenario",
         "order",
         "psi",
         "base_alpha",
         "max_alpha",
         "tau_alpha",
         ]]
paramspace = Paramspace(
    df,
    filename_params=[
        "order",
        "psi",
        "base_alpha",
        "max_alpha",
        "tau_alpha",
    ],
)

checkpoint create_simspace_csv:
    input:
        simspace_file
    output:
        "simulation_space.csv"
    log:
        f"logs/create_simulation_space.log",
    benchmark:
        f"benchmarks/create_simulation_space.log"
    conda:
        "../envs/BoARIO-sensi.yml"
    script:
        "../scripts/create_simspace_csv.py"

def all_required_mriots(wildcards):
    df_path = checkpoints.create_simspace_csv.get(**wildcards).output[0]
    df = pd.read_csv(df_path)
    all_files = collect(
        "{mriot_data}{parsed}/{mriot_full}.pkl",
        mriot_data=config["data-mriot"]["prefix"],
        mriot_full = df[["mriot","mriot_year","mriot_aggreg"]].apply(lambda row: f'{row["mriot"]}/{"_".join(row.values.astype(str))}', axis=1).unique(),
        parsed=config["data-mriot"]["parsed_mriot_dir"],
    )
    return all_files

rule all_mriots:
    input:
        all_required_mriots

def get_all_sectors_config(wildcards):
    df_path = checkpoints.create_simspace_csv.get(**wildcards).output[0]
    df = pd.read_csv(df_path)
    mriot_aggs = df[["mriot","mriot_aggreg"]].apply(
            lambda row: "_".join(row.values.astype(str)), axis=1
        )
    mriot_sectors_aggs = mriot_aggs.str.extract(mriot_tools_snake.MRIOT_BASENAME_REGEX+"_"+mriot_tools_snake.MRIOT_AGGREG_SECTORS_REGEX)
    mriot_sectors_aggs = mriot_sectors_aggs.apply(
        lambda row: "_".join(row.values.astype(str)),
        axis=1).unique()
    all_files = collect(
        "{mriot_data}{params}/{mriot_sectors_aggs}.csv",
        mriot_data=config["data-mriot"]["prefix"],
        params=config["data-mriot"]["mriot_params_dir"],
        mriot_sectors_aggs = mriot_sectors_aggs
    )
    return all_files

rule create_mriot_sectors_config:
    input:
        get_all_sectors_config

rule create_flood_scenarios_csv:
    input:
        flood_scenario=str(Path(f"{workflow.basedir}/../config/{config['flood scenario']}").resolve()),
        mriots = all_required_mriots,
    output:
        "flood_scenarios.csv"
    log:
        f"logs/create_flood_scenarios.log",
    params:
        pkl_dir = "{mriot_data}{parsed}".format(mriot_data=config["data-mriot"]["prefix"],parsed=config["data-mriot"]["parsed_mriot_dir"])
    conda:
        "../envs/BoARIO-sensi.yml"
    script:
        "../scripts/create_flood_scenarios_csv.py"

rule cp_exio3_full_to_storage:
    input:
        exio3_sectors_config=str(Path(f"{workflow.basedir}/../config/{config['mriot_base_config']}").resolve())
    output:
        exio3_sectors_config=expand(
            "{mriot_data}{mriot_params_dir}/exiobase3_ixi_full_sectors.csv",
            mriot_params_dir=config["data-mriot"]["mriot_params_dir"],
            mriot_data=config["data-mriot"]["prefix"]
    ),
    shell:
        """
        cp {input} {output}
        """
