// Initialize state for all subcategories
let subcategoryState = {};
let activeLegends = {};
let activeTab = 'legend'; // Default tab is legend

let climateData = null; // Will store the seasonal climate data
let currentRegion = null; // Store the currently selected region
let chart = null; // Store the chart instance for reuse/updates

// Load climate data on page load
document.addEventListener('DOMContentLoaded', async function() {
    try {
        const response = await fetch('seasonal_data_2005_2014.json');
        climateData = await response.json();
        console.log('Climate data loaded:', climateData);
        
        // Set up event listeners for analyze buttons in popups
        setupAnalyzeButtons();
        
    } catch (error) {
        console.error('Error loading climate data:', error);
    }
});


// Function to toggle category (expand/collapse)
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
function toggleSubcategoryLayer(checkbox) {
    const layerName = checkbox.dataset.layer;
    const legendType = checkbox.dataset.legend;
    const isChecked = checkbox.checked;
    
    // Store the state
    subcategoryState[checkbox.id] = isChecked;
    
    // Find the corresponding layer control checkbox in Folium's layer control
    const layerControls = document.querySelectorAll('.leaflet-control-layers-overlays input');
    
    layerControls.forEach(input => {
        const label = input.nextElementSibling.textContent.trim();
        if (label === layerName && input.checked !== isChecked) {
            // Programmatically click the Folium layer checkbox
            input.click();
        }
    });
    
    // Update legend visibility
    updateLegendVisibility(legendType, isChecked);
}

