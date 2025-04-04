import { supabase } from '../../../supabase/init.js';
import { currentUser } from '../auth.js';
import { getProjectId } from '../app.js';

// Initialize comments for a record
async function initComments(options) {
  const container = document.getElementById(options.container);
  if (!container) return;
  
  // Store options in container data attributes
  container.dataset.recordId = options.recordId;
  container.dataset.recordType = options.recordType;
  container.dataset.module = options.module;
  
  // Initialize components
  await loadComments(container);
  setupCommentForm(container);
}

// Load comments for a record
async function loadComments(container) {
  try {
    const recordId = container.dataset.recordId;
    const recordType = container.dataset.recordType;
    
    container.querySelector('.comments-list').innerHTML = '<div class="loading-comments">Loading comments...</div>';
    
    // Fetch comments
    const { data: comments, error } = await supabase
      .from('comments')
      .select(`
        id,
        content,
        created_at,
        user_id,
        users(first_name, last_name, profile_image_url)
      `)
      .eq('record_id', recordId)
      .eq('record_type', recordType)
      .order('created_at', { ascending: false });
    
    if (error) throw error;
    
    // Update container
    updateCommentsDisplay(container, comments);
    
    return comments;
  } catch (error) {
    console.error('Error loading comments:', error);
    showCommentError(container, error.message);
    return [];
  }
}

// Update comments display
function updateCommentsDisplay(container, comments) {
  const commentsList = container.querySelector('.comments-list');
  
  // Clear list
  commentsList.innerHTML = '';
  
  if (!comments || comments.length === 0) {
    commentsList.innerHTML = '<div class="no-comments">No comments yet</div>';
    return;
  }
  
  // Add each comment
  comments.forEach(comment => {
    const commentItem = document.createElement('div');
    commentItem.className = 'comment-item';
    commentItem.dataset.id = comment.id;
    
    // Format date
    const commentDate = new Date(comment.created_at);
    const formattedDate = commentDate.toLocaleString();
    
    // Check if comment is from current user
    const isCurrentUserComment = comment.user_id === currentUser.id;
    
    // Create avatar element
    const avatarElement = document.createElement('div');
    avatarElement.className = 'comment-avatar';
    
    if (comment.users.profile_image_url) {
      avatarElement.innerHTML = `<img src="${comment.users.profile_image_url}" alt="User Avatar">`;
    } else {
      // Generate initials
      const initials = `${comment.users.first_name.charAt(0)}${comment.users.last_name.charAt(0)}`;
      avatarElement.innerHTML = `<div class="avatar-initials">${initials}</div>`;
    }
    
    // Create content element
    const contentElement = document.createElement('div');
    contentElement.className = 'comment-content';
    
    contentElement.innerHTML = `
      <div class="comment-header">
        <span class="comment-author">${comment.users.first_name} ${comment.users.last_name}</span>
        <span class="comment-date">${formattedDate}</span>
      </div>
      <div class="comment-text">${formatCommentText(comment.content)}</div>
    `;
    
    // Create actions element (for current user's comments)
    if (isCurrentUserComment) {
      const actionsElement = document.createElement('div');
      actionsElement.className = 'comment-actions';
      
      actionsElement.innerHTML = `
        <button type="button" class="btn btn-link btn-sm edit-comment">Edit</button>
        <button type="button" class="btn btn-link btn-sm delete-comment">Delete</button>
      `;
      
      contentElement.appendChild(actionsElement);
      
      // Add edit/delete handlers
      setupCommentActions(commentItem, comment);
    }
    
    // Assemble comment item
    commentItem.appendChild(avatarElement);
    commentItem.appendChild(contentElement);
    
    // Add to list
    commentsList.appendChild(commentItem);
  });
}

// Setup comment form
function setupCommentForm(container) {
  const commentForm = container.querySelector('.comment-form');
  if (!commentForm) return;
  
  // Form submission
  commentForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const commentInput = commentForm.querySelector('.comment-input');
    const content = commentInput.value.trim();
    
    if (!content) {
      showCommentError(container, 'Comment cannot be empty');
      return;
    }
    
    // Disable form during submission
    const submitButton = commentForm.querySelector('button[type="submit"]');
    commentInput.disabled = true;
    submitButton.disabled = true;
    
    try {
      await addComment(container, content);
      
      // Clear input
      commentInput.value = '';
      
      // Hide any errors
      hideCommentError(container);
    } catch (error) {
      console.error('Error adding comment:', error);
      showCommentError(container, 'Failed to add comment');
    } finally {
      // Re-enable form
      commentInput.disabled = false;
      submitButton.disabled = false;
    }
  });
}

