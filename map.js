// Initialize state for all subcategories
let subcategoryState = {};
let activeLegends = {};
let activeTab = 'legend'; // Default tab is legend

// Function to toggle category (expand/collapse)
// Hides all subcategories before toggling the selected one.
//Updates the UI by highlighting the active category button.

function toggleCategory(category) {
    // Get the selected category's subcategories
    const targetSubcategories = document.getElementById(`${category}-subcategories`);
    
    // Check if it's already visible
    const isVisible = targetSubcategories && 
                     targetSubcategories.style.display === 'block';
    
    // Get all subcategories elements
    const allSubcategories = document.querySelectorAll('.subcategories');
    
    // Hide all subcategories first
    allSubcategories.forEach(el => {
        el.style.display = 'none';
    });
    
    // If it wasn't visible, show it (otherwise it remains hidden)
    if (targetSubcategories && !isVisible) {
        targetSubcategories.style.display = 'block';
    }
    
    // Highlight the active category button - only if we're opening
    const allCategoryBtns = document.querySelectorAll('.category-btn');
    allCategoryBtns.forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Add active class to the clicked button - only if we're opening
    if (!isVisible) {
        document.querySelector(`.category-btn[onclick="toggleCategory('${category}')"]`).classList.add('active');
    }
}

// Function to toggle a specific subcategory layer
//Syncs UI checkbox states with Folium's layer controls.
//Simulates a click on the corresponding layer control in Folium.
//Calls updateLegendVisibility() to manage legend display.

function toggleSubcategoryLayer(checkbox) {
    const layerName = checkbox.dataset.layer;
    const legendType = checkbox.dataset.legend;
    const isChecked = checkbox.checked;
    
    // Store the state of the checkbox
    subcategoryState[checkbox.id] = isChecked;
    
    // Find the corresponding layer control checkbox in Folium's layer control
    const layerControls = document.querySelectorAll('.leaflet-control-layers-overlays input');
    
    layerControls.forEach(input => { //Iterates over each layer control checkbox
        const label = input.nextElementSibling.textContent.trim();
        if (label === layerName && input.checked !== isChecked) {
            // Programmatically click the Folium layer checkbox if its state doesn't match the checkbox state.
            input.click();
        }
    });
    
    // Update legend visibility
    updateLegendVisibility(legendType, isChecked);
}

// Function to update legend visibility
//Tracks active legends in activeLegends based on layer visibility.
//If no other subcategory of the same type is active, the legend is hidden.
//Only updates the legend display if the legend tab is currently selected.

function updateLegendVisibility(legendType, isChecked) {
    if (!legendType) return;
    
    // Track if this legend should be shown. Sets the legend type to active if the checkbox is checked.

    if (isChecked) {
        activeLegends[legendType] = true;
    } else {
        // Only set to false if no other layer of this type is active
        const otherLayersOfSameType = document.querySelectorAll(`[data-legend="${legendType}"]`);
        let anyOtherActive = false;
        otherLayersOfSameType.forEach(layer => {
            if (layer.checked && layer !== document.activeElement) {
                anyOtherActive = true;
            }
        });
        
        if (!anyOtherActive) {
            activeLegends[legendType] = false;
        }
    }
    
    // Update legend visibility if we're in the legend tab
    if (activeTab === 'legend') {
        for (const type in activeLegends) {
            const legendElement = document.getElementById(`legend-${type}`);
            if (legendElement) {
                legendElement.style.display = activeLegends[type] ? 'block' : 'none';
            }
        }
    }
}

// Function to switch between tabs (legend and analysis)
function switchTab(tabName) {
    activeTab = tabName;
    
    // Update tab button styles
    document.getElementById('legend-tab').classList.toggle('active', tabName === 'legend');
    document.getElementById('analysis-tab').classList.toggle('active', tabName === 'analysis');
    
    // Show/hide appropriate container
    const legendContainer = document.getElementById('legend-container');
    const analysisContainer = document.getElementById('analysis-container');
    
    if (tabName === 'legend') {
        legendContainer.style.display = 'block';
        analysisContainer.style.display = 'none';
        
        // Update legend items visibility based on active layers
        for (const type in activeLegends) {
            const legendElement = document.getElementById(`legend-${type}`);
            if (legendElement) {
                legendElement.style.display = activeLegends[type] ? 'block' : 'none';
            }
        }
    } else { // analysis
        legendContainer.style.display = 'none';
        analysisContainer.style.display = 'block';
    }
}

