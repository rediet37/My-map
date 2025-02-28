import pandas as pd
import json

df = pd.read_csv("rainfall.csv")

geojson = {
    "type": "FeatureCollection",
    "features": []
}

for _, row in df.iterrows():
    feature = {
        "type": "Feature",
        "geometry": {
            "type": "point",
            "coordinates": [row["longitude"], row["latitude"]]
        },
        "properties": row.to_dict()  # Include all other data as properties
    }
    geojson["features"].append(feature)

# Save as GeoJSON file
with open("rain.geojson", "w") as f:
    json.dump(geojson, f)

print("GeoJSON file created successfully!")