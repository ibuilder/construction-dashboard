document.addEventListener('DOMContentLoaded', function () {
    // Sidebar toggle
    document.getElementById('sidebarCollapse')?.addEventListener('click', function () {
        document.getElementById('sidebar').classList.toggle('active');
        document.getElementById('content').classList.toggle('active');
    });

    // Initialize all DataTables
    const tables = document.querySelectorAll('.datatable');
    if (tables.length) {
        tables.forEach(function(table) {
            new DataTable(table, {
                responsive: true,
                language: {
                    search: "Filter records:",
                },
                dom: 'Bfrtip',
                buttons: [
                    'copy', 'csv', 'excel', 'pdf', 'print'
                ]
            });
        });
    }

    // Confirm deletes
    document.querySelectorAll('.btn-delete').forEach(function(btn) {
        btn.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to delete this item? This cannot be undone.')) {
                e.preventDefault();
            }
        });
    });

    // CSRF Token for AJAX requests
    const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');
    
    if (csrfToken) {
        // Set up CSRF token for AJAX requests
        $.ajaxSetup({
            beforeSend: function(xhr, settings) {
                if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader("X-CSRFToken", csrfToken);
                }
            }
        });
    }

    // Initialize popovers
    const popoverTriggerList = document.querySelectorAll('[data-bs-toggle="popover"]');
    [...popoverTriggerList].map(popoverTriggerEl => new bootstrap.Popover(popoverTriggerEl));
    
    // Initialize tooltips
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
    
    // Form validation styling
    const forms = document.querySelectorAll('.needs-validation');
    if (forms.length) {
        Array.from(forms).forEach(form => {
            form.addEventListener('submit', event => {
                if (!form.checkValidity()) {
                    event.preventDefault();
                    event.stopPropagation();
                }
                form.classList.add('was-validated');
            }, false);
        });
    }
});