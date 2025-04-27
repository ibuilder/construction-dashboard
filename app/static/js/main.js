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


// main.js - Common JavaScript for Construction Management Dashboard

$(document).ready(function() {
    // Sidebar toggle
    $('#sidebarCollapse').on('click', function() {
        $('#sidebar').toggleClass('active');
    });

    // Close sidebar on mobile when clicking outside
    $(document).click(function(e) {
        const sidebar = $('#sidebar');
        const sidebarToggle = $('#sidebarCollapse');
        
        if (!sidebar.is(e.target) && 
            sidebar.has(e.target).length === 0 && 
            !sidebarToggle.is(e.target) && 
            sidebarToggle.has(e.target).length === 0 && 
            sidebar.hasClass('active') &&
            $(window).width() <= 768) {
            
            sidebar.removeClass('active');
        }
    });

    // Initialize popovers
    $('[data-toggle="popover"]').popover();
    
    // Initialize tooltips
    $('[data-toggle="tooltip"]').tooltip();
    
    // Confirm delete actions
    $('.confirm-delete').on('click', function(e) {
        if (!confirm('Are you sure you want to delete this item? This action cannot be undone.')) {
            e.preventDefault();
        }
    });
    
    // Date picker initialization
    if ($.fn.datepicker) {
        $('.datepicker').datepicker({
            format: 'yyyy-mm-dd',
            autoclose: true,
            todayHighlight: true
        });
    }
    
    // Data tables initialization
    if ($.fn.DataTable) {
        $('.datatable').DataTable({
            responsive: true,
            pageLength: 25,
            language: {
                search: "_INPUT_",
                searchPlaceholder: "Search...",
            }
        });
    }
    
    // Form validation
    if ($.fn.validate) {
        $("form.needs-validation").validate({
            errorElement: 'div',
            errorClass: 'invalid-feedback',
            highlight: function(element) {
                $(element).addClass('is-invalid');
            },
            unhighlight: function(element) {
                $(element).removeClass('is-invalid');
            },
            errorPlacement: function(error, element) {
                error.insertAfter(element);
            }
        });
    }
    
    // Activate current sidebar item based on URL
    const currentPath = window.location.pathname;
    const sidebarLinks = $('#sidebar a');
    
    sidebarLinks.each(function() {
        const linkPath = $(this).attr('href');
        if (linkPath && currentPath.indexOf(linkPath) === 0) {
            $(this).closest('li').addClass('active');
            $(this).closest('ul.collapse').addClass('show');
        }
    });
    
    // Add animation to cards and other elements
    $('.animate-on-scroll').each(function() {
        const el = $(this);
        
        $(window).scroll(function() {
            if (isElementInViewport(el)) {
                el.addClass('animated fadeIn');
            }
        });
        
        // Check if element is already in viewport on page load
        if (isElementInViewport(el)) {
            el.addClass('animated fadeIn');
        }
    });
    
    // Helper function to check if element is in viewport
    function isElementInViewport(el) {
        const rect = el[0].getBoundingClientRect();
        return (
            rect.top >= 0 &&
            rect.left >= 0 &&
            rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
            rect.right <= (window.innerWidth || document.documentElement.clientWidth)
        );
    }
});
