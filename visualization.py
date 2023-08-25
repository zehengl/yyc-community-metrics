# %%
import pyproj
import seaborn as sns
from shapely.geometry import shape
from shapely.ops import transform
from tqdm import tqdm
from opendata import get_community_district_boundaries, get_school_locations


# %%
wgs84 = pyproj.CRS("EPSG:4326")
utm = pyproj.CRS("EPSG:3776")
project = pyproj.Transformer.from_crs(wgs84, utm, always_xy=True).transform


# %%
communities = get_community_district_boundaries()
communities["multipolygon"] = communities["multipolygon"].apply(lambda g: shape(g))
communities["area"] = communities["multipolygon"].apply(
    lambda g: transform(project, g).area
)


# %%
schools = get_school_locations()
schools["the_geom"] = schools["the_geom"].apply(lambda g: shape(g))
counts = []
for g in tqdm(communities["multipolygon"], desc="Counting Number of Schools"):
    count = schools["the_geom"].apply(lambda p: g.contains(p)).sum()
    counts.append(count)
communities["schools"] = counts


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
