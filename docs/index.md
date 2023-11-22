<figure markdown>
![Logo](https://cdn1.iconfinder.com/data/icons/flat-and-simple-part-1/128/location-512.png){ width="100" }
</figure>

# yyc-community-metrics

An aggregation of community-related data for City of Calgary

## Data Aggregation

Each community is a polygon in the map. When we aggregate data for a community, only the intersected portion of a feature is considered.

See the following examples where we use a <span style="color:blue">blue polygon</span> to represent a community, a <span style="color:green">green polygon</span> / a <span style="color:orange">orange line</span> / a **point** to represent a feature. Only the <span style="color:red">red portion</span> of those features will be taken into consideration during data aggregation.

![Example 1](example1.png)

![Example 2](example2.png)

![Example 3](example3.png)

## Projection

Use UTM projection for area / length calculation.

![WGS84](wgs84.png)

![UTM](utm.png)
