import folium
import json
from folium.plugins import HeatMap
import branca.colormap as cm

# Initialize the map
mapObj = folium.Map(location=[9.102096738726456, 40.71533203125001], zoom_start=6, zoom_control=False)

# Load the seasonal climate data
with open("seasonal_data_2005_2014.json", "r", encoding="utf-8") as f:
    climate_data = json.load(f)

# Load the Ethiopia GeoJSON file
with open("et.json", "r", encoding="utf-8") as f:
    ethiopia_geojson = json.load(f)

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

# Improved function to calculate the centroid of a polygon
def calculate_centroid(coordinates):
    """Calculate the centroid of a polygon using the shoelace formula."""
    area = 0
    cx = cy = 0
    
    # For simple polygon with too few points
    if len(coordinates) < 3:
        return sum(p[1] for p in coordinates) / len(coordinates), sum(p[0] for p in coordinates) / len(coordinates)
    
    for i in range(len(coordinates) - 1):
        # Cross product for area calculation
        area_part = coordinates[i][0] * coordinates[i+1][1] - coordinates[i+1][0] * coordinates[i][1]
        area += area_part
        
        # Weighted coordinates
        cx += (coordinates[i][0] + coordinates[i+1][0]) * area_part
        cy += (coordinates[i][1] + coordinates[i+1][1]) * area_part
    
    # Finish the area calculation
    area /= 2
    area = abs(area)  # Make sure area is positive
    
    # Calculate centroid
    if area != 0:
        cx = cx / (6 * area)
        cy = cy / (6 * area)
        return cy, cx  # Return lat, lon
    else:
        # Fallback to average if area is zero
        return sum(p[1] for p in coordinates) / len(coordinates), sum(p[0] for p in coordinates) / len(coordinates)

# Function to calculate bounds-based center (visual center)
def calculate_visual_center(coordinates):
    """Calculate the center of the bounding box of a polygon."""
    # Extract all lon/lat coordinates
    all_lons = [coord[0] for coord in coordinates]
    all_lats = [coord[1] for coord in coordinates]
    
    # Calculate bounds
    min_lon = min(all_lons)
    max_lon = max(all_lons)
    min_lat = min(all_lats)
    max_lat = max(all_lats)
    
    # Return the center of the bounding box
    return (min_lat + max_lat) / 2, (min_lon + max_lon) / 2

# Extract region information from the GeoJSON file and add markers
for feature in ethiopia_geojson['features']:
    # Get region name from properties
    region_name = feature['properties'].get('name', 'Unknown Region')
    
    # Calculate marker placement based on geometry type
    if feature['geometry']['type'] == 'Polygon':
        # For simple polygons
        coordinates = feature['geometry']['coordinates'][0]  # Use outer ring
        # Try mathematical centroid first
        lat, lon = calculate_centroid(coordinates)
        
        # Check if the centroid is within reasonable bounds
        # If not, use visual center as fallback
        min_lon = min(coord[0] for coord in coordinates)
        max_lon = max(coord[0] for coord in coordinates)
        min_lat = min(coord[1] for coord in coordinates)
        max_lat = max(coord[1] for coord in coordinates)
        
        # If centroid is outside the bounding box, use visual center instead
        if not (min_lon <= lon <= max_lon and min_lat <= lat <= max_lat):
            lat, lon = calculate_visual_center(coordinates)
            
    elif feature['geometry']['type'] == 'MultiPolygon':
        # For multipolygons, find the largest polygon and use its centroid
        largest_area = 0
        lat = lon = 0
        
        for polygon in feature['geometry']['coordinates']:
            coords = polygon[0]  # Outer ring of this polygon
            
            # Calculate area to determine the largest polygon
            poly_area = 0
            for i in range(len(coords) - 1):
                poly_area += coords[i][0] * coords[i+1][1] - coords[i+1][0] * coords[i][1]
            poly_area = abs(poly_area / 2)
            
            if poly_area > largest_area:
                largest_area = poly_area
                curr_lat, curr_lon = calculate_centroid(coords)
                
                # Verify the centroid is inside the polygon's bounds
                min_lon = min(coord[0] for coord in coords)
                max_lon = max(coord[0] for coord in coords)
                min_lat = min(coord[1] for coord in coords)
                max_lat = max(coord[1] for coord in coords)
                
                # If outside bounds, use visual center
                if not (min_lon <= curr_lon <= max_lon and min_lat <= curr_lat <= max_lat):
                    curr_lat, curr_lon = calculate_visual_center(coords)
                    
                lat, lon = curr_lat, curr_lon
    else:
        # Skip if not a polygon or multipolygon
        continue
    
    # Add marker at the calculated position
    folium.Marker(
        location=[lat, lon],
        icon=folium.Icon(icon='map-marker', prefix='fa', color='darkblue'),
        tooltip=region_name,
        popup=folium.Popup(f"""<h3>{region_name}</h3> <br/>
                This is the <b>{region_name}</b> region<br/><br/>
                <button id="analyze-button" onclick="analyzeRegion('{region_name}')">Analyze</button> """, max_width=500)
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

# Load the GeoJSON file for rainfall data
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

# Add Layer Control
folium.LayerControl().add_to(mapObj)

# Custom sidebar and tab structure (from your original code)
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
        <button id="legend-tab" class="tab-btn active" onclick="switchTab('legend')">LEGEND</button>
        <button id="analysis-tab" class="tab-btn" onclick="switchTab('analysis')">ANALYSIS</button>
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
            <div id="analysis-placeholder">
                <p>Click "Analyze" on a region marker to see climate analysis.</p>
            </div>
            <div id="analysis-region-data" style="display: none;">
                <h3 id="region-title">Region Analysis</h3>
                
                <!-- Seasonal buttons -->
                <div class="analysis-buttons">
                    <button id="btn-fmam" class="season-btn" onclick="showSeasonData('fmam')">FMAM</button>
                    <button id="btn-jjas" class="season-btn" onclick="showSeasonData('jjas')">JJAS</button>
                    <button id="btn-ondj" class="season-btn" onclick="showSeasonData('ondj')">ONDJ</button>
                    <button id="btn-annual" class="season-btn" onclick="showAnnualCycle()">Annual Cycle</button> 
                    <button id="btn-timeseries" class="season-btn" onclick="showTimeSeries()">Time Series</button>
                </div>
                
                <!-- Data visualization container -->
                <div id="data-visualization">
                    <div id="chart-container">
                        <canvas id="climate-chart" width="400" height="300"></canvas>
                    </div>
                    <div id="data-summary"></div>
                </div>
            </div>
        </div>
    </div>
</div>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script src="map.js"></script>

<script>
// Add a function to handle region analysis clicks and pass the region name to the map.js functions
function analyzeRegion(regionName) {
    // Update the region title in the analysis tab
    document.getElementById('region-title').textContent = regionName + ' Analysis';
    
    // Hide the placeholder and show the analysis content
    document.getElementById('analysis-placeholder').style.display = 'none';
    document.getElementById('analysis-region-data').style.display = 'block';
    
    // Switch to the analysis tab
    switchTab('analysis');
    
    // You can add more code here to load specific data for the region
    // This would connect to the existing map.js functions
}
</script>
"""

# Add custom HTML to map
mapObj.get_root().html.add_child(folium.Element(custom_sidebar))

# Pass the climate data to JavaScript
folium.Element(f'<script>const seasonalData = {json.dumps(climate_data)};</script>').add_to(mapObj.get_root().html)

# Save map to file
mapObj.save('output.html')