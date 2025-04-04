import CrudModule from '../components/crud.js';
import { supabase } from '../../../supabase/init.js';
import { currentUser } from '../auth.js';
import { formatDate } from '../app.js';

// RFI Module
class RfiModule extends CrudModule {
  constructor() {
    super({
      table: 'rfis',
      primaryKey: 'id',
      columns: [
        { data: 'id', title: 'RFI #' },
        { data: 'title', title: 'Title' },
        { 
          data: 'status', 
          title: 'Status',
          render: (data) => {
            const statusClasses = {
              'draft': 'badge bg-secondary',
              'submitted': 'badge bg-primary',
              'in_review': 'badge bg-warning text-dark',
              'answered': 'badge bg-success',
              'closed': 'badge bg-dark'
            };
            return `<span class="${statusClasses[data] || 'badge bg-secondary'}">${data.replace('_', ' ').toUpperCase()}</span>`;
          }
        },
        { 
          data: 'priority', 
          title: 'Priority',
          render: (data) => {
            const priorityClasses = {
              'low': 'badge bg-info',
              'medium': 'badge bg-warning text-dark',
              'high': 'badge bg-danger',
              'critical': 'badge bg-danger'
            };
            return `<span class="${priorityClasses[data] || 'badge bg-secondary'}">${data.toUpperCase()}</span>`;
          }
        },
        { 
          data: 'due_date', 
          title: 'Due Date',
          render: (data) => data ? formatDate(data) : 'N/A'
        },
        { 
          data: 'assigned_to', 
          title: 'Assigned To',
          render: (data, type, row) => {
            if (!data) return 'Unassigned';
            return row.assigned_to_name || 'Loading...';
          }
        },
        { 
          data: 'created_at', 
          title: 'Created',
          render: (data) => formatDate(data)
        }
      ],
      tableDomId: 'rfis-table',
      formDomId: 'rfi-form',
      detailsDomId: 'rfi-details',
      module: 'engineering',
      recordType: 'rfi',
      defaultSort: { column: 'id', direction: 'desc' },
      relations: [
        { table: 'users', fields: ['first_name', 'last_name'], as: 'created_by_user' },
        { table: 'users', fields: ['first_name', 'last_name'], as: 'assigned_to_user' },
        { table: 'users', fields: ['first_name', 'last_name'], as: 'answered_by_user' }
      ]
    });
    
    // Add custom methods
    this.initCustomEventListeners();
  }
  
  // Initialize any custom event listeners
  initCustomEventListeners() {
    // Status change handler
    document.addEventListener('change', (e) => {
      if (e.target.id === 'rfi-status' || e.target.id === 'edit-status') {
        this.handleStatusChange(e.target);
      }
    });
    
    // Answer form submission
    const answerForm = document.getElementById('answer-form');
    if (answerForm) {
      answerForm.addEventListener('submit', (e) => {
        e.preventDefault();
        this.submitAnswer();
      });
    }
  }
  
  // Handle status change to show/hide relevant form fields
  handleStatusChange(selectElement) {
    const status = selectElement.value;
    const answerSection = document.getElementById('answer-section');
    
    if (answerSection) {
      if (status === 'answered' || status === 'closed') {
        answerSection.style.display = 'block';
      } else {
        answerSection.style.display = 'none';
      }
    }
  }
  
  // Submit an answer to an RFI
  async submitAnswer() {
    const answerForm = document.getElementById('answer-form');
    if (!answerForm || !this.currentRecord) return;
    
    const answer = document.getElementById('rfi-answer').value;
    const status = document.getElementById('rfi-status').value;
    
    if (!answer) {
      this.showErrorMessage('Please provide an answer before submitting.');
      return;
    }
    
    try {
      const rfiId = this.currentRecord.id;
      
      // Update RFI with answer
      const { data, error } = await supabase
        .from('rfis')
        .update({
          answer,
          status,
          answered_date: new Date().toISOString().split('T')[0],
          answered_by: currentUser.id,
          updated_at: new Date().toISOString(),
          updated_by: currentUser.id
        })
        .eq('id', rfiId)
        .select();
      
      if (error) throw error;
      
      // Log activity
      await this.logActivity('update', rfiId);
      
      // Update current record and display
      this.currentRecord = data[0];
      this.displayRecordDetails(this.currentRecord);
      
      this.showSuccessMessage('RFI answer submitted successfully.');
      
      // Reset form
      answerForm.reset();
    } catch (error) {
      console.error('Error submitting answer:', error);
      this.showErrorMessage('Failed to submit answer. ' + error.message);
    }
  }
  
