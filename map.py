import folium
import json
from folium.plugins import HeatMap
import branca.colormap as cm
import numpy as np
from folium.raster_layers import ImageOverlay
from PIL import Image
from matplotlib import pyplot as plt
import io
import base64
import geopandas as gpd
from matplotlib.path import Path
from matplotlib.patches import PathPatch


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
        icon=folium.Icon(icon='map-marker', prefix='fa', color='red'),
        tooltip=d[3],
        popup=folium.Popup(f"""<h3>{d[3]}</h3> <br/>
                This is the <b>{d[3]}</b> region<br/><br/>
                <button id="analyze-button">Analyze</button> """, max_width=500)
    ).add_to(markerLayer)


# Feature Groups for different hazard types and their subcategories
# Rainfall subcategories
rainfall_weekly_exceptional = folium.FeatureGroup(name="Weekly Exceptional Rainfall", show=False)
#rainfall_weekly_total = folium.FeatureGroup(name="Weekly Total Rainfall Forecast", show=False)

# Temperature subcategories
temperature_current = folium.FeatureGroup(name="Current Temperature", show=False)

# Climate Change subcategories
climate_change_trends = folium.FeatureGroup(name="Climate Change Trends", show=False)

# Drought subcategories
drought_current = folium.FeatureGroup(name="Current Drought Conditions", show=False)


# Sample Heatmap Data
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

# Create colormaps for each hazard type
rainfall_colormap = cm.LinearColormap(
    ['blue', 'green', 'yellow', 'orange', 'red'],
    vmin=0, vmax=100,
    caption='Rainfall (mm)'
)

temperature_colormap = cm.LinearColormap(
    ['blue', 'green', 'yellow', 'orange', 'red'],
    vmin=0, vmax=50,
    caption='Temperature (°C)'
)

drought_colormap = cm.LinearColormap(
    ['green', 'yellow', 'orange', 'red', 'darkred'],
    vmin=0, vmax=100,
    caption='Drought Severity Index'
)

# Add HeatMap layers
HeatMap(data=rainfall_data, radius=15, blur=10).add_to(rainfall_weekly_exceptional)
HeatMap(data=current_temperature_data, radius=15, blur=10).add_to(temperature_current)
HeatMap(data=current_drought_data, radius=15, blur=10).add_to(drought_current)

# Add layers to map
mapObj.add_child(rainfall_weekly_exceptional)
mapObj.add_child(temperature_current)
mapObj.add_child(climate_change_trends)
mapObj.add_child(drought_current)


def add_masked_raster_to_map(map_obj, json_file_path, geojson_path, layer_name="Masked Raster", colormap='viridis', opacity=0.8, show=True):
    """
    Add a JSON raster to the map, masked to a GeoJSON boundary using image processing
    
    Parameters:
    -----------
    map_obj : folium.Map
        The map object to add the layer to
    json_file_path : str
        Path to the JSON file containing raster data
    geojson_path : str
        Path to the GeoJSON file containing the boundary to mask with
    layer_name : str
        Name of the layer for the layer control
    colormap : str
        Matplotlib colormap name
    opacity : float
        Opacity of the layer (0-1)
    show : bool
        Whether to show the layer initially
    """
    # Load the JSON data
    with open(json_file_path, 'r') as f:
        json_data = json.load(f)
    
    # Extract raster data
    if isinstance(json_data, list) and isinstance(json_data[0], list):
        raster_array = np.array(json_data)
    elif 'data' in json_data and isinstance(json_data['data'], list):
        raster_array = np.array(json_data['data'])
    else:
        if 'width' in json_data and 'height' in json_data and 'values' in json_data:
            width = json_data['width']
            height = json_data['height']
            values = json_data['values']
            raster_array = np.array(values).reshape(height, width)
        else:
            raise ValueError("Unsupported JSON structure.")
    
    # Extract bounds
    if 'bounds' in json_data:
        bounds = json_data['bounds']
    else:
        bounds = [[3.0, 33.0], [15.0, 48.0]]  # Default Ethiopia bounds
    
    # Create a mask using the GeoJSON
    # Load the GeoJSON as a GeoDataFrame
    ethiopia_gdf = gpd.read_file(geojson_path)
    
    # Create a mask based on the raster dimensions
    y_size, x_size = raster_array.shape
    
    # Create coordinate arrays for the raster - FIXED: Reverse y_coords order to flip the image
    # The key fix is here - we need to reverse the order of y_coords to match the orientation of the data
    y_coords = np.linspace(bounds[1][0], bounds[0][0], y_size)  # Reversed order from north to south
    x_coords = np.linspace(bounds[0][1], bounds[1][1], x_size)
    
    # Create a mesh grid
    xx, yy = np.meshgrid(x_coords, y_coords)
    
    # Convert to points
    points = np.vstack([xx.flatten(), yy.flatten()]).T
    
    # Create a mask from the Ethiopia boundary
    mask = np.zeros((y_size, x_size), dtype=bool)
    
    # For each polygon in the GeoJSON
    for idx, row in ethiopia_gdf.iterrows():
        geom = row.geometry
        
        # Handle MultiPolygon vs Polygon
        if geom.geom_type == 'MultiPolygon':
            for poly in geom.geoms:
                x, y = poly.exterior.xy
                poly_path = Path(np.column_stack([x, y]))
                mask_points = poly_path.contains_points(points).reshape(y_size, x_size)
                mask = mask | mask_points
        else:  # Polygon
            x, y = geom.exterior.xy
            poly_path = Path(np.column_stack([x, y]))
            mask_points = poly_path.contains_points(points).reshape(y_size, x_size)
            mask = mask | mask_points
    
    # Apply the mask to the raster
    masked_raster = np.ma.masked_array(raster_array, ~mask)
    
    # Create a colormap
    cmap = plt.get_cmap(colormap)
    
    # Normalize the data
    if np.ma.is_masked(masked_raster) and not np.all(masked_raster.mask):
        vmin = np.ma.min(masked_raster)
        vmax = np.ma.max(masked_raster)
        norm = plt.Normalize(vmin, vmax)
        
        # Create an RGBA image
        rgba_img = cmap(norm(masked_raster))
        
        # Set alpha channel to 0 for masked areas
        rgba_img[..., 3] = np.where(mask, opacity, 0)
        
        # Create a figure and render the image
        fig, ax = plt.subplots(figsize=(20, 20), frameon=False)
        ax.imshow(rgba_img)
        ax.axis('off')
        
        # Save with transparency
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0, 
                   transparent=True, dpi=150)
        plt.close(fig)
        buf.seek(0)
        
        # Convert to PIL Image and preserve transparency
        image = Image.open(buf)
        
        # Save as PNG with transparency
        img_data = io.BytesIO()
        image.save(img_data, format='PNG')
        img_data.seek(0)
        
        # Encode as base64
        encoded = base64.b64encode(img_data.read()).decode('ascii')
        img_src = f"data:image/png;base64,{encoded}"
        
        # Create new feature group
        rainfall_weekly_total = folium.FeatureGroup(name="Weekly Total Rainfall Forecast", show=show)
        
        # Add the image overlay
        overlay = folium.raster_layers.ImageOverlay(
            image=img_src,
            bounds=bounds,
            opacity=0.9,  
            name=layer_name,
            pixelated=False,
        ).add_to(rainfall_weekly_total)
        
        # Add the feature group to the map
        map_obj.add_child(rainfall_weekly_total)
        return rainfall_weekly_total
    else:
        print("Error: Empty masked raster array.")
        return None
        
