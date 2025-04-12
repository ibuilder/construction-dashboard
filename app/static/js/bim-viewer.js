/**
 * BIM Viewer using IFC.js
 * This script provides functionality for viewing IFC models in the web browser
 */

// Global variables for IFC viewer
let viewer;
let model;
let allIDs = [];
let wireframeMode = false;
let shadowsOn = true;
let issueMarkers = [];

/**
 * Initialize the BIM viewer
 * @param {string} containerId - ID of the container element
 * @param {string} modelUrl - URL to the IFC model file
 */
async function initBimViewer(containerId, modelUrl) {
    try {
        // Show loading indicator
        document.getElementById('loading-indicator').style.display = 'flex';
        document.getElementById('error-message').style.display = 'none';
        
        // Create the viewer
        const container = document.getElementById(containerId);
        viewer = new WebIFCViewer.IfcViewerAPI({
            container,
            backgroundColor: new THREE.Color(0xf5f5f5),
        });
        
        // Set up scene
        viewer.IFC.setWasmPath('../../static/js/');
        viewer.IFC.applyWebIfcConfig({
            COORDINATE_TO_ORIGIN: true,
            USE_FAST_BOOLS: true
        });
        
        // Create grid and axes
        viewer.grid.setGrid();
        viewer.axes.setAxes();
        
        // Load the model
        model = await viewer.IFC.loadIfcUrl(modelUrl);

        // Get all IDs for later use
        allIDs = await loadAllElementIds(model.modelID);
        
        // Set up selection
        setupSelection();
        
        // Hide loading indicator
        document.getElementById('loading-indicator').style.display = 'none';
        
        // Return the loaded model for further processing
        return { viewer, model };
    } catch (error) {
        console.error('Error loading IFC model:', error);
        document.getElementById('loading-indicator').style.display = 'none';
        document.getElementById('error-message').style.display = 'flex';
        throw error;
    }
}

/**
 * Load all element IDs of specific types
 * @param {number} modelID - The model ID
 */
async function loadAllElementIds(modelID) {
    try {
        const allItems = [];
        const ifcTypes = [
            'IFCWALL',
            'IFCSLAB',
            'IFCDOOR',
            'IFCWINDOW',
            'IFCBEAM',
            'IFCCOLUMN',
            'IFCMEMBER',
            'IFCFURNISHINGELEMENT',
            'IFCBUILDINGSTOREY',
            'IFCROOF',
            'IFCSTAIR',
        ];
        
        for (const type of ifcTypes) {
            const ids = await viewer.IFC.getAllItemsOfType(modelID, type, false);
            allItems.push(...ids);
        }
        
        return allItems;
    } catch (error) {
        console.error('Error loading element IDs:', error);
        return [];
    }
}

/**
 * Set up mouse selection for IFC elements
 */
function setupSelection() {
    // Set up click selection
    viewer.IFC.selector.setupEvents();
    
    // Get HTML elements for display
    const elementInfoPanel = document.getElementById('element-info-panel');
    const elementProperties = document.getElementById('element-properties');
    
    // Add selection handler
    window.addEventListener('mouseup', async () => {
        const selection = viewer.IFC.selector.selection.get();
        if (selection.size === 0) return;
        
        // Get the first selected model and element
        const selectionArray = Array.from(selection.values());
        const selectedModelID = selectionArray[0].modelID;
        const selectedElementID = selectionArray[0].id;
        
        // Get properties
        const properties = await viewer.IFC.getProperties(
            selectedModelID,
            selectedElementID,
            true,
            false
        );
        
        // Display properties
        displayElementProperties(properties);
    });
}

/**
 * Display element properties in the info panel
 * @param {Object} properties - Element properties
 */
