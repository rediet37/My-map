import folium
import json
from folium.plugins import HeatMap
import branca.colormap as cm


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

# Create a feature group for shapes (circles, markers, etc.)
markerLayer = folium.FeatureGroup(name="Marker").add_to(mapObj)

# Add markers to the shapes layer
MarkerData = [
    [7.073637435358673, 43.66928100585938, 30000, "Somali"],
    [12.06618091465063, 40.81146240234376, 30000, "Afar"],
    [7.83073144786945, 34.46754455566407, 30000, "Gambela"]
]

for d in MarkerData:
    folium.Marker(
        location=[d[0], d[1]],
        icon=folium.Icon(icon='map-marker', prefix='fa', color='darkblue'),
        tooltip=d[3],
        popup=folium.Popup(f"""<h3>{d[3]}</h3> <br/>
                This is the <b>{d[3]}</b> region<br/><br/>
                <button id="analyze-button">Analyze</button> """, max_width=500)
    ).add_to(markerLayer)


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

# Create colormaps for each hazard type
#rainfall_colormap = cm.LinearColormap(
 #   ['blue', 'green', 'yellow', 'orange', 'red'],
  #  vmin=0, vmax=100,
   # caption='Rainfall (mm)'
#)

#temperature_colormap = cm.LinearColormap(
 #   ['blue', 'green', 'yellow', 'orange', 'red'],
  #  vmin=0, vmax=50,
   # caption='Temperature (°C)'
#)

#drought_colormap = cm.LinearColormap(
 #   ['green', 'yellow', 'orange', 'red', 'darkred'],
 #   vmin=0, vmax=100,
 #   caption='Drought Severity Index'
#)

# Add HeatMap layers
HeatMap(data=rainfall_data, radius=20, blur=10).add_to(rainfall_weekly_exceptional)
HeatMap(data=total_weekly_rainfall_data, radius=20, blur=10).add_to(rainfall_weekly_total)
HeatMap(data=current_temperature_data, radius=20, blur=10).add_to(temperature_current)
HeatMap(data=current_drought_data, radius=20, blur=10).add_to(drought_current)

# Add layers to map
mapObj.add_child(rainfall_weekly_exceptional)
mapObj.add_child(rainfall_weekly_total)
mapObj.add_child(temperature_current)
mapObj.add_child(climate_change_trends)
mapObj.add_child(drought_current)

# Add colormaps to the map
#rainfall_colormap.add_to(mapObj)
#temperature_colormap.add_to(mapObj)
#drought_colormap.add_to(mapObj)

# Create a Layer Control that will be hidden but still functional
folium.LayerControl().add_to(mapObj)

