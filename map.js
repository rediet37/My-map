var activeLayer = null;
var map = mapObj.get_name(); //...

function toggleCategory(category) {
    document.getElementById("sub-options").style.display = "block";
    document.getElementById("category-title").innerText = category.charAt(0).toUpperCase() + category.slice(1);
    
    // Set the corresponding folium layer
    if (category === 'rainfall') activeLayer = rainfallLayer; //.get_name();
    else if (category === 'temperature') activeLayer = temperatureLayer;
    else if (category === 'climateChange') activeLayer = climateChangeLayer;
    else if (category === 'drought') activeLayer = droughtLayer;
    
    document.getElementById("toggle-layer").checked = false;
    map.removeLayer(activeLayer); // Ensure layer is hidden initially
}

function toggleLayer() {
    if (document.getElementById("toggle-layer").checked) {
        map.addLayer(activeLayer);
    } else {
        map.removeLayer(activeLayer);
    }
}