// Function to populate analysis content when "Analyze" button is clicked
function performAnalysis(regionName) {
    const analysisContainer = document.getElementById('analysis-container');
    if (!analysisContainer) return;
    
    // Switch to analysis tab
    switchTab('analysis');
    
    // Update analysis content
    const analysisContent = document.getElementById('analysis-content');
    if (analysisContent) {
        analysisContent.innerHTML = `
            <h4>${regionName.toUpperCase()}</h4>
            <div class="analysis-header">
                <span>WEEKLY EXCEPTIONAL RAINFALL - POPULATION EXPOSED FOR ${regionName.toUpperCase()}</span>
                <button class="info-button">ⓘ</button>
            </div>
            <div class="analysis-details">
                <p>Forecast Period: 5th Mar 2025 to 12th Mar 2025</p>
                <div class="analysis-data">
                    <p>These areas are highlighted based on the sampling of the selected period. Results may be clearer at closer zoom levels.</p>
                </div>
                <div class="analysis-buttons">
                    <button class="refresh-button">REFRESH ANALYSIS</button>
                    <button class="cancel-button">CANCEL ANALYSIS</button>
                </div>
                <div class="interest-section">
                    <h5>INTERESTED IN THIS PARTICULAR AREA?</h5>
                    <p>Save this area to create a dashboard with a more in-depth analysis and receive email updates on products that we monitor.</p>
                </div>
            </div>
        `;
        
        // Add event listener to cancel button
        const cancelButton = analysisContent.querySelector('.cancel-button');
        if (cancelButton) {
            cancelButton.addEventListener('click', () => {
                switchTab('legend');
            });
        }
    }
}

// Event listener for the "Analyze" button using event delegation
document.addEventListener('click', function(event) {
    if (event.target && event.target.id === 'analyze-button') {
        // Get the region name from the popup (parent elements)
        const popup = event.target.closest('.leaflet-popup-content');
        let regionName = "Selected Region";
        
        if (popup) {
            const heading = popup.querySelector('h3');
            if (heading) {
                regionName = heading.textContent;
            }
        }
        
        performAnalysis(regionName);
    }
});

// Function to sync checkboxes with Folium layer states
function syncLayerStates() {
    const layerControls = document.querySelectorAll('.leaflet-control-layers-overlays input');
    const subcategoryCheckboxes = document.querySelectorAll('.subcategory input[type="checkbox"]');
    
    // Reset active legends
    activeLegends = {
        rainfall: false,
        temperature: false,
        drought: false,
        climate: false
    };
    
    // Create a mapping of layer names to their current state
    const layerStates = {};
    layerControls.forEach(input => {
        const label = input.nextElementSibling.textContent.trim();
        layerStates[label] = input.checked;
    });
    
    // Update subcategory checkboxes based on layer states
    subcategoryCheckboxes.forEach(checkbox => {
        const layerName = checkbox.dataset.layer;
        const legendType = checkbox.dataset.legend;
        
        if (layerName in layerStates) {
            checkbox.checked = layerStates[layerName];
            subcategoryState[checkbox.id] = layerStates[layerName];
            
            // Update legend state
            if (checkbox.checked && legendType) {
                activeLegends[legendType] = true;
            }
        }
    });
    
    // Update all legends visibility if in legend tab
    if (activeTab === 'legend') {
        for (const type in activeLegends) {
            const legendElement = document.getElementById(`legend-${type}`);
            if (legendElement) {
                legendElement.style.display = activeLegends[type] ? 'block' : 'none';
            }
        }
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    // Hide all subcategories initially
    const allSubcategories = document.querySelectorAll('.subcategories');
    allSubcategories.forEach(el => {
        el.style.display = 'none';
    });
    
    // Set up tabs
    const legendTabBtn = document.getElementById('legend-tab');
    const analysisTabBtn = document.getElementById('analysis-tab');
    
    if (legendTabBtn) {
        legendTabBtn.addEventListener('click', () => switchTab('legend'));
    }
    
    if (analysisTabBtn) {
        analysisTabBtn.addEventListener('click', () => switchTab('analysis'));
    }
    
    // Initialize tab state
    switchTab('legend');
    
    // Initialize active legends state
    activeLegends = {
        rainfall: false,
        temperature: false,
        drought: false,
        climate: false
    };
    
    // Set up monitoring of Folium layer changes
    setTimeout(() => {
        // Initial sync
        syncLayerStates();
        
        // Add event listeners to Folium layer controls
        const layerControls = document.querySelectorAll('.leaflet-control-layers-overlays input');
        layerControls.forEach(input => {
            input.addEventListener('change', syncLayerStates);
        });
    }, 1000); // Wait for Folium to initialize
    
    // Show tooltip on info icon hover
    const infoIcons = document.querySelectorAll('.info-icon');
    infoIcons.forEach(icon => {
        icon.addEventListener('mouseover', function() {
            const tooltip = document.createElement('div');
            tooltip.className = 'tooltip';
            tooltip.textContent = this.title;
            document.body.appendChild(tooltip);
            
            const rect = this.getBoundingClientRect();
            tooltip.style.top = `${rect.bottom + 5}px`;
            tooltip.style.left = `${rect.left + 5}px`;
            
            this.addEventListener('mouseout', function() {
                document.body.removeChild(tooltip);
            }, { once: true });
        });
    });
});