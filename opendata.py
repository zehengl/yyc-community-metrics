from pathlib import Path

import pandas as pd
import pyproj
import requests
from shapely.geometry import shape
from shapely.ops import transform
from tqdm import tqdm

data = Path("data")
data.mkdir(exist_ok=True)

wgs84 = pyproj.CRS("EPSG:4326")
utm = pyproj.CRS("EPSG:3776")
project = pyproj.Transformer.from_crs(wgs84, utm, always_xy=True).transform


def download(code, offset=25000, force=False, func=None, **kwargs):
    f = data / f"{code}.pkl"
    if f.exists() and not force:
        print(f"Reading {code} from file")
        df = pd.read_pickle(f)

    else:
        print(f"Downloading {code} from opendata")
        total_url = f"https://data.calgary.ca/resource/{code}.json?$select=count(*)"
        total = int(requests.get(total_url).json()[0]["count"])

        df = pd.DataFrame()
        for i in range(0, total, offset):
            batch_url = f"https://data.calgary.ca/resource/{code}.json?$offset={i}&$limit={offset}"
            df = pd.concat(
                [
                    df,
                    pd.DataFrame(requests.get(batch_url).json()),
                ]
            )

        if func:
            df = func(df, **kwargs)

        df.to_pickle(f)

    return df


def process_community_district_boundaries(communities):
    communities["multipolygon"] = communities["multipolygon"].apply(shape)
    communities["area"] = communities["multipolygon"].apply(
        lambda g: transform(project, g).area
    )
    communities["area"] = communities["area"].round(3)
    return communities


def get_community_district_boundaries(offset=25000, force=False):
    df = download(
        "surr-xmvs",
        offset,
        force,
        process_community_district_boundaries,
    )
    return df


def process_school_locations(schools, communities):
    schools["point"] = schools["point"].apply(shape)
    counts = []
    desc = "Counting Number of Schools"
    for g in tqdm(communities["multipolygon"], desc=desc):
        count = schools["point"].apply(g.contains).sum()
        counts.append(count)
    communities["schools"] = counts
    return communities[["name", "schools"]]


def get_school_locations(offset=25000, force=False):
    df = download(
        "fd9t-tdn2",
        offset,
        force,
        process_school_locations,
        communities=get_community_district_boundaries(),
    )
    return df


def process_bikeways(bikeways, communities):
    bikeways = bikeways[~bikeways["multilinestring"].isna()]
    bikeways = bikeways[bikeways["status"] != "INACTIVE"]
    bikeways["multilinestring"] = bikeways["multilinestring"].apply(shape)
    lengths = []
    desc = "Counting Length of BikeWays"
    for g in tqdm(communities["multipolygon"], desc=desc):
        length = (
            bikeways["multilinestring"]
            .apply(lambda p: transform(project, g.intersection(p)).length)
            .sum()
        )
        lengths.append(length)
    communities["bikeways"] = lengths
    communities["bikeways"] = communities["bikeways"].round(3)
    return communities[["name", "bikeways"]]


def get_bikeways(offset=25000, force=False):
    df = download(
        "jjqk-9b73",
        offset,
        force,
        process_bikeways,
        communities=get_community_district_boundaries(),
    )
    return df


def process_bus_stops(bus_stops, communities):
    bus_stops = bus_stops[bus_stops["status"] != "ACTIVE"]
    bus_stops["point"] = bus_stops["point"].apply(shape)
    counts = []
    desc = "Counting Number of Bus Stops"
    for g in tqdm(communities["multipolygon"], desc=desc):
        count = bus_stops["point"].apply(g.contains).sum()
        counts.append(count)
    communities["bus_stops"] = counts
    return communities[["name", "bus_stops"]]


def get_bus_stops(offset=25000, force=False):
    df = download(
        "muzh-c9qc",
        offset,
        force,
        process_bus_stops,
        communities=get_community_district_boundaries(),
    )
    return df


