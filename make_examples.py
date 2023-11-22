# %% https://stackoverflow.com/a/25276331
import math
import random
from typing import List, Tuple

random.seed(2023)


def generate_polygon(
    center: Tuple[float, float],
    avg_radius: float,
    irregularity: float,
    spikiness: float,
    num_vertices: int,
) -> List[Tuple[float, float]]:
    """
    Start with the center of the polygon at center, then creates the
    polygon by sampling points on a circle around the center.
    Random noise is added by varying the angular spacing between
    sequential points, and by varying the radial distance of each
    point from the centre.

    Args:
        center (Tuple[float, float]):
            a pair representing the center of the circumference used
            to generate the polygon.
        avg_radius (float):
            the average radius (distance of each generated vertex to
            the center of the circumference) used to generate points
            with a normal distribution.
        irregularity (float):
            variance of the spacing of the angles between consecutive
            vertices.
        spikiness (float):
            variance of the distance of each vertex to the center of
            the circumference.
        num_vertices (int):
            the number of vertices of the polygon.
    Returns:
        List[Tuple[float, float]]: list of vertices, in CCW order.
    """
    # Parameter check
    if irregularity < 0 or irregularity > 1:
        raise ValueError("Irregularity must be between 0 and 1.")
    if spikiness < 0 or spikiness > 1:
        raise ValueError("Spikiness must be between 0 and 1.")

    irregularity *= 2 * math.pi / num_vertices
    spikiness *= avg_radius
    angle_steps = random_angle_steps(num_vertices, irregularity)

    # now generate the points
    points = []
    angle = random.uniform(0, 2 * math.pi)
    for i in range(num_vertices):
        radius = clip(random.gauss(avg_radius, spikiness), 0, 2 * avg_radius)
        point = (
            center[0] + radius * math.cos(angle),
            center[1] + radius * math.sin(angle),
        )
        points.append(point)
        angle += angle_steps[i]

    return points


def random_angle_steps(steps: int, irregularity: float) -> List[float]:
    """Generates the division of a circumference in random angles.

    Args:
        steps (int):
            the number of angles to generate.
        irregularity (float):
            variance of the spacing of the angles between consecutive vertices.
    Returns:
        List[float]: the list of the random angles.
    """
    # generate n angle steps
    angles = []
    lower = (2 * math.pi / steps) - irregularity
    upper = (2 * math.pi / steps) + irregularity
    cumsum = 0
    for i in range(steps):
        angle = random.uniform(lower, upper)
        angles.append(angle)
        cumsum += angle

    # normalize the steps so that point 0 and point n+1 are the same
    cumsum /= 2 * math.pi
    for i in range(steps):
        angles[i] /= cumsum
    return angles


def clip(value, lower, upper):
    """
    Given an interval, values outside the interval are clipped to the interval
    edges.
    """
    return min(upper, max(value, lower))


# %%
import io

import folium
from PIL import Image
from shapely.geometry import LineString, Point, Polygon
from tqdm import tqdm

center = (51.0447, -114.0719)
blue = "#0000FF"
green = "#3BB143"
orange = "#FF7F50"
red = "#800000"

for i in tqdm(range(3), desc="Making examples"):
    m = folium.Map(location=center, zoom_start=12)

    poly1 = Polygon(
        generate_polygon(
            center=center[::-1],
            avg_radius=0.01,
            irregularity=0.35,
            spikiness=0.2,
            num_vertices=8,
        )
    )

    poly2 = Polygon(
        generate_polygon(
            center=center[::-1],
            avg_radius=0.01,
            irregularity=0.35,
            spikiness=0.2,
            num_vertices=8,
        )
    )

    line = LineString(
        generate_polygon(
            center=center[::-1],
            avg_radius=0.02,
            irregularity=0.35,
            spikiness=0.2,
            num_vertices=2,
        )
    )

    point = Point(
        generate_polygon(
            center=center[::-1],
            avg_radius=0.01,
            irregularity=0.35,
            spikiness=0.2,
            num_vertices=1,
        )
    )

    folium.GeoJson(poly1, lambda _: {"fillColor": blue, "color": blue}).add_to(m)
    m.fit_bounds([poly1.bounds[:2][::-1], poly1.bounds[2:][::-1]])

    folium.GeoJson(
        poly2,
        style_function=lambda _: {"fillColor": green, "color": green},
    ).add_to(m)

    folium.GeoJson(
        line,
        style_function=lambda _: {"fillColor": orange, "color": orange},
    ).add_to(m)

    folium.GeoJson(
        point,
        marker=folium.Marker(
            (point.xy[1][0], point.xy[0][0]),
            icon=folium.Icon(color="red" if poly1.contains(point) else "blue"),
        ),
    ).add_to(m)

    overlap_poly = poly1.intersection(poly2)
    folium.GeoJson(
        overlap_poly,
        style_function=lambda _: {"fillColor": red, "color": red},
    ).add_to(m)

    overlap_line = poly1.intersection(line)
    folium.GeoJson(
        overlap_line,
        style_function=lambda _: {"fillColor": red, "color": red},
    ).add_to(m)

    img_data = m._to_png(10)
    img = Image.open(io.BytesIO(img_data))
    img.save(f"docs/example{i+1}.png")


# %%
import io

import folium
import matplotlib.pyplot as plt
import pyproj
from PIL import Image
from shapely.geometry import Polygon
from shapely.ops import transform

from opendata import project

m = folium.Map(location=center, zoom_start=12)
poly1 = Polygon(
    generate_polygon(
        center=center[::-1],
        avg_radius=0.01,
        irregularity=0.35,
        spikiness=0.2,
        num_vertices=8,
    )
)
folium.GeoJson(poly1, lambda _: {"fillColor": blue, "color": blue}).add_to(m)
m.fit_bounds([poly1.bounds[:2][::-1], poly1.bounds[2:][::-1]])
img_data = m._to_png(10)
img = Image.open(io.BytesIO(img_data))
img.save("docs/wgs84.png")


# %%
g = transform(project, poly1)
fig = plt.figure()
plt.plot(*g.exterior.xy)
fig.savefig("docs/utm.png")

# %%
