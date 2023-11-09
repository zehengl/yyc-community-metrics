# %%
from pathlib import Path

import pandas as pd
import seaborn as sns

from opendata import (
    get_bikeways,
    get_bus_stops,
    get_community_district_boundaries,
    get_lrt_stations,
    get_public_art,
    get_recreation_facilities,
    get_school_locations,
    get_tracks_lrt,
    get_tracks_railway,
    get_tree_canopy_2022,
)

# %%
output = Path("output")
output.mkdir(exist_ok=True)

# %%
communities = get_community_district_boundaries()

# %%
schools = get_school_locations()

# %%
bikeways = get_bikeways()

# %%
bus_stops = get_bus_stops()

# %%
lrt_stations = get_lrt_stations()

# %%
public_art = get_public_art()

# %%
recreation_facilities = get_recreation_facilities()

# %%
tree_canopy = get_tree_canopy_2022()

# %%
tracks_lrt = get_tracks_lrt(force=True)

# %%
tracks_railway = get_tracks_railway(force=True)

# %%
for src in [
    schools,
    bikeways,
    bus_stops,
    lrt_stations,
    public_art,
    recreation_facilities,
    tree_canopy,
    tracks_lrt,
    tracks_railway,
]:
    communities = pd.merge(communities, src, on="name")

cols = [
    col
    for col in communities
    if col not in ["class_code", "comm_code", "srg", "multipolygon"]
]
communities = communities[cols]


# %%
def format_name(name):
    if type(name) is not str or name[0].isdigit():
        return name
    name = "/".join(
        " ".join(t.capitalize() for t in p.split()) for p in name.split("/")
    )

    return name


communities["name"] = communities["name"].apply(format_name)
communities["sector"] = communities["sector"].apply(format_name)
communities["comm_structure"] = communities["comm_structure"].apply(format_name)
communities = communities.sort_values("name")
communities


# %%
communities.to_json(
    output / "data.json",
    orient="records",
    indent=2,
    double_precision=3,
)
communities.to_csv(
    output / "data.csv",
    index=False,
)


# %%
ax = sns.barplot(
    data=communities.groupby("sector").sum(numeric_only=True).reset_index(),
    y="sector",
    x="area",
)

# %%
ax = sns.barplot(
    data=communities.groupby("class").sum(numeric_only=True).reset_index(),
    y="class",
    x="area",
)

# %%
ax = sns.barplot(
    data=communities.groupby("comm_structure").sum(numeric_only=True).reset_index(),
    y="comm_structure",
    x="area",
)


# %%
ax = sns.histplot(data=communities, x="schools")


# %%
ax = sns.boxplot(data=communities, y="bikeways", x="sector")
ax.set_xticklabels(ax.get_xticklabels(), rotation=45)

# %%