rainfall_raster_layer = add_masked_raster_to_map(
    mapObj,
    "eth_rf.json",
    "et.json",
    layer_name="Ethiopia Rainfall Data",
    colormap='Blues',  # Using Blues colormap for rainfall data
    opacity=1.0,
    show=False  # Initially hidden, can be toggled via the layer control
)

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
                    <input type="checkbox" id="rainfall-weekly-exceptional" data-layer="Weekly Exceptional Rainfall" data-legend="rainfall" onclick="toggleSubcategoryLayer(this)">
                    <label for="rainfall-weekly-exceptional">Weekly Exceptional Rainfall</label>
                    <span class="info-icon" title="Latest: 5th Mar 2025 to 12th Mar 2025">ⓘ</span>
                </div>
                <div class="subcategory">
                    <input type="checkbox" id="rainfall-weekly-total" data-layer="Weekly Total Rainfall Forecast" data-legend="rainfall" onclick="toggleSubcategoryLayer(this)">
                    <label for="rainfall-weekly-total">Weekly Total Rainfall Forecast</label>
                    <span class="info-icon" title="Latest: 5th Mar 2025 to 12th Mar 2025">ⓘ</span>
                </div>
            </div>
        </div>
        
        <div class="category">
            <button class="category-btn" onclick="toggleCategory('temperature')">Temperature</button>
            <div id="temperature-subcategories" class="subcategories">
                <div class="subcategory">
                    <input type="checkbox" id="temperature-current" data-layer="Current Temperature" data-legend="temperature" onclick="toggleSubcategoryLayer(this)">
                    <label for="temperature-current">Current Temperature</label>
                    <span class="info-icon" title="Latest available data">ⓘ</span>
                </div>
                <div class="subcategory">
                    <input type="checkbox" id="temperature-forecast" data-layer="Temperature Forecast" data-legend="temperature" onclick="toggleSubcategoryLayer(this)">
                    <label for="temperature-forecast">Temperature Forecast</label>
                    <span class="info-icon" title="7-day forecast">ⓘ</span>
                </div>
            </div>
        </div>
        
        <div class="category">
            <button class="category-btn" onclick="toggleCategory('climateChange')">Climate Change</button>
            <div id="climateChange-subcategories" class="subcategories">
                <div class="subcategory">
                    <input type="checkbox" id="climate-change-trends" data-layer="Climate Change Trends" data-legend="climate" onclick="toggleSubcategoryLayer(this)">
                    <label for="climate-change-trends">Climate Change Trends</label>
                    <span class="info-icon" title="Historical trends">ⓘ</span>
                </div>
                <div class="subcategory">
                    <input type="checkbox" id="climate-change-impact" data-layer="Climate Change Impact" data-legend="climate" onclick="toggleSubcategoryLayer(this)">
                    <label for="climate-change-impact">Climate Change Impact</label>
                    <span class="info-icon" title="Projected impact">ⓘ</span>
                </div>
            </div>
        </div>
        
        <div class="category">
            <button class="category-btn" onclick="toggleCategory('drought')">Drought</button>
            <div id="drought-subcategories" class="subcategories">
                <div class="subcategory">
                    <input type="checkbox" id="drought-current" data-layer="Current Drought Conditions" data-legend="drought" onclick="toggleSubcategoryLayer(this)">
                    <label for="drought-current">Current Drought Conditions</label>
                    <span class="info-icon" title="Current conditions">ⓘ</span>
                </div>
                <div class="subcategory">
                    <input type="checkbox" id="drought-forecast" data-layer="Drought Forecast" data-legend="drought" onclick="toggleSubcategoryLayer(this)">
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