// Add a new comment
async function addComment(container, content) {
  const recordId = container.dataset.recordId;
  const recordType = container.dataset.recordType;
  const module = container.dataset.module;
  
  // Insert comment
  const { error } = await supabase
    .from('comments')
    .insert({
      content,
      record_id: recordId,
      record_type: recordType,
      module,
      user_id: currentUser.id,
      created_at: new Date().toISOString(),
      project_id: getProjectId()
    });
  
  if (error) throw error;
  
  // Log activity
  await logCommentActivity('comment', recordId, recordType, module);
  
  // Reload comments
  await loadComments(container);
  
  return true;
}

// Update a comment
async function updateComment(container, commentId, content) {
  // Update comment
  const { error } = await supabase
    .from('comments')
    .update({
      content,
      updated_at: new Date().toISOString()
    })
    .eq('id', commentId);
  
  if (error) throw error;
  
  // Reload comments
  await loadComments(container);
  
  return true;
}

// Delete a comment
async function deleteComment(container, commentId) {
  // Delete comment
  const { error } = await supabase
    .from('comments')
    .delete()
    .eq('id', commentId);
  
  if (error) throw error;
  
  // Reload comments
  await loadComments(container);
  
  return true;
}

// Setup edit/delete actions for a comment
function setupCommentActions(commentItem, comment) {
  const container = commentItem.closest('.comments-container');
  
  // Edit button
  const editButton = commentItem.querySelector('.edit-comment');
  if (editButton) {
    editButton.addEventListener('click', () => {
      // Switch to edit mode
      const commentTextElement = commentItem.querySelector('.comment-text');
      const currentText = commentTextElement.textContent;
      
      commentTextElement.innerHTML = `
        <div class="edit-comment-form">
          <textarea class="form-control edit-comment-input">${currentText}</textarea>
          <div class="edit-actions mt-2">
            <button type="button" class="btn btn-primary btn-sm save-edit">Save</button>
            <button type="button" class="btn btn-secondary btn-sm cancel-edit">Cancel</button>
          </div>
        </div>
      `;
      
      // Setup save/cancel buttons
      const saveButton = commentTextElement.querySelector('.save-edit');
      const cancelButton = commentTextElement.querySelector('.cancel-edit');
      
      saveButton.addEventListener('click', async () => {
        const editInput = commentTextElement.querySelector('.edit-comment-input');
        const newContent = editInput.value.trim();
        
        if (!newContent) {
          alert('Comment cannot be empty');
          return;
        }
        
        try {
          await updateComment(container, comment.id, newContent);
        } catch (error) {
          console.error('Error updating comment:', error);
          showCommentError(container, 'Failed to update comment');
        }
      });
      
      cancelButton.addEventListener('click', () => {
        // Restore original content
        commentTextElement.innerHTML = formatCommentText(currentText);
      });
    });
  }
  
  // Delete button
  const deleteButton = commentItem.querySelector('.delete-comment');
  if (deleteButton) {
    deleteButton.addEventListener('click', async () => {
      if (confirm('Are you sure you want to delete this comment?')) {
        try {
          await deleteComment(container, comment.id);
        } catch (error) {
          console.error('Error deleting comment:', error);
          showCommentError(container, 'Failed to delete comment');
        }
      }
    });
  }
}

// Log comment activity
async function logCommentActivity(action, recordId, recordType, module) {
  try {
    await supabase
      .from('activity_log')
      .insert({
        action,
        module,
        record_type: recordType,
        record_id: recordId,
        user_id: currentUser.id,
        created_at: new Date().toISOString(),
        project_id: getProjectId()
      });
  } catch (error) {
    console.error('Error logging comment activity:', error);
  }
}

// Format comment text (handle line breaks, links, etc.)
function formatCommentText(text) {
  // Convert line breaks to <br>
  text = text.replace(/\n/g, '<br>');
  
  // Linkify URLs
  text = text.replace(
    /(https?:\/\/[^\s]+)/g, 
    '<a href="$1" target="_blank" rel="noopener noreferrer">$1</a>'
  );
  
  // Highlight @mentions
  text = text.replace(
    /@([a-zA-Z0-9_]+)/g,
    '<span class="mention">@$1</span>'
  );
  
  return text;
}

// Show comment error
function showCommentError(container, message) {
  const errorElement = container.querySelector('.comment-error');
  if (errorElement) {
    errorElement.textContent = message;
    errorElement.style.display = 'block';
  }
}

// Hide comment error
function hideCommentError(container) {
  const errorElement = container.querySelector('.comment-error');
  if (errorElement) {
    errorElement.style.display = 'none';
  }
}

// Export functions
export {
  initComments
};