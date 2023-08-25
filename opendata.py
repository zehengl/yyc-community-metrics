import requests
import pandas as pd


def download(code, offset=25000):
    total_url = f"https://data.calgary.ca/resource/{code}.json?$select=count(*)"
    total = int(requests.get(total_url).json()[0]["count"])

    df = pd.DataFrame()
    for i in range(0, total, offset):
        batch_url = (
            f"https://data.calgary.ca/resource/{code}.json?$offset={i}&$limit={offset}"
        )
        df = pd.concat(
            [
                df,
                pd.DataFrame(requests.get(batch_url).json()),
            ]
        )

    return df


def get_community_district_boundaries():
    df = download("surr-xmvs")
    return df


def get_school_locations():
    df = download("fd9t-tdn2")
    return df