# Custom Sidebar and Tab structure
custom_sidebar = """
<link rel="stylesheet" type="text/css" href="map.css">

<!-- Main sidebar with hazard categories -->
<div id="sidebar">
    <h3>Hazard Watch</h3>
        
    <!-- Categories Section -->
    <div class="categories-section">
        <div class="category">
            <button class="category-btn" onclick="toggleCategory('rainfall')">Rainfall</button>
            <div id="rainfall-subcategories" class="subcategories">
                <div class="subcategory">
                    <label class="toggle-switch">
                        <input type="checkbox" id="rainfall-weekly-exceptional" data-layer="Weekly Exceptional Rainfall" data-legend="rainfall" onclick="toggleSubcategoryLayer(this)">
                        <span class="slider"></span>
                    </label>
                    <label for="rainfall-weekly-exceptional">Weekly Exceptional Rainfall</label>
                    <span class="info-icon" title="Latest: 5th Mar 2025 to 12th Mar 2025">ⓘ</span>
                </div>
                <div class="subcategory">
                    <label class="toggle-switch">
                        <input type="checkbox" id="rainfall-weekly-total" data-layer="Weekly Total Rainfall Forecast" data-legend="rainfall" onclick="toggleSubcategoryLayer(this)">
                        <span class="slider"></span>
                    </label>
                    <label for="rainfall-weekly-total">Weekly Total Rainfall Forecast</label>
                    <span class="info-icon" title="Latest: 5th Mar 2025 to 12th Mar 2025">ⓘ</span>
                </div>
            </div>
        </div>
        
        <div class="category">
            <button class="category-btn" onclick="toggleCategory('temperature')">Temperature</button>
            <div id="temperature-subcategories" class="subcategories">
                <div class="subcategory">
                    <label class="toggle-switch">
                        <input type="checkbox" id="temperature-current" data-layer="Current Temperature" data-legend="temperature" onclick="toggleSubcategoryLayer(this)">
                        <span class="slider"></span>
                    </label>
                    <label for="temperature-current">Current Temperature</label>
                    <span class="info-icon" title="Latest available data">ⓘ</span>
                </div>
                <div class="subcategory">
                    <label class="toggle-switch">
                        <input type="checkbox" id="temperature-forecast" data-layer="Temperature Forecast" data-legend="temperature" onclick="toggleSubcategoryLayer(this)">
                        <span class="slider"></span>
                    </label>
                    <label for="temperature-forecast">Temperature Forecast</label>
                    <span class="info-icon" title="7-day forecast">ⓘ</span>
                </div>
            </div>
        </div>
        
        <div class="category">
            <button class="category-btn" onclick="toggleCategory('climateChange')">Climate Change</button>
            <div id="climateChange-subcategories" class="subcategories">
                <div class="subcategory">
                    <label class="toggle-switch">
                        <input type="checkbox" id="climate-change-trends" data-layer="Climate Change Trends" data-legend="climate" onclick="toggleSubcategoryLayer(this)">
                        <span class="slider"></span>
                    </label>
                    <label for="climate-change-trends">Climate Change Trends</label>
                    <span class="info-icon" title="Historical trends">ⓘ</span>
                </div>
                <div class="subcategory">
                    <label class="toggle-switch">
                        <input type="checkbox" id="climate-change-impact" data-layer="Climate Change Impact" data-legend="climate" onclick="toggleSubcategoryLayer(this)">
                        <span class="slider"></span>
                    </label>
                    <label for="climate-change-impact">Climate Change Impact</label>
                    <span class="info-icon" title="Projected impact">ⓘ</span>
                </div>
            </div>
        </div>
        
        <div class="category">
            <button class="category-btn" onclick="toggleCategory('drought')">Drought</button>
            <div id="drought-subcategories" class="subcategories">
                <div class="subcategory">
                    <label class="toggle-switch">
                        <input type="checkbox" id="drought-current" data-layer="Current Drought Conditions" data-legend="drought" onclick="toggleSubcategoryLayer(this)">
                        <span class="slider"></span>
                    </label>
                    <label for="drought-current">Current Drought Conditions</label>
                    <span class="info-icon" title="Current conditions">ⓘ</span>
                </div>
                <div class="subcategory">
                    <label class="toggle-switch">
                        <input type="checkbox" id="drought-forecast" data-layer="Drought Forecast" data-legend="drought" onclick="toggleSubcategoryLayer(this)">
                        <span class="slider"></span>
                    </label>
                    <label for="drought-forecast">Drought Forecast</label>
                    <span class="info-icon" title="3-month forecast">ⓘ</span>
                </div>
            </div>
        </div>
    </div>
</div>


<!-- Tab container for Legend and Analysis -->
<div id="tab-container">
    <!-- Tab Navigation -->
    <div class="tab-navigation">
        <button id="legend-tab" class="tab-btn active">LEGEND</button>
        <button id="analysis-tab" class="tab-btn">ANALYSIS</button>
    </div>

    <!-- Legend Container (Legend Tab) -->
    <div id="legend-container" class="tab-content">
        <div id="legend-rainfall" class="legend-item" style="display: none;">
            <h4>Rainfall (mm)</h4>
            <div class="legend-gradient rainfall-gradient"></div>
            <div class="legend-labels">
                <span>0</span>
                <span>25</span>
                <span>50</span>
                <span>75</span>
                <span>100+</span>
            </div>
        </div>
        <div id="legend-temperature" class="legend-item" style="display: none;">
            <h4>Temperature (°C)</h4>
            <div class="legend-gradient temperature-gradient"></div>
            <div class="legend-labels">
                <span>0</span>
                <span>12.5</span>
                <span>25</span>
                <span>37.5</span>
                <span>50+</span>
            </div>
        </div>
        <div id="legend-drought" class="legend-item" style="display: none;">
            <h4>Drought Severity Index</h4>
            <div class="legend-gradient drought-gradient"></div>
            <div class="legend-labels">
                <span>0</span>
                <span>25</span>
                <span>50</span>
                <span>75</span>
                <span>100</span>
            </div>
        </div>
    </div>

    <!-- Analysis Container (Analysis Tab) -->
    <div id="analysis-container" class="tab-content" style="display: none;">
        <div id="analysis-content">
            <p>Click "Analyze" on a region marker to see results here.</p>
        </div>
    </div>
</div>
<script src="map.js"></script>
"""

# Add custom HTML to map
mapObj.get_root().html.add_child(folium.Element(custom_sidebar))

# Save map to file
mapObj.save('output.html')