def process_tree_canopy_2022(tree_canopy, communities):
    tree_canopy = tree_canopy[~tree_canopy["multipolygon"].isna()]
    tree_canopy["multipolygon"] = tree_canopy["multipolygon"].apply(shape)
    areas = []
    desc = "Counting 2022 Tree Canopy Areas"
    for g in tqdm(communities["multipolygon"], desc=desc):
        area = (
            tree_canopy["multipolygon"]
            .apply(lambda r: transform(project, g.intersection(r)).area)
            .sum()
        )
        areas.append(area)
    communities["tree_canopy_2022"] = areas
    communities["tree_canopy_2022"] = communities["tree_canopy_2022"].round(3)
    return communities[["name", "tree_canopy_2022"]]


def get_tree_canopy_2022(offset=25000, force=False):
    df = download(
        "mn2n-4z98",
        offset,
        force,
        process_tree_canopy_2022,
        communities=get_community_district_boundaries(),
    )
    return df


def process_lrt_stations(lrt_stations, communities):
    lrt_stations["the_geom"] = lrt_stations["the_geom"].apply(shape)
    counts = []
    desc = "Counting Number of LRT Stations"
    for g in tqdm(communities["multipolygon"], desc=desc):
        count = lrt_stations["the_geom"].apply(g.contains).sum()
        counts.append(count)
    communities["lrt_stations"] = counts
    return communities[["name", "lrt_stations"]]


def get_lrt_stations(offset=25000, force=False):
    df = download(
        "2axz-xm4q",
        offset,
        force,
        process_lrt_stations,
        communities=get_community_district_boundaries(),
    )
    return df


def process_public_art(public_art, communities):
    public_art["point"] = public_art["point"].apply(shape)
    counts = []
    desc = "Counting Number of Public Art"
    for g in tqdm(communities["multipolygon"], desc=desc):
        count = public_art["point"].apply(g.contains).sum()
        counts.append(count)
    communities["public_art"] = counts
    return communities[["name", "public_art"]]


def get_public_art(offset=25000, force=False):
    df = download(
        "2kp2-hsy7",
        offset,
        force,
        process_public_art,
        communities=get_community_district_boundaries(),
    )
    return df


def process_recreation_facilities(recreation_facilities, communities):
    recreation_facilities["point"] = recreation_facilities["point"].apply(shape)
    counts = []
    desc = "Counting Number of Recreation Facilities"
    for g in tqdm(communities["multipolygon"], desc=desc):
        count = recreation_facilities["point"].apply(g.contains).sum()
        counts.append(count)
    communities["recreation_facilities"] = counts
    return communities[["name", "recreation_facilities"]]


def get_recreation_facilities(offset=25000, force=False):
    df = download(
        "hxfu-6d96",
        offset,
        force,
        process_recreation_facilities,
        communities=get_community_district_boundaries(),
    )
    return df


def process_tracks_lrt(tracks_lrt, communities):
    tracks_lrt["the_geom"] = tracks_lrt["the_geom"].apply(shape)
    lengths = []
    desc = "Counting Length of LRT Tracks"
    for g in tqdm(communities["multipolygon"], desc=desc):
        length = (
            tracks_lrt["the_geom"]
            .apply(lambda p: transform(project, g.intersection(p)).length)
            .sum()
        )
        lengths.append(length)
    communities["tracks_lrt"] = lengths
    communities["tracks_lrt"] = communities["tracks_lrt"].round(3)
    return communities[["name", "tracks_lrt"]]


def get_tracks_lrt(offset=25000, force=False):
    df = download(
        "ic67-rkd7",
        offset,
        force,
        process_tracks_lrt,
        communities=get_community_district_boundaries(),
    )
    return df


def process_tracks_railway(tracks_railway, communities):
    tracks_railway["the_geom"] = tracks_railway["the_geom"].apply(shape)
    lengths = []
    desc = "Counting Length of Railway Tracks"
    for g in tqdm(communities["multipolygon"], desc=desc):
        length = (
            tracks_railway["the_geom"]
            .apply(lambda p: transform(project, g.intersection(p)).length)
            .sum()
        )
        lengths.append(length)
    communities["tracks_railway"] = lengths
    communities["tracks_railway"] = communities["tracks_railway"].round(3)
    return communities[["name", "tracks_railway"]]


