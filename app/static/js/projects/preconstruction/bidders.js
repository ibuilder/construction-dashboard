document.addEventListener('DOMContentLoaded', function() {
    // Initialize DataTable with sorting and filtering
    const biddersTable = $('#bidders-table').DataTable({
        responsive: true,
        order: [[0, 'asc']],
        columns: [
            { orderable: true },
            { orderable: true },
            { orderable: true },
            { orderable: true },
            { orderable: true },
            { orderable: false }
        ],
        dom: 'Bfrtip',
        buttons: [
            'copy', 'csv', 'excel', 'pdf', 'print'
        ]
    });

    // Delete bidder functionality
    document.querySelectorAll('.delete-bidder').forEach(button => {
        button.addEventListener('click', function() {
            const bidderId = this.getAttribute('data-id');
            
            if (confirm('Are you sure you want to delete this bidder?')) {
                const form = document.createElement('form');
                form.method = 'POST';
                form.action = `/projects/preconstruction/bidders/${bidderId}/delete`;
                
                const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
                const csrfInput = document.createElement('input');
                csrfInput.type = 'hidden';
                csrfInput.name = 'csrf_token';
                csrfInput.value = csrfToken;
                
                form.appendChild(csrfInput);
                document.body.appendChild(form);
                form.submit();
            }
        });
    });

    // Add comment functionality
    document.getElementById('comment-form')?.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const formData = new FormData(this);
        const bidderId = this.getAttribute('data-bidder-id');
        
        fetch(`/api/comments/bidder/${bidderId}`, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRF-TOKEN': document.querySelector('meta[name="csrf-token"]').getAttribute('content')
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Add new comment to the UI without reloading
                const commentsContainer = document.getElementById('comments-container');
                const commentTemplate = document.getElementById('comment-template').innerHTML;
                const newComment = document.createElement('div');
                
                newComment.innerHTML = commentTemplate
                    .replace('{{author}}', data.comment.author)
                    .replace('{{date}}', data.comment.created_at)
                    .replace('{{content}}', data.comment.content);
                
                commentsContainer.appendChild(newComment);
                
                // Clear the comment form
                document.getElementById('comment-content').value = '';
            } else {
                alert('Error adding comment: ' + data.message);
            }
        })
        .catch(error => console.error('Error:', error));
    });
});