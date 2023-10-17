# %%
from pathlib import Path

import pyproj
import seaborn as sns
from shapely.geometry import shape
from shapely.ops import transform
from tqdm import tqdm

from opendata import (
    get_bikeways,
    get_bus_stops,
    get_community_district_boundaries,
    get_lrt_stations,
    get_public_art,
    get_recreation_facilities,
    get_school_locations,
    get_tree_canopy_2022,
)

# %%
wgs84 = pyproj.CRS("EPSG:4326")
utm = pyproj.CRS("EPSG:3776")
project = pyproj.Transformer.from_crs(wgs84, utm, always_xy=True).transform

output = Path("output")
output.mkdir(exist_ok=True)

# %%
communities = get_community_district_boundaries()
communities["multipolygon"] = communities["multipolygon"].apply(shape)
communities["area"] = communities["multipolygon"].apply(
    lambda g: transform(project, g).area
)
communities["area"] = communities["area"].round(3)


# %%
schools = get_school_locations()
schools["point"] = schools["point"].apply(shape)
counts = []
for g in tqdm(communities["multipolygon"], desc="Counting Number of Schools"):
    count = schools["point"].apply(g.contains).sum()
    counts.append(count)
communities["schools"] = counts


# %%
bikeways = get_bikeways()
bikeways = bikeways[~bikeways["multilinestring"].isna()]
bikeways = bikeways[bikeways["status"] != "INACTIVE"]
bikeways["multilinestring"] = bikeways["multilinestring"].apply(shape)
lengths = []
for g in tqdm(communities["multipolygon"], desc="Counting Length of BikeWays"):
    length = (
        bikeways["multilinestring"]
        .apply(lambda p: transform(project, g.intersection(p)).length)
        .sum()
    )
    lengths.append(length)
communities["bikeways"] = lengths
communities["bikeways"] = communities["bikeways"].round(3)

# %%
bus_stops = get_bus_stops()
bus_stops = bus_stops[bus_stops["status"] != "ACTIVE"]
bus_stops["point"] = bus_stops["point"].apply(shape)
counts = []
for g in tqdm(communities["multipolygon"], desc="Counting Number of Bus Stops"):
    count = bus_stops["point"].apply(g.contains).sum()
    counts.append(count)
communities["bus_stops"] = counts


# %%
lrt_stations = get_lrt_stations()
lrt_stations["the_geom"] = lrt_stations["the_geom"].apply(shape)
counts = []
for g in tqdm(communities["multipolygon"], desc="Counting Number of LRT Stations"):
    count = lrt_stations["the_geom"].apply(g.contains).sum()
    counts.append(count)
communities["lrt_stations"] = counts


# %%
public_art = get_public_art()
public_art["point"] = public_art["point"].apply(shape)
counts = []
for g in tqdm(communities["multipolygon"], desc="Counting Number of Public Art"):
    count = public_art["point"].apply(g.contains).sum()
    counts.append(count)
communities["public_art"] = counts


# %%
recreation_facilities = get_recreation_facilities()
recreation_facilities["point"] = recreation_facilities["point"].apply(shape)
counts = []
for g in tqdm(
    communities["multipolygon"], desc="Counting Number of Recreation Facilities"
):
    count = recreation_facilities["point"].apply(g.contains).sum()
    counts.append(count)
communities["recreation_facilities"] = counts


# %%
tree_canopy = get_tree_canopy_2022()
tree_canopy = tree_canopy[~tree_canopy["multipolygon"].isna()]
tree_canopy["multipolygon"] = tree_canopy["multipolygon"].apply(shape)
areas = []
for g in tqdm(communities["multipolygon"], desc="Counting 2022 Tree Canopy Areas"):
    area = (
        tree_canopy["multipolygon"]
        .apply(lambda r: transform(project, g.intersection(r)).area)
        .sum()
    )
    areas.append(area)
communities["tree_canopy_2022"] = areas
communities["tree_canopy_2022"] = communities["tree_canopy_2022"].round(3)


# %%
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
