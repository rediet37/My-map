import folium
import json
from folium.plugins import HeatMap

# Initialize the map
mapObj = folium.Map(location=[9.102096738726456, 40.71533203125001], zoom_start=6, zoom_control=False)

# Ethiopia GeoJSON layer
bordersStyle = {
    'color': 'grey',
    'weight': '2',
    'fillColor': 'purple',
    'fillOpacity': 0.2
}

folium.GeoJson("et.json", name="Ethiopia", style_function=lambda x: bordersStyle).add_to(mapObj)

# Feature Groups for different hazard types
rainfallLayer = folium.FeatureGroup(name="Rainfall", show=False)
temperatureLayer = folium.FeatureGroup(name="Temperature", show=False)
climateChangeLayer = folium.FeatureGroup(name="Climate Change", show=False)
droughtLayer = folium.FeatureGroup(name="Drought", show=False)

# Sample Heatmap Data
#rainfall_data = [[7.1, 43.6, 60], [12.0, 40.8, 50], [7.8, 34.4, 70]]
temperature_data = [[7.2, 42.5, 35], [11.5, 39.9, 40], [8.0, 33.5, 30]]

##### TRIAL FOR THE GEOJSON FILE####
# Load the GeoJSON file
with open("rain.geojson", "r", encoding="utf-8") as f:
    geojson_data = json.load(f)

# Extract coordinates and rainfall values
rainfall_data = []
for feature in geojson_data["features"]:
    try:
        lon, lat = feature["geometry"]["coordinates"]  # Extract coordinates
        rainfall = feature["properties"].get("rainfall", 50)  # Default to 50 if missing
        rainfall_data.append([lat, lon, rainfall])
    except (KeyError, TypeError, ValueError):
        continue  # Skip invalid data

# Add HeatMap layers
HeatMap(data=rainfall_data, radius=15, blur=10).add_to(rainfallLayer)
#HeatMap(data=temperature_data, radius=15, blur=10).add_to(temperatureLayer)



# Add layers to map
mapObj.add_child(rainfallLayer)
mapObj.add_child(temperatureLayer)
mapObj.add_child(climateChangeLayer)
mapObj.add_child(droughtLayer)

# Custom Sidebar (references external CSS & JS)
custom_sidebar = """
<link rel="stylesheet" type="text/css" href="map.css">
<div id="sidebar">
    <h3>Hazard Watch</h3>
    <button onclick="toggleCategory('rainfall')">Rainfall</button>
    <button onclick="toggleCategory('temperature')">Temperature</button>
    <button onclick="toggleCategory('climateChange')">Climate Change</button>
    <button onclick="toggleCategory('drought')">Drought</button>

    <div id="sub-options">
        <h4 id="category-title"></h4>
        <input type="checkbox" id="toggle-layer" onclick="toggleLayer()"> Show Data
    </div>
</div>
<script src="map.js"></script>
"""

folium.LayerControl().add_to(mapObj)

# Add sidebar to map
mapObj.get_root().html.add_child(folium.Element(custom_sidebar))

# Save map to file
mapObj.save('output.html')