  // Override to customize how RFI details are displayed
  updateDetailsContent(container, record) {
    // Call parent method for common fields
    super.updateDetailsContent(container, record);
    
    // Update RFI-specific fields
    if (container) {
      // RFI Number
      const rfiNumber = container.querySelector('.rfi-number');
      if (rfiNumber) {
        rfiNumber.textContent = `RFI #${record.id}`;
      }
      
      // Title
      const titleElement = container.querySelector('.record-title');
      if (titleElement) {
        titleElement.textContent = record.title;
      }
      
      // Status
      const statusElement = container.querySelector('.record-status');
      if (statusElement) {
        const statusText = record.status.replace('_', ' ').toUpperCase();
        statusElement.textContent = statusText;
        
        // Update status class
        const statusClasses = {
          'draft': 'status-draft',
          'submitted': 'status-submitted',
          'in_review': 'status-in-review',
          'answered': 'status-answered',
          'closed': 'status-closed'
        };
        
        statusElement.className = `record-status ${statusClasses[record.status] || ''}`;
      }
      
      // Priority
      const priorityElement = container.querySelector('.rfi-priority');
      if (priorityElement) {
        priorityElement.textContent = record.priority.toUpperCase();
        
        const priorityClasses = {
          'low': 'priority-low',
          'medium': 'priority-medium',
          'high': 'priority-high',
          'critical': 'priority-critical'
        };
        
        priorityElement.className = `rfi-priority ${priorityClasses[record.priority] || ''}`;
      }
      
      // Question
      const questionElement = container.querySelector('.rfi-question');
      if (questionElement) {
        questionElement.innerHTML = record.question.replace(/\n/g, '<br>');
      }
      
      // Answer
      const answerElement = container.querySelector('.rfi-answer');
      const answerSection = container.querySelector('.answer-section');
      
      if (answerElement) {
        if (record.answer) {
          answerElement.innerHTML = record.answer.replace(/\n/g, '<br>');
          if (answerSection) {
            answerSection.style.display = 'block';
          }
        } else {
          answerElement.innerHTML = '<em>Not answered yet</em>';
          if (answerSection) {
            answerSection.style.display = 'none';
          }
        }
      }
      
      // Dates
      this.updateDateElement(container, '.submitted-date', record.submitted_date);
      this.updateDateElement(container, '.due-date', record.due_date);
      this.updateDateElement(container, '.answered-date', record.answered_date);
      
      // Users
      this.updateUserElement(container, '.submitted-by', record.submitted_by);
      this.updateUserElement(container, '.assigned-to', record.assigned_to);
      this.updateUserElement(container, '.answered-by', record.answered_by);
      
      // Show/hide answer form based on user role and RFI status
      this.updateAnswerForm(container, record);
    }
  }
  
  // Helper to update date elements
  updateDateElement(container, selector, date) {
    const element = container.querySelector(selector);
    if (element && date) {
      element.textContent = formatDate(date);
    } else if (element) {
      element.textContent = 'N/A';
    }
  }
  
  // Helper to update user elements
  async updateUserElement(container, selector, userId) {
    const element = container.querySelector(selector);
    if (element && userId) {
      const userName = await this.getUserName(userId);
      element.textContent = userName;
    } else if (element) {
      element.textContent = 'N/A';
    }
  }
  
