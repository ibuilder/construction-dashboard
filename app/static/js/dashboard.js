// This file contains JavaScript code for dashboard interactivity and AJAX calls.

document.addEventListener('DOMContentLoaded', function() {
    // Function to fetch project data
    function fetchProjects() {
        fetch('/api/projects')
            .then(response => response.json())
            .then(data => {
                const projectList = document.getElementById('project-list');
                projectList.innerHTML = '';
                data.forEach(project => {
                    const listItem = document.createElement('li');
                    listItem.textContent = project.name;
                    projectList.appendChild(listItem);
                });
            })
            .catch(error => console.error('Error fetching projects:', error));
    }

    // Function to create a new project
    document.getElementById('create-project-form').addEventListener('submit', function(event) {
        event.preventDefault();
        const formData = new FormData(this);
        fetch('/api/projects', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            console.log('Project created:', data);
            fetchProjects(); // Refresh project list
        })
        .catch(error => console.error('Error creating project:', error));
    });

    // Function to delete a project
    function deleteProject(projectId) {
        fetch(`/api/projects/${projectId}`, {
            method: 'DELETE'
        })
        .then(response => {
            if (response.ok) {
                console.log('Project deleted');
                fetchProjects(); // Refresh project list
            }
        })
        .catch(error => console.error('Error deleting project:', error));
    }

    // Initial fetch of projects
    fetchProjects();
});