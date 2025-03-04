// Initialize state for all subcategories
let subcategoryState = {};

// Function to toggle category (expand/collapse)
function toggleCategory(category) {
    // Get all subcategories elements
    const allSubcategories = document.querySelectorAll('.subcategories');
    
    // Hide all subcategories first
    allSubcategories.forEach(el => {
        el.style.display = 'none';
    });
    
    // Show the selected category's subcategories
    const targetSubcategories = document.getElementById(`${category}-subcategories`);
    if (targetSubcategories) {
        targetSubcategories.style.display = 'block';
    }
    
    // Highlight the active category button
    const allCategoryBtns = document.querySelectorAll('.category-btn');
    allCategoryBtns.forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Add active class to the clicked button
    document.querySelector(`.category-btn[onclick="toggleCategory('${category}')"]`).classList.add('active');
}

// Function to toggle a specific subcategory layer
function toggleSubcategoryLayer(checkbox) {
    const layerName = checkbox.dataset.layer;
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
}

// Function to sync checkboxes with Folium layer states
function syncLayerStates() {
    const layerControls = document.querySelectorAll('.leaflet-control-layers-overlays input');
    const subcategoryCheckboxes = document.querySelectorAll('.subcategory input[type="checkbox"]');
    
    // Create a mapping of layer names to their current state
    const layerStates = {};
    layerControls.forEach(input => {
        const label = input.nextElementSibling.textContent.trim();
        layerStates[label] = input.checked;
    });
    
    // Update subcategory checkboxes based on layer states
    subcategoryCheckboxes.forEach(checkbox => {
        const layerName = checkbox.dataset.layer;
        if (layerName in layerStates) {
            checkbox.checked = layerStates[layerName];
            subcategoryState[checkbox.id] = layerStates[layerName];
        }
    });
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    // Hide all subcategories initially
    const allSubcategories = document.querySelectorAll('.subcategories');
    allSubcategories.forEach(el => {
        el.style.display = 'none';
    });
    
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