  // Update answer form visibility
  updateAnswerForm(container, record) {
    const answerFormSection = container.querySelector('.answer-form-section');
    if (!answerFormSection) return;
    
    // Only show answer form if the RFI is not closed and either:
    // 1. Current user is the assigned person, or
    // 2. Current user has admin/owner role
    if (record.status !== 'closed' && 
        (record.assigned_to === currentUser.id || 
         currentUser.role === 'owner' || 
         currentUser.role === 'owner_rep')) {
      answerFormSection.style.display = 'block';
      
      // Update form fields
      const statusSelect = document.getElementById('rfi-status');
      if (statusSelect) {
        statusSelect.value = record.status;
      }
      
      const answerTextarea = document.getElementById('rfi-answer');
      if (answerTextarea) {
        answerTextarea.value = record.answer || '';
      }
    } else {
      answerFormSection.style.display = 'none';
    }
  }
  
  // Initialize related data for dropdowns
  async initRelatedData() {
    try {
      // Fetch users for assignee dropdown
      const { data: users, error } = await supabase
        .from('users')
        .select('id, first_name, last_name, role')
        .order('first_name');
      
      if (error) throw error;
      
      // Populate assignee dropdowns
      const assigneeDropdowns = document.querySelectorAll('.assignee-dropdown');
      
      assigneeDropdowns.forEach(dropdown => {
        // Clear existing options
        dropdown.innerHTML = '<option value="">Select Assignee</option>';
        
        // Add user options
        users.forEach(user => {
          const option = document.createElement('option');
          option.value = user.id;
          option.textContent = `${user.first_name} ${user.last_name} (${user.role.replace('_', ' ')})`;
          dropdown.appendChild(option);
        });
      });
    } catch (error) {
      console.error('Error initializing related data:', error);
    }
  }
  
  // Override to customize the form data before submission
  getFormData(form) {
    const formData = super.getFormData(form);
    
    // Set default values for new RFIs
    if (form.dataset.mode === 'create') {
      formData.status = formData.status || 'draft';
      formData.priority = formData.priority || 'medium';
      formData.submitted_by = currentUser.id;
    }
    
    return formData;
  }
}

// Submittal Module
class SubmittalModule extends CrudModule {
  constructor() {
    super({
      table: 'submittals',
      primaryKey: 'id',
      columns: [
        { data: 'id', title: 'Submittal #' },
        { data: 'title', title: 'Title' },
        { 
          data: 'status', 
          title: 'Status',
          render: (data) => {
            const statusClasses = {
              'draft': 'badge bg-secondary',
              'submitted': 'badge bg-primary',
              'in_review': 'badge bg-warning text-dark',
              'approved': 'badge bg-success',
              'approved_as_noted': 'badge bg-info',
              'revise_and_resubmit': 'badge bg-danger',
              'rejected': 'badge bg-danger',
              'closed': 'badge bg-dark'
            };
            return `<span class="${statusClasses[data] || 'badge bg-secondary'}">${data.replace(/_/g, ' ').toUpperCase()}</span>`;
          }
        },
        { 
          data: 'priority', 
          title: 'Priority',
          render: (data) => {
            const priorityClasses = {
              'low': 'badge bg-info',
              'medium': 'badge bg-warning text-dark',
              'high': 'badge bg-danger',
              'critical': 'badge bg-danger'
            };
            return `<span class="${priorityClasses[data] || 'badge bg-secondary'}">${data.toUpperCase()}</span>`;
          }
        },
        { data: 'spec_section', title: 'Spec Section' },
        { 
          data: 'due_date', 
          title: 'Due Date',
          render: (data) => data ? formatDate(data) : 'N/A'
        },
        { 
          data: 'revision_number', 
          title: 'Revision',
          render: (data) => data > 0 ? `Rev ${data}` : 'Original'
        },
        { 
          data: 'created_at', 
          title: 'Created',
          render: (data) => formatDate(data)
        }
      ],
      tableDomId: 'submittals-table',
      formDomId: 'submittal-form',
      detailsDomId: 'submittal-details',
      module: 'engineering',
      recordType: 'submittal',
      defaultSort: { column: 'id', direction: 'desc' },
      relations: [
        { table: 'users', fields: ['first_name', 'last_name'], as: 'created_by_user' },
        { table: 'users', fields: ['first_name', 'last_name'], as: 'submitted_by_user' },
        { table: 'users', fields: ['first_name', 'last_name'], as: 'reviewed_by_user' }
      ]
    });
    
    // Add custom methods and event listeners
    this.initCustomEventListeners();
  }
  
