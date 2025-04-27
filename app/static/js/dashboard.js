document.addEventListener('DOMContentLoaded', function() {
    // Function to fetch project data
    const projectList = document.getElementById('project-list');
    if (projectList) {
        function fetchProjects() {
            fetch('/api/projects')
                .then(response => response.json())
                .then(data => {
                    projectList.innerHTML = '';
                    data.forEach(project => {
                        const listItem = document.createElement('li');
                        listItem.textContent = project.name;
                        projectList.appendChild(listItem);
                    });
                })
                .catch(error => console.error('Error fetching projects:', error));
        }
        fetchProjects();
    }

    const createProjectForm = document.getElementById('create-project-form');
    // Function to create a new project
    if (createProjectForm) {
        createProjectForm.addEventListener('submit', function(event) {
            event.preventDefault();
            const formData = new FormData(this);
            fetch('/api/projects', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                console.log('Project created:', data);
                // Redirect to the project page or refresh the list
                window.location.href = `/projects/${data.id}`;
            })
            .catch(error => console.error('Error creating project:', error));
        });
    }

    // Only set up delete functions if we're on a page with delete buttons
    const deleteButtons = document.querySelectorAll('.delete-project-btn');
    if (deleteButtons.length > 0) {
        deleteButtons.forEach(button => {
            button.addEventListener('click', function() {
                const projectId = this.getAttribute('data-project-id');
                if (confirm('Are you sure you want to delete this project?')) {
                    deleteProject(projectId);
                }
            });
        });
    }

    function deleteProject(projectId) {
        fetch(`/api/projects/${projectId}`, {
            method: 'DELETE'
        })
        .then(response => {
            if (response.ok) {
                console.log('Project deleted');
                // Either redirect or refresh
                window.location.reload();
            }
        })
        .catch(error => console.error('Error deleting project:', error));
    }
});