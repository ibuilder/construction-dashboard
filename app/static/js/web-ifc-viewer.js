// filepath: c:\Users\iphoe\OneDrive\Documents\Server\cm-dashboard-flask\construction-dashboard\app\static\js\web-ifc-viewer.js

// Web IFC Viewer Library
// This script provides functionality to load and display IFC models in the browser.

const IFCLoader = new IFCLoader();
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

function loadIFCModel(url) {
    IFCLoader.load(url, (ifcModel) => {
        scene.add(ifcModel);
        render();
    }, undefined, (error) => {
        console.error('An error happened while loading the IFC model:', error);
    });
}

function render() {
    requestAnimationFrame(render);
    renderer.render(scene, camera);
}

// Adjust camera position
camera.position.set(0, 0, 10);

// Handle window resize
window.addEventListener('resize', () => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
});

// Export the loadIFCModel function for external use
export { loadIFCModel };