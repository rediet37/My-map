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

# Feature Groups for different hazard types and their subcategories
# Rainfall subcategories
rainfall_weekly_exceptional = folium.FeatureGroup(name="Weekly Exceptional Rainfall", show=False)
rainfall_weekly_total = folium.FeatureGroup(name="Weekly Total Rainfall Forecast", show=False)

# Temperature subcategories
temperature_current = folium.FeatureGroup(name="Current Temperature", show=False)

# Climate Change subcategories
climate_change_trends = folium.FeatureGroup(name="Climate Change Trends", show=False)

# Drought subcategories
drought_current = folium.FeatureGroup(name="Current Drought Conditions", show=False)


# Sample Heatmap Data
total_weekly_rainfall_data = [[7.1, 43.6, 60], [12.0, 40.8, 50], [7.8, 34.4, 70]]
current_temperature_data = [[7.2, 42.5, 35], [11.5, 39.9, 40], [8.0, 33.5, 30]]
current_drought_data = [[7.1, 43.6, 60], [12.0, 40.8, 50], [7.8, 34.4, 70]]

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
HeatMap(data=rainfall_data, radius=15, blur=10).add_to(rainfall_weekly_exceptional)
HeatMap(data=total_weekly_rainfall_data, radius=15, blur=10).add_to(rainfall_weekly_total)
HeatMap(data=current_temperature_data, radius=15, blur=10).add_to(temperature_current)
HeatMap(data=current_drought_data, radius=15, blur=10).add_to(drought_current)

# Add layers to map
mapObj.add_child(rainfall_weekly_exceptional)
mapObj.add_child(rainfall_weekly_total)
mapObj.add_child(temperature_current)
mapObj.add_child(climate_change_trends)
mapObj.add_child(drought_current)

folium.LayerControl().add_to(mapObj)

# Custom Sidebar (references external CSS & JS)
custom_sidebar = """
<link rel="stylesheet" type="text/css" href="map.css">
<div id="sidebar">
    <h3>Hazard Watch</h3>
    <div class="category">
        <button class="category-btn" onclick="toggleCategory('rainfall')">Rainfall</button>
        <div id="rainfall-subcategories" class="subcategories">
            <div class="subcategory">
                <input type="checkbox" id="rainfall-weekly-exceptional" data-layer="Weekly Exceptional Rainfall" onclick="toggleSubcategoryLayer(this)">
                <label for="rainfall-weekly-exceptional">Weekly Exceptional Rainfall</label>
                <span class="info-icon" title="Latest: 27th Feb 2025 to 6th Mar 2025">ⓘ</span>
            </div>
            <div class="subcategory">
                <input type="checkbox" id="rainfall-weekly-total" data-layer="Weekly Total Rainfall Forecast" onclick="toggleSubcategoryLayer(this)">
                <label for="rainfall-weekly-total">Weekly Total Rainfall Forecast</label>
                <span class="info-icon" title="Latest: 27th Feb 2025 to 6th Mar 2025">ⓘ</span>
            </div>
        </div>
    </div>
    
    <div class="category">
        <button class="category-btn" onclick="toggleCategory('temperature')">Temperature</button>
        <div id="temperature-subcategories" class="subcategories">
            <div class="subcategory">
                <input type="checkbox" id="temperature-current" data-layer="Current Temperature" onclick="toggleSubcategoryLayer(this)">
                <label for="temperature-current">Current Temperature</label>
                <span class="info-icon" title="Latest available data">ⓘ</span>
            </div>
            <div class="subcategory">
                <input type="checkbox" id="temperature-forecast" data-layer="Temperature Forecast" onclick="toggleSubcategoryLayer(this)">
                <label for="temperature-forecast">Temperature Forecast</label>
                <span class="info-icon" title="7-day forecast">ⓘ</span>
            </div>
        </div>
    </div>
    
    <div class="category">
        <button class="category-btn" onclick="toggleCategory('climateChange')">Climate Change</button>
        <div id="climateChange-subcategories" class="subcategories">
            <div class="subcategory">
                <input type="checkbox" id="climate-change-trends" data-layer="Climate Change Trends" onclick="toggleSubcategoryLayer(this)">
                <label for="climate-change-trends">Climate Change Trends</label>
                <span class="info-icon" title="Historical trends">ⓘ</span>
            </div>
            <div class="subcategory">
                <input type="checkbox" id="climate-change-impact" data-layer="Climate Change Impact" onclick="toggleSubcategoryLayer(this)">
                <label for="climate-change-impact">Climate Change Impact</label>
                <span class="info-icon" title="Projected impact">ⓘ</span>
            </div>
        </div>
    </div>
    
    <div class="category">
        <button class="category-btn" onclick="toggleCategory('drought')">Drought</button>
        <div id="drought-subcategories" class="subcategories">
            <div class="subcategory">
                <input type="checkbox" id="drought-current" data-layer="Current Drought Conditions" onclick="toggleSubcategoryLayer(this)">
                <label for="drought-current">Current Drought Conditions</label>
                <span class="info-icon" title="Current conditions">ⓘ</span>
            </div>
            <div class="subcategory">
                <input type="checkbox" id="drought-forecast" data-layer="Drought Forecast" onclick="toggleSubcategoryLayer(this)">
                <label for="drought-forecast">Drought Forecast</label>
                <span class="info-icon" title="3-month forecast">ⓘ</span>
            </div>
        </div>
    </div>
</div>
<script src="map.js"></script>
"""

# Add sidebar to map
mapObj.get_root().html.add_child(folium.Element(custom_sidebar))

# Save map to file
mapObj.save('output.html')