  // Initialize custom event listeners
  initCustomEventListeners() {
    // Status change handler
    document.addEventListener('change', (e) => {
      if (e.target.id === 'submittal-status' || e.target.id === 'edit-status') {
        this.handleStatusChange(e.target);
      }
    });
    
    // Review form submission
    const reviewForm = document.getElementById('review-form');
    if (reviewForm) {
      reviewForm.addEventListener('submit', (e) => {
        e.preventDefault();
        this.submitReview();
      });
    }
  }
  
  // Handle status change
  handleStatusChange(selectElement) {
    const status = selectElement.value;
    const reviewSection = document.getElementById('review-section');
    
    if (reviewSection) {
      if (status === 'approved' || status === 'approved_as_noted' || 
          status === 'revise_and_resubmit' || status === 'rejected') {
        reviewSection.style.display = 'block';
      } else {
        reviewSection.style.display = 'none';
      }
    }
  }
  
  // Submit a review
  async submitReview() {
    const reviewForm = document.getElementById('review-form');
    if (!reviewForm || !this.currentRecord) return;
    
    const comments = document.getElementById('review-comments').value;
    const status = document.getElementById('submittal-status').value;
    
    try {
      const submittalId = this.currentRecord.id;
      
      // Update submittal with review
      const { data, error } = await supabase
        .from('submittals')
        .update({
          status,
          review_comments: comments,
          reviewed_date: new Date().toISOString().split('T')[0],
          reviewed_by: currentUser.id,
          updated_at: new Date().toISOString(),
          updated_by: currentUser.id
        })
        .eq('id', submittalId)
        .select();
      
      if (error) throw error;
      
      // Log activity
      await this.logActivity('update', submittalId);
      
      // Update current record and display
      this.currentRecord = data[0];
      this.displayRecordDetails(this.currentRecord);
      
      this.showSuccessMessage('Submittal review submitted successfully.');
      
      // Reset form
      reviewForm.reset();
    } catch (error) {
      console.error('Error submitting review:', error);
      this.showErrorMessage('Failed to submit review. ' + error.message);
    }
  }
  
  // Override to customize how submittal details are displayed
  updateDetailsContent(container, record) {
    // Call parent method for common fields
    super.updateDetailsContent(container, record);
    
    // Update submittal-specific fields
    if (container) {
      // Submittal Number
      const submittalNumber = container.querySelector('.submittal-number');
      if (submittalNumber) {
        submittalNumber.textContent = `Submittal #${record.id}`;
      }
      
      // Title
      const titleElement = container.querySelector('.record-title');
      if (titleElement) {
        titleElement.textContent = record.title;
      }
      
      // Status
      const statusElement = container.querySelector('.record-status');
      if (statusElement) {
        const statusText = record.status.replace(/_/g, ' ').toUpperCase();
        statusElement.textContent = statusText;
        
        // Update status class
        const statusClasses = {
          'draft': 'status-draft',
          'submitted': 'status-submitted',
          'in_review': 'status-in-review',
          'approved': 'status-approved',
          'approved_as_noted': 'status-approved-as-noted',
          'revise_and_resubmit': 'status-revise-and-resubmit',
          'rejected': 'status-rejected',
          'closed': 'status-closed'
        };
        
        statusElement.className = `record-status ${statusClasses[record.status] || ''}`;
      }
      
      // Description
      const descriptionElement = container.querySelector('.submittal-description');
      if (descriptionElement && record.description) {
        descriptionElement.innerHTML = record.description.replace(/\n/g, '<br>');
      }
      
      // Spec section
      const specSectionElement = container.querySelector('.spec-section');
      if (specSectionElement) {
        specSectionElement.textContent = record.spec_section || 'N/A';
      }
      
      // Review comments
      const reviewCommentsElement = container.querySelector('.review-comments');
      const reviewSection = container.querySelector('.review-results-section');
      
      if (reviewCommentsElement) {
        if (record.review_comments) {
          reviewCommentsElement.innerHTML = record.review_comments.replace(/\n/g, '<br>');
          if (reviewSection) {
            reviewSection.style.display = 'block';
          }
        } else {
          reviewCommentsElement.innerHTML = '<em>No review comments yet</em>';
          if (reviewSection) {
            reviewSection.style.display = 'none';
          }
        }
      }
      
      // Revision number
      const revisionElement = container.querySelector('.revision-number');
      if (revisionElement) {
        revisionElement.textContent = record.revision_number > 0 ? `Revision ${record.revision_number}` : 'Original Submission';
      }
      
      // Dates
      this.updateDateElement(container, '.submitted-date', record.submitted_date);
      this.updateDateElement(container, '.due-date', record.due_date);
      this.updateDateElement(container, '.reviewed-date', record.reviewed_date);
      
      // Users
      this.updateUserElement(container, '.submitted-by', record.submitted_by);
      this.updateUserElement(container, '.reviewed-by', record.reviewed_by);
      
      // Show/hide review form based on user role and submittal status
      this.updateReviewForm(container, record);
    }
  }
  