def get_tracks_railway(offset=25000, force=False):
    df = download(
        "cq6k-mmku",
        offset,
        force,
        process_tracks_railway,
        communities=get_community_district_boundaries(),
    )
    return df


def process_off_leash_areas(off_leash_areas, communities):
    off_leash_areas["multipolygon"] = off_leash_areas["multipolygon"].apply(shape)
    areas = []
    desc = "Counting 2022 Tree Canopy Areas"
    for g in tqdm(communities["multipolygon"], desc=desc):
        area = (
            off_leash_areas["multipolygon"]
            .apply(lambda r: transform(project, g.intersection(r)).area)
            .sum()
        )
        areas.append(area)
    communities["off_leash_areas"] = areas
    communities["off_leash_areas"] = communities["off_leash_areas"].round(3)
    return communities[["name", "off_leash_areas"]]


def get_off_leash_areas(offset=25000, force=False):
    df = download(
        "enr4-crti",
        offset,
        force,
        process_off_leash_areas,
        communities=get_community_district_boundaries(),
    )
    return df


def process_pathways(pathways, communities):
    pathways["the_geom"] = pathways["the_geom"].apply(shape)
    lengths = []
    desc = "Counting Length of Pathways"
    for g in tqdm(communities["multipolygon"], desc=desc):
        length = (
            pathways["the_geom"]
            .apply(lambda p: transform(project, g.intersection(p)).length)
            .sum()
        )
        lengths.append(length)
    communities["pathways"] = lengths
    communities["pathways"] = communities["pathways"].round(3)
    return communities[["name", "pathways"]]


def get_pathways(offset=25000, force=False):
    df = download(
        "qndb-27qm",
        offset,
        force,
        process_pathways,
        communities=get_community_district_boundaries(),
    )
    return df


def process_community_services(community_services, communities):
    community_services["point"] = community_services["point"].apply(shape)
    libraries, hospitals_and_clinics, attractions = [], [], []
    desc = "Counting Number of Community Services"
    for g in tqdm(communities["multipolygon"], desc=desc):
        libraries.append(
            community_services[community_services["type"] == "Library"]["point"]
            .apply(g.contains)
            .sum()
        )
        hospitals_and_clinics.append(
            community_services[
                community_services["type"].isin(["PHS Clinic", "Hospital"])
            ]["point"]
            .apply(g.contains)
            .sum()
        )
        attractions.append(
            community_services[community_services["type"] == "Attraction"]["point"]
            .apply(g.contains)
            .sum()
        )
    communities["libraries"] = libraries
    communities["hospitals_and_clinics"] = hospitals_and_clinics
    communities["attractions"] = attractions

    return communities[["name", "libraries", "hospitals_and_clinics", "attractions"]]


def get_community_services(offset=25000, force=False):
    df = download(
        "x34e-bcjz",
        offset,
        force,
        process_community_services,
        communities=get_community_district_boundaries(),
    )
    return df


def process_community_crime_statistics(community_crime_statistics, communities):
    community_crime_statistics["crime_count"] = pd.to_numeric(
        community_crime_statistics["crime_count"]
    )
    community_crime_statistics = (
        community_crime_statistics.groupby(["community_name", "year"])
        .sum(numeric_only=True)
        .reset_index()
        .groupby("community_name")
        .mean(numeric_only=True)
        .reset_index()
    )
    df = communities.merge(
        community_crime_statistics,
        left_on="name",
        right_on="community_name",
        how="left",
    )[["name", "crime_count"]]
    df["crime_count"] = df["crime_count"].round(0).astype("Int64")
    return df


def get_community_crime_statistics(offset=25000, force=False):
    df = download(
        "78gh-n26t",
        offset,
        force,
        process_community_crime_statistics,
        communities=get_community_district_boundaries(),
    )
    return df