function displayElementProperties(properties) {
    const elementInfoPanel = document.getElementById('element-info-panel');
    const elementProperties = document.getElementById('element-properties');
    
    // Format properties for display
    let html = '<table class="table table-striped">';
    
    // Basic properties
    if (properties.type) {
        html += `<tr><td><strong>Type</strong></td><td>${properties.type}</td></tr>`;
    }
    
    // IFC common properties
    if (properties.psets) {
        const psets = properties.psets;
        for (const pset of psets) {
            html += `<tr><td colspan="2" class="bg-light"><strong>${pset.name || 'Properties'}</strong></td></tr>`;
            
            if (pset.properties) {
                for (const prop of pset.properties) {
                    html += `<tr><td>${prop.name}</td><td>${formatPropertyValue(prop.value)}</td></tr>`;
                }
            }
        }
    }
    
    // Native properties
    if (properties.mats && properties.mats.length > 0) {
        html += `<tr><td colspan="2" class="bg-light"><strong>Materials</strong></td></tr>`;
        for (const mat of properties.mats) {
            html += `<tr><td>Material</td><td>${mat.name || 'Unnamed'}</td></tr>`;
        }
    }
    
    html += '</table>';
    
    // Update panel and display it
    elementProperties.innerHTML = html;
    elementInfoPanel.style.display = 'block';
}

/**
 * Format property value for display
 * @param {any} value - Property value
 */
function formatPropertyValue(value) {
    if (value === null || value === undefined) return 'N/A';
    if (typeof value === 'object') {
        if (value.value !== undefined) {
            return formatPropertyValue(value.value);
        }
        return JSON.stringify(value);
    }
    return value.toString();
}

/**
 * Toggle wireframe mode for all elements
 */
function toggleWireframe() {
    wireframeMode = !wireframeMode;
    
    const materials = viewer.IFC.context.items.ifcModels.map(model => model.material);
    
    for (const material of materials) {
        material.wireframe = wireframeMode;
    }
}

/**
 * Toggle shadows for all elements
 */
function toggleShadows() {
    shadowsOn = !shadowsOn;
    
    // Toggle renderer shadow map
    viewer.context.renderer.shadowMap.enabled = shadowsOn;
    
    // Toggle shadows on all objects
    const objects = viewer.context.getScene().children;
    for (const object of objects) {
        if (object.isLight) {
            object.castShadow = shadowsOn;
        } else if (object.isMesh) {
            object.castShadow = shadowsOn;
            object.receiveShadow = shadowsOn;
        }
    }
}

/**
 * Reset the camera view to show the entire model
 */
function resetView() {
    viewer.context.fitToFrame();
}

/**
 * Filter visible elements by category
 * @param {string} category - Element category to show
 */
async function filterByCategory(category) {
    try {
        // Clear any existing filters
        await viewer.IFC.selector.unpickIfcItems();
        
        // If category is 'all', show everything and return
        if (category === 'all') {
            allIDs.forEach(id => {
                viewer.IFC.selector.undoHideIfcItems(model.modelID, [id]);
            });
            return;
        }
        
        // Get IDs of elements matching the category
        const ids = await viewer.IFC.getAllItemsOfType(model.modelID, category.toUpperCase(), false);
        
        // Hide all elements
        allIDs.forEach(id => {
            viewer.IFC.selector.hideIfcItems(model.modelID, [id]);
        });
        
        // Show only elements of the selected category
        ids.forEach(id => {
            viewer.IFC.selector.undoHideIfcItems(model.modelID, [id]);
        });
    } catch (error) {
        console.error('Error filtering elements:', error);
    }
}

/**
 * Create an issue marker at the clicked position
 * @param {Object} position - 3D position {x, y, z}
 * @param {Object} issueData - Issue data
 */