// Function to update legend visibility
function updateLegendVisibility(legendType, isChecked) {
    if (!legendType) return;
    
    // Track if this legend should be shown
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

// Set up event listeners for the Analyze buttons in map popups
function setupAnalyzeButtons() {
    // Use MutationObserver to detect when popups are added to the DOM
    const observer = new MutationObserver(mutations => {
        mutations.forEach(mutation => {
            mutation.addedNodes.forEach(node => {
                if (node.nodeType === Node.ELEMENT_NODE) {
                    const analyzeButton = node.querySelector('#analyze-button');
                    if (analyzeButton) {
                        analyzeButton.addEventListener('click', function() {
                            // Get the region name from the popup content
                            const popupContent = analyzeButton.closest('.leaflet-popup-content');
                            const regionName = popupContent.querySelector('h3').textContent;
                            
                            // Switch to analysis tab and show data for the region
                            switchTab('analysis');
                            showRegionAnalysis(regionName);
                        });
                    }
                }
            });
        });
    });
    
    // Start observing the document body
    observer.observe(document.body, { childList: true, subtree: true });
}

// Show analysis for the selected region
function showRegionAnalysis(regionName) {
    // Set current region
    currentRegion = regionName;
    
    // Update UI
    document.getElementById('analysis-placeholder').style.display = 'none';
    document.getElementById('analysis-region-data').style.display = 'block';
    document.getElementById('region-title').textContent = `${regionName} Region Analysis`;
    
    // Show FMAM season data by default
    showSeasonData('fmam');
}

// Show seasonal data
function showSeasonData(season) {
    if (!climateData || !currentRegion || !climateData[currentRegion]) {
        console.error('Climate data not available for region:', currentRegion);
        return;
    }
    
    // Highlight the active season button
    document.querySelectorAll('.season-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    document.getElementById(`btn-${season}`).classList.add('active');
    
    // Get data for the selected season
    const seasonData = climateData[currentRegion][season];
    if (!seasonData) {
        console.error(`Data for season ${season} not available`);
        return;
    }
    
    // Prepare the data for the chart
    const years = Array.from({length: seasonData.length}, (_, i) => 2005 + i);
    
    // Create or update the chart
    createBarChart(years, seasonData, `${season.toUpperCase()} Seasonal Rainfall (2005-2014)`, 'Year', 'Rainfall (mm)');
    
    // Display summary statistics
    const average = (seasonData.reduce((a, b) => a + b, 0) / seasonData.length).toFixed(2);
    const min = Math.min(...seasonData).toFixed(2);
    const max = Math.max(...seasonData).toFixed(2);
    
    document.getElementById('data-summary').innerHTML = `
        <h4>Summary Statistics:</h4>
        <p><strong>Average Rainfall:</strong> ${average} mm</p>
        <p><strong>Minimum:</strong> ${min} mm (${years[seasonData.indexOf(Math.min(...seasonData))]})</p>
        <p><strong>Maximum:</strong> ${max} mm (${years[seasonData.indexOf(Math.max(...seasonData))]})</p>
    `;
}

// Show annual cycle data
function showAnnualCycle() {
    if (!climateData || !currentRegion || !climateData[currentRegion]) {
        console.error('Climate data not available for region:', currentRegion);
        return;
    }
    
    // Highlight the active button
    document.querySelectorAll('.season-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    document.getElementById('btn-annual').classList.add('active');
    
    // Prepare data for the annual cycle
    const seasonLabels = ['FMAM', 'JJAS', 'ONDJ'];
    const averagesBySeason = seasonLabels.map(season => {
        const seasonKey = season.toLowerCase();
        const seasonData = climateData[currentRegion][seasonKey];
        return seasonData ? (seasonData.reduce((a, b) => a + b, 0) / seasonData.length) : 0;
    });
    
    // Create or update the chart
    createBarChart(seasonLabels, averagesBySeason, 'Average Rainfall by Season (2005-2014)', 'Season', 'Average Rainfall (mm)');
    
    // Display summary
    const annualAverage = (averagesBySeason.reduce((a, b) => a + b, 0) / averagesBySeason.length).toFixed(2);
    const wetSeason = seasonLabels[averagesBySeason.indexOf(Math.max(...averagesBySeason))];
    const drySeason = seasonLabels[averagesBySeason.indexOf(Math.min(...averagesBySeason))];
    
    document.getElementById('data-summary').innerHTML = `
        <h4>Annual Cycle Summary:</h4>
        <p><strong>Overall Average:</strong> ${annualAverage} mm per season</p>
        <p><strong>Wettest Season:</strong> ${wetSeason} (${Math.max(...averagesBySeason).toFixed(2)} mm)</p>
        <p><strong>Driest Season:</strong> ${drySeason} (${Math.min(...averagesBySeason).toFixed(2)} mm)</p>
    `;
}

// Show time series data
function showTimeSeries() {
    if (!climateData || !currentRegion || !climateData[currentRegion]) {
        console.error('Climate data not available for region:', currentRegion);
        return;
    }
    
    // Highlight the active button
    document.querySelectorAll('.season-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    document.getElementById('btn-timeseries').classList.add('active');
    
    // Prepare data for all seasons
    const years = Array.from({length: 10}, (_, i) => 2005 + i);
    const fmamData = climateData[currentRegion]['fmam'] || [];
    const jjasData = climateData[currentRegion]['jjas'] || [];
    const ondjData = climateData[currentRegion]['ondj'] || [];
    
    // Create or update the time series chart
    createTimeSeriesChart(years, fmamData, jjasData, ondjData);
    
    // Display summary
    const fmamTrend = calculateTrend(fmamData);
    const jjasTrend = calculateTrend(jjasData);
    const ondjTrend = calculateTrend(ondjData);
    
    document.getElementById('data-summary').innerHTML = `
        <h4>Time Series Analysis (2005-2014):</h4>
        <p><strong>FMAM Trend:</strong> ${fmamTrend > 0 ? 'Increasing' : 'Decreasing'} (${Math.abs(fmamTrend).toFixed(2)} mm/year)</p>
        <p><strong>JJAS Trend:</strong> ${jjasTrend > 0 ? 'Increasing' : 'Decreasing'} (${Math.abs(jjasTrend).toFixed(2)} mm/year)</p>
        <p><strong>ONDJ Trend:</strong> ${ondjTrend > 0 ? 'Increasing' : 'Decreasing'} (${Math.abs(ondjTrend).toFixed(2)} mm/year)</p>
    `;
}

// Calculate a simple linear trend
function calculateTrend(data) {
    if (!data || data.length < 2) return 0;
    
    const n = data.length;
    let sumX = 0, sumY = 0, sumXY = 0, sumX2 = 0;
    
    for (let i = 0; i < n; i++) {
        sumX += i;
        sumY += data[i];
        sumXY += i * data[i];
        sumX2 += i * i;
    }
    
    const slope = (n * sumXY - sumX * sumY) / (n * sumX2 - sumX * sumX);
    return slope;
}

// Create or update a bar chart
function createBarChart(labels, data, title, xAxisLabel, yAxisLabel) {
    const ctx = document.getElementById('climate-chart').getContext('2d');
    
    // Destroy previous chart if it exists
    if (chart) {
        chart.destroy();
    }
    
    chart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: title,
                data: data,
                backgroundColor: 'rgba(54, 162, 235, 0.6)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: yAxisLabel
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: xAxisLabel
                    }
                }
            },
            plugins: {
                title: {
                    display: true,
                    text: title,
                    font: {
                        size: 16
                    }
                }
            }
        }
    });
}

// Create or update a time series chart
function createTimeSeriesChart(years, fmamData, jjasData, ondjData) {
    const ctx = document.getElementById('climate-chart').getContext('2d');
    
    // Destroy previous chart if it exists
    if (chart) {
        chart.destroy();
    }
    
    chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: years,
            datasets: [
                {
                    label: 'FMAM Season',
                    data: fmamData,
                    borderColor: 'rgba(54, 162, 235, 1)',
                    backgroundColor: 'rgba(54, 162, 235, 0.1)',
                    borderWidth: 2,
                    tension: 0.1
                },
                {
                    label: 'JJAS Season',
                    data: jjasData,
                    borderColor: 'rgba(75, 192, 192, 1)',
                    backgroundColor: 'rgba(75, 192, 192, 0.1)',
                    borderWidth: 2,
                    tension: 0.1
                },
                {
                    label: 'ONDJ Season',
                    data: ondjData,
                    borderColor: 'rgba(255, 159, 64, 1)',
                    backgroundColor: 'rgba(255, 159, 64, 0.1)',
                    borderWidth: 2,
                    tension: 0.1
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Rainfall (mm)'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Year'
                    }
                }
            },
            plugins: {
                title: {
                    display: true,
                    text: 'Rainfall Time Series (2005-2014)',
                    font: {
                        size: 16
                    }
                }
            }
        }
    });
}

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