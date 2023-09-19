from pathlib import Path

import pandas as pd
import requests

data = Path("data")
data.mkdir(exist_ok=True)


def download(code, offset=25000, force=False):
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

        df.to_pickle(f)

    return df


def get_community_district_boundaries(offset=25000, force=False):
    df = download("surr-xmvs", offset, force)
    return df


def get_school_locations(offset=25000, force=False):
    df = download("fd9t-tdn2", offset, force)
    return df


def get_bikeways(offset=25000, force=False):
    df = download("jjqk-9b73", offset, force)
    return df


def get_bus_stops(offset=25000, force=False):
    df = download("muzh-c9qc", offset, force)
    return df


def get_tree_canopy_2022(offset=25000, force=False):
    df = download("mn2n-4z98", offset, force)
    return df