function addIssueMarker(position, issueData) {
    // Create marker element
    const marker = document.createElement('div');
    marker.className = 'issue-marker';
    if (issueData.priority === 'high' || issueData.priority === 'critical') {
        marker.classList.add('high-priority');
    }
    marker.textContent = issueMarkers.length + 1;
    marker.dataset.issueId = issueData.id;
    
    // Add to document
    const container = viewer.context.getDomElement().parentElement;
    container.appendChild(marker);
    
    // Store marker data
    const markerData = {
        element: marker,
        position: new THREE.Vector3(position.x, position.y, position.z),
        issueData: issueData
    };
    issueMarkers.push(markerData);
    
    // Update marker position
    updateMarkerPosition(markerData);
    
    // Add event listener for tooltip
    marker.addEventListener('mouseenter', () => showIssueTooltip(markerData));
    marker.addEventListener('mouseleave', hideIssueTooltip);
    marker.addEventListener('click', () => openIssueDetails(issueData.id));
    
    return markerData;
}

/**
 * Update the 2D position of all issue markers
 */
function updateAllMarkers() {
    issueMarkers.forEach(marker => updateMarkerPosition(marker));
}

/**
 * Update the 2D position of a marker based on its 3D position
 * @param {Object} markerData - Marker data
 */
function updateMarkerPosition(markerData) {
    const position2D = worldToScreen(markerData.position);
    if (position2D) {
        markerData.element.style.display = 'flex';
        markerData.element.style.left = position2D.x + 'px';
        markerData.element.style.top = position2D.y + 'px';
    } else {
        // Hide marker if it's behind the camera
        markerData.element.style.display = 'none';
    }
}

/**
 * Convert a 3D world position to 2D screen position
 * @param {THREE.Vector3} position - 3D position
 * @returns {Object|null} - 2D position {x, y} or null if behind camera
 */
function worldToScreen(position) {
    const vector = position.clone();
    const canvas = viewer.context.getDomElement();
    
    // Convert world position to normalized device coordinates (NDC)
    vector.project(viewer.context.getCamera());
    
    // Check if the point is in front of the camera
    if (vector.z > 1) {
        return null;
    }
    
    // Convert NDC to screen coordinates
    const x = (vector.x + 1) / 2 * canvas.clientWidth;
    const y = (-vector.y + 1) / 2 * canvas.clientHeight;
    
    return { x, y };
}

/**
 * Show tooltip for an issue marker
 * @param {Object} markerData - Marker data
 */
function showIssueTooltip(markerData) {
    // Create tooltip element
    const tooltip = document.createElement('div');
    tooltip.className = 'tooltip-container';
    tooltip.id = 'issue-tooltip';
    
    // Create tooltip content
    const issue = markerData.issueData;
    tooltip.innerHTML = `
        <div class="tooltip-header">
            <strong>${issue.title}</strong>
            <span class="badge ${issue.priority === 'high' || issue.priority === 'critical' ? 'bg-danger' : 'bg-warning'} ms-2">${issue.priority}</span>
        </div>
        <div class="tooltip-body mt-2">
            ${issue.description || 'No description'}
        </div>
        <div class="tooltip-footer mt-2 text-muted">
            <small>Assigned to: ${issue.assignedTo || 'Unassigned'}</small>
        </div>
    `;
    
    // Position tooltip
    const markerRect = markerData.element.getBoundingClientRect();
    const containerRect = viewer.context.getDomElement().parentElement.getBoundingClientRect();
    tooltip.style.left = (markerRect.left - containerRect.left + markerRect.width / 2) + 'px';
    tooltip.style.top = (markerRect.top - containerRect.top) + 'px';
    
    // Add to document
    viewer.context.getDomElement().parentElement.appendChild(tooltip);
}

/**
 * Hide issue tooltip
 */
function hideIssueTooltip() {
    const tooltip = document.getElementById('issue-tooltip');
    if (tooltip) {
        tooltip.remove();
    }
}

/**
 * Open issue details page
 * @param {string} issueId - Issue ID
 */
function openIssueDetails(issueId) {
    // Navigate to issue details page
    window.location.href = `/projects/bim/issues/${issueId}?project_id=${projectId}&model_id=${modelId}`;
}

// Export functions for use in other modules
window.BimViewer = {
    init: initBimViewer,
    toggleWireframe,
    toggleShadows,
    resetView,
    filterByCategory,
    addIssueMarker,
    updateAllMarkers
};