  // Update review form visibility
  updateReviewForm(container, record) {
    const reviewFormSection = container.querySelector('.review-form-section');
    if (!reviewFormSection) return;
    
    // Only show review form if the submittal is not closed and either:
    // 1. Current user is reviewer (design team), or
    // 2. Current user has admin/owner role
    if (record.status !== 'closed' && 
        (currentUser.role === 'design_team' || 
         currentUser.role === 'owner' || 
         currentUser.role === 'owner_rep')) {
      reviewFormSection.style.display = 'block';
      
      // Update form fields
      const statusSelect = document.getElementById('submittal-status');
      if (statusSelect) {
        statusSelect.value = record.status;
      }
      
      const commentsTextarea = document.getElementById('review-comments');
      if (commentsTextarea) {
        commentsTextarea.value = record.review_comments || '';
      }
    } else {
      reviewFormSection.style.display = 'none';
    }
  }
  
  // Initialize related data for dropdowns
  async initRelatedData() {
    try {
      // Get CSI divisions for spec section dropdown
      const { data: divisions, error } = await supabase
        .from('csi_divisions')
        .select('division_number, division_name')
        .order('division_number');
      
      if (error) throw error;
      
      // Populate spec section dropdowns
      const specSectionDropdowns = document.querySelectorAll('.spec-section-dropdown');
      
      specSectionDropdowns.forEach(dropdown => {
        // Clear existing options
        dropdown.innerHTML = '<option value="">Select Spec Section</option>';
        
        // Add division options
        divisions.forEach(division => {
          const option = document.createElement('option');
          option.value = division.division_number;
          option.textContent = `${division.division_number} - ${division.division_name}`;
          dropdown.appendChild(option);
        });
      });
    } catch (error) {
      console.error('Error initializing related data:', error);
    }
  }
  
  // Override to customize the form data before submission
  getFormData(form) {
    const formData = super.getFormData(form);
    
    // Set default values for new submittals
    if (form.dataset.mode === 'create') {
      formData.status = formData.status || 'draft';
      formData.priority = formData.priority || 'medium';
      formData.revision_number = formData.revision_number || 0;
      formData.submitted_by = currentUser.id;
    }
    
    return formData;
  }
}

// Initialize modules
const initEngineeringModules = () => {
  // Determine which module to initialize based on current page
  const currentPath = window.location.pathname;
  
  if (currentPath.includes('/engineering/rfis.html')) {
    return new RfiModule();
  } else if (currentPath.includes('/engineering/submittals.html')) {
    return new SubmittalModule();
  }
  // Add more module initializations as needed
};

export default initEngineeringModules;