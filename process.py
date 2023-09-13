# %%
from pathlib import Path

import pyproj
import seaborn as sns
from shapely.geometry import shape
from shapely.ops import transform
from tqdm import tqdm

from opendata import (
    get_bikeways,
    get_community_district_boundaries,
    get_school_locations,
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


# %%
schools = get_school_locations()
schools["the_geom"] = schools["the_geom"].apply(shape)
counts = []
for g in tqdm(communities["multipolygon"], desc="Counting Number of Schools"):
    count = schools["the_geom"].apply(g.contains).sum()
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


# %%
cols = [
    col
    for col in communities
    if col not in ["class_code", "comm_code", "srg", "multipolygon"]
]
communities = communities[cols]


# %%
communities.to_json(output / "data.json", orient="records", indent=2)
communities.to_csv(output / "data.csv", index=False)


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
