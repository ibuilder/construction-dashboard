let projectId;
      
      if (mode === 'edit') {
        const id = form.dataset.id;
        const { data, error } = await this.updateRecord(id, formData);
        
        if (error) throw error;
        projectId = id;
      } else {
        const { data, error } = await this.createRecord(formData);
        
        if (error) throw error;
        projectId = data.id;
      }
      
      // Process project users if in the form
      const projectUserRows = Array.from(form.querySelectorAll('.project-user-row'));
      if (projectUserRows.length > 0) {
        await this.processProjectUsers(projectId, projectUserRows);
      }
      
      // Show success message
      this.showSuccessMessage(`Project ${mode === 'edit' ? 'updated' : 'created'} successfully.`);
      
      // Close form and reload data
      this.closeForm();
      await this.loadData();
      
      appState.isLoading = false;
      this.showLoading(false);
    } catch (error) {
      console.error('Error submitting form:', error);
      this.showErrorMessage(`Failed to ${form.dataset.mode === 'edit' ? 'update' : 'create'} project. ${error.message}`);
      appState.isLoading = false;
      this.showLoading(false);
    }
  }
  
  // Process project users from form
  async processProjectUsers(projectId, userRows) {
    try {
      // Extract user data from rows
      const projectUsers = userRows.map(row => {
        const userSelect = row.querySelector('select[name*="user_id"]');
        const roleSelect = row.querySelector('select[name*="role"]');
        
        if (!userSelect || !roleSelect || !userSelect.value || !roleSelect.value) {
          return null;
        }
        
        return {
          project_id: projectId,
          user_id: userSelect.value,
          role: roleSelect.value,
          created_at: new Date().toISOString()
        };
      }).filter(Boolean);
      
      if (projectUsers.length === 0) return;
      
      // Insert project users
      const { error } = await supabase
        .from('project_users')
        .insert(projectUsers);
      
      if (error) throw error;
    } catch (error) {
      console.error('Error processing project users:', error);
      throw error;
    }
  }
  
  // Override to load project users when editing
  async openForm(data = null) {
    // Call parent method to open form
    super.openForm(data);
    
    // Clear existing project users
    const usersContainer = document.getElementById('project-users-container');
    if (usersContainer) {
      usersContainer.innerHTML = '';
    }
    
    // If editing an existing project, load project users
    if (data && data.id) {
      // Load existing project users for editing
      const { data: projectUsers, error } = await supabase
        .from('project_users')
        .select(`
          id,
          user_id,
          role,
          users(first_name, last_name, email)
        `)
        .eq('project_id', data.id);
      
      if (!error && projectUsers && projectUsers.length > 0) {
        // Add user rows for each project user
        projectUsers.forEach(() => {
          this.addProjectUserRow();
        });
        
        // Fill in user data
        const userRows = document.querySelectorAll('.project-user-row');
        projectUsers.forEach((pu, index) => {
          if (index < userRows.length) {
            const row = userRows[index];
            const userSelect = row.querySelector('select[name*="user_id"]');
            const roleSelect = row.querySelector('select[name*="role"]');
            
            if (userSelect) userSelect.value = pu.user_id;
            if (roleSelect) roleSelect.value = pu.role;
          }
        });
      }
    }
    
    // Populate user dropdowns
    await this.populateUserDropdowns();
  }
  
  // Initialize related data for dropdowns
  async initRelatedData() {
    try {
      // Fetch companies for dropdown
      const { data: companies, error: companiesError } = await supabase
        .from('companies')
        .select('id, name, type')
        .order('name');
      
      if (companiesError) throw companiesError;
      
      // Populate owner company dropdown
      const ownerCompanySelect = document.getElementById('owner_company_id');
      if (ownerCompanySelect) {
        // Clear existing options except the first one
        while (ownerCompanySelect.options.length > 1) {
          ownerCompanySelect.remove(1);
        }
        
        // Add company options (filter for owner type)
        companies
          .filter(company => company.type === 'owner')
          .forEach(company => {
            const option = document.createElement('option');
            option.value = company.id;
            option.textContent = company.name;
            ownerCompanySelect.appendChild(option);
          });
      }
      
      // Populate GC company dropdown
      const gcCompanySelect = document.getElementById('gc_company_id');
      if (gcCompanySelect) {
        // Clear existing options except the first one
        while (gcCompanySelect.options.length > 1) {
          gcCompanySelect.remove(1);
        }
        import CrudModule from '../components/crud.js';
import { supabase } from '../../../supabase/init.js';
import { currentUser } from '../auth.js';
import { formatDate } from '../app.js';

// Project Info Module
class ProjectInfoModule extends CrudModule {
  constructor() {
    super({
      table: 'projects',
      primaryKey: 'id',
      columns: [
        { data: 'name', title: 'Project Name' },
        { data: 'address', title: 'Address' },
        { 
          data: 'start_date', 
          title: 'Start Date',
          render: (data) => formatDate(data)
        },
        { 
          data: 'end_date', 
          title: 'End Date',
          render: (data) => formatDate(data)
        },
        { data: 'status', title: 'Status' },
        { 
          data: 'owner_company_id', 
          title: 'Owner',
          render: (data, type, row) => {
            return row.owner_company_name || 'Loading...';
          }
        },
        { 
          data: 'created_at', 
          title: 'Created',
          render: (data) => formatDate(data)
        }
      ],
      tableDomId: 'projects-table',
      formDomId: 'project-form',
      detailsDomId: 'project-details',
      module: 'settings',
      recordType: 'project',
      defaultSort: { column: 'name', direction: 'asc' },
      relations: [
        { table: 'companies', fields: ['name'], as: 'owner_company' },
        { table: 'companies', fields: ['name'], as: 'gc_company' },
        { table: 'users', fields: ['first_name', 'last_name'], as: 'primary_contact' }
      ],
      projectRelated: false // Projects table is not project-specific
    });
    
    // Add custom methods and event listeners
    this.initCustomEventListeners();
  }
  
  // Initialize custom event listeners
  initCustomEventListeners() {
    // Project selection
    const projectSelector = document.getElementById('project-selector');
    if (projectSelector) {
      this.initProjectSelector(projectSelector);
    }
    
    // Add project users button
    document.addEventListener('click', (e) => {
      if (e.target.classList.contains('add-project-user-btn') || e.target.closest('.add-project-user-btn')) {
        e.preventDefault();
        this.addProjectUserRow();
      }
      
      // Remove project user button
      if (e.target.classList.contains('remove-project-user-btn') || e.target.closest('.remove-project-user-btn')) {
        e.preventDefault();
        const row = e.target.closest('.project-user-row');
        if (row) row.remove();
      }
    });
  }
  
  // Initialize project selector dropdown
  async initProjectSelector(selector) {
    try {
      // Get all projects
      const { data: projects, error } = await supabase
        .from('projects')
        .select('id, name')
        .order('name');
      
      if (error) throw error;
      
      // Clear existing options
      selector.innerHTML = '';
      
      // Add projects to dropdown
      projects.forEach(project => {
        const option = document.createElement('option');
        option.value = project.id;
        option.textContent = project.name;
        selector.appendChild(option);
      });
      
      // Set current project as selected
      const currentProjectId = localStorage.getItem('currentProjectId');
      if (currentProjectId) {
        selector.value = currentProjectId;
      }
      
      // Add change event
      selector.addEventListener('change', () => {
        const projectId = selector.value;
        localStorage.setItem('currentProjectId', projectId);
        
        // Reload the page to update all project data
        window.location.reload();
      });
    } catch (error) {
      console.error('Error initializing project selector:', error);
    }
  }
  
  // Add a project user row
  addProjectUserRow() {
    const usersContainer = document.getElementById('project-users-container');
    if (!usersContainer) return;
    
    const rowIndex = document.querySelectorAll('.project-user-row').length;
    const newRow = document.createElement('div');
    newRow.className = 'project-user-row row g-3 mb-2 align-items-end border-bottom pb-2';
    newRow.innerHTML = `
      <div class="col-md-6">
        <label class="form-label">User</label>
        <select class="form-select user-dropdown" name="project_users[${rowIndex}][user_id]" required>
          <option value="">Select User</option>
          <!-- Options will be populated by JavaScript -->
        </select>
      </div>
      <div class="col-md-5">
        <label class="form-label">Role</label>
        <select class="form-select" name="project_users[${rowIndex}][role]" required>
          <option value="">Select Role</option>
          <option value="owner">Owner</option>
          <option value="owner_rep">Owner's Representative</option>
          <option value="general_contractor">General Contractor</option>
          <option value="subcontractor">Subcontractor</option>
          <option value="design_team">Design Team</option>
        </select>
      </div>
      <div class="col-md-1">
        <button type="button" class="btn btn-danger remove-project-user-btn">
          <i class="bi bi-trash"></i>
        </button>
      </div>
    `;
    
    usersContainer.appendChild(newRow);
    
    // Populate user dropdown
    this.populateUserDropdowns();
  }
  
  // Populate user dropdowns
  async populateUserDropdowns() {
    try {
      // Get all users if not already fetched
      if (!this.users) {
        const { data: users, error } = await supabase
          .from('users')
          .select('id, first_name, last_name, email, role, companies(name)')
          .order('first_name');
        
        if (error) throw error;
        
        this.users = users;
      }
      
      // Populate all user dropdowns
      const userDropdowns = document.querySelectorAll('.user-dropdown');
      
      userDropdowns.forEach(dropdown => {
        // Preserve selected value
        const selectedValue = dropdown.value;
        
        // Clear existing options except the first one
        while (dropdown.options.length > 1) {
          dropdown.remove(1);
        }
        
        // Add user options
        this.users.forEach(user => {
          const option = document.createElement('option');
          option.value = user.id;
          option.textContent = `${user.first_name} ${user.last_name} (${user.email})`;
          dropdown.appendChild(option);
        });
        
        // Restore selected value
        if (selectedValue) {
          dropdown.value = selectedValue;
        }
      });
    } catch (error) {
      console.error('Error populating user dropdowns:', error);
    }
  }
  
  // Override to customize how project details are displayed
  updateDetailsContent(container, record) {
    // Call parent method for common fields
    super.updateDetailsContent(container, record);
    
    // Update project-specific fields
    if (container) {
      // Project Name
      const projectNameElement = container.querySelector('.project-name');
      if (projectNameElement) {
        projectNameElement.textContent = record.name;
      }
      
      // Address
      const addressElement = container.querySelector('.project-address');
      if (addressElement) {
        let address = record.address || '';
        if (record.city) address += (address ? ', ' : '') + record.city;
        if (record.state) address += (address ? ', ' : '') + record.state;
        if (record.zip) address += (address ? ' ' : '') + record.zip;
        if (record.country && record.country !== 'USA') address += (address ? ', ' : '') + record.country;
        
        addressElement.textContent = address || 'No address specified';
      }
      
      // Date range
      const dateRangeElement = container.querySelector('.project-dates');
      if (dateRangeElement) {
        let dateRange = '';
        if (record.start_date) dateRange += formatDate(record.start_date);
        if (record.end_date) dateRange += ' to ' + formatDate(record.end_date);
        
        dateRangeElement.textContent = dateRange || 'No dates specified';
      }
      
      // Status
      const statusElement = container.querySelector('.project-status');
      if (statusElement) {
        statusElement.textContent = record.status || 'N/A';
        
        // Add color class based on status
        const statusClasses = {
          'active': 'text-success',
          'planning': 'text-primary',
          'completed': 'text-secondary',
          'on_hold': 'text-warning',
          'cancelled': 'text-danger'
        };
        
        for (const cls in statusClasses) {
          statusElement.classList.remove(statusClasses[cls]);
        }
        
        if (record.status && statusClasses[record.status]) {
          statusElement.classList.add(statusClasses[record.status]);
        }
      }
      
      // Description
      const descriptionElement = container.querySelector('.project-description');
      if (descriptionElement) {
        if (record.description) {
          descriptionElement.innerHTML = record.description.replace(/\n/g, '<br>');
        } else {
          descriptionElement.innerHTML = '<em>No description</em>';
        }
      }
      
      // Owner Company
      const ownerCompanyElement = container.querySelector('.owner-company');
      if (ownerCompanyElement) {
        if (record.owner_company_id) {
          ownerCompanyElement.textContent = record.owner_company_name || 'Loading...';
        } else {
          ownerCompanyElement.textContent = 'Not specified';
        }
      }
      
      // GC Company
      const gcCompanyElement = container.querySelector('.gc-company');
      if (gcCompanyElement) {
        if (record.gc_company_id) {
          gcCompanyElement.textContent = record.gc_company_name || 'Loading...';
        } else {
          gcCompanyElement.textContent = 'Not specified';
        }
      }
      
      // Primary Contact
      const primaryContactElement = container.querySelector('.primary-contact');
      if (primaryContactElement) {
        if (record.primary_contact_id) {
          primaryContactElement.textContent = `${record.primary_contact_first_name || ''} ${record.primary_contact_last_name || ''}`.trim() || 'Loading...';
        } else {
          primaryContactElement.textContent = 'Not specified';
        }
      }
      
      // Load project users
      this.loadProjectUsers(record.id);
    }
  }
  
  // Load project users for display
  async loadProjectUsers(projectId) {
    try {
      const usersContainer = document.getElementById('project-users-list');
      if (!usersContainer) return;
      
      usersContainer.innerHTML = '<div class="loading text-center p-3"><div class="spinner-border spinner-border-sm text-primary me-2"></div> Loading users...</div>';
      
      const { data: projectUsers, error } = await supabase
        .from('project_users')
        .select(`
          id,
          role,
          users(id, first_name, last_name, email, companies(name))
        `)
        .eq('project_id', projectId)
        .order('role');
      
      if (error) throw error;
      
      // Clear loading indicator
      usersContainer.innerHTML = '';
      
      if (!projectUsers || projectUsers.length === 0) {
        usersContainer.innerHTML = '<div class="no-data text-center p-3">No users assigned to this project</div>';
        return;
      }
      
      // Create users table
      const usersTable = document.createElement('table');
      usersTable.className = 'table table-sm';
      usersTable.innerHTML = `
        <thead>
          <tr>
            <th>Name</th>
            <th>Email</th>
            <th>Role</th>
            <th>Company</th>
            <th class="text-end">Actions</th>
          </tr>
        </thead>
        <tbody></tbody>
      `;
      
      const tbody = usersTable.querySelector('tbody');
      
      // Add user rows
      projectUsers.forEach(pu => {
        if (!pu.users) return;
        
        const user = pu.users;
        const row = document.createElement('tr');
        
        // Format role for display
        const role = pu.role.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
        
        row.innerHTML = `
          <td>${user.first_name} ${user.last_name}</td>
          <td>${user.email}</td>
          <td>${role}</td>
          <td>${user.companies ? user.companies.name : 'N/A'}</td>
          <td class="text-end">
            <button type="button" class="btn btn-sm btn-outline-danger remove-user-btn" data-id="${pu.id}">
              <i class="bi bi-trash"></i>
            </button>
          </td>
        `;
        
        tbody.appendChild(row);
      });
      
      usersContainer.appendChild(usersTable);
      
      // Add event listeners for remove buttons
      const removeButtons = usersContainer.querySelectorAll('.remove-user-btn');
      removeButtons.forEach(button => {
        button.addEventListener('click', async () => {
          const puId = button.dataset.id;
          await this.removeProjectUser(puId);
        });
      });
    } catch (error) {
      console.error('Error loading project users:', error);
      const usersContainer = document.getElementById('project-users-list');
      if (usersContainer) {
        usersContainer.innerHTML = `<div class="error text-danger p-3">Error loading users: ${error.message}</div>`;
      }
    }
  }
  
  // Remove a project user
  async removeProjectUser(projectUserId) {
    try {
      if (!confirm('Are you sure you want to remove this user from the project?')) {
        return;
      }
      
      const { error } = await supabase
        .from('project_users')
        .delete()
        .eq('id', projectUserId);
      
      if (error) throw error;
      
      // Reload project users
      const projectId = this.currentRecord.id;
      await this.loadProjectUsers(projectId);
      
      this.showSuccessMessage('User removed from project successfully');
    } catch (error) {
      console.error('Error removing project user:', error);
      this.showErrorMessage(`Failed to remove user: ${error.message}`);
    }
  }
  
  // Override to handle form submission with project users
  async submitForm() {
    const form = document.getElementById(this.formDomId);
    if (!form) return;
    
    // Check form validity
    if (!form.checkValidity()) {
      form.reportValidity();
      return;
    }
    
    // Get form data for the main record
    const formData = this.getFormData(form);
    
    try {
      appState.isLoading = true;
      this.showLoading(true);
      
      // Determine if this is a create or update
      const mode = form.dataset.mode;
      
      let projectId;