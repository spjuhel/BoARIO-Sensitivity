import pandas as pd

mrio_dict = {
    "eora26":"Eora sectors",
    "euregio":"Euregio sectors",
    "oecd_v2021":"ICIO2021_reworked sectors name"
}

colname = mrio_dict[snakemake.params.mrio_type]

sectors_df = pd.read_csv(snakemake.input.exio3_sectors_config, index_col=0, decimal=",")
aggregation_master_df = pd.read_excel(snakemake.input.aggregation_master, sheet_name=0, index_col="Exiobase3 full sectors")
res = aggregation_master_df.join(sectors_df)[[colname, 'affected', 'rebuilding_factor', 'inventory_size', 'kapital_to_va_ratio', 'inventory_tau']].groupby(colname).agg(
    {
        'affected':any,
        'rebuilding_factor':sum,
        'inventory_size':"mean",
        'kapital_to_va_ratio':"mean",
        'inventory_tau':"mean",
    }
).fillna("Infinity")
res.to_csv(snakemake.output[0])
