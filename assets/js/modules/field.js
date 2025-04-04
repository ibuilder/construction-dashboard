import CrudModule from '../components/crud.js';
import { supabase } from '../../../supabase/init.js';
import { currentUser } from '../auth.js';
import { formatDate } from '../app.js';

// Daily Reports Module
class DailyReportModule extends CrudModule {
  constructor() {
    super({
      table: 'daily_reports',
      primaryKey: 'id',
      columns: [
        { data: 'id', title: 'Report #' },
        { 
          data: 'report_date', 
          title: 'Date',
          render: (data) => formatDate(data)
        },
        { 
          data: 'weather_conditions', 
          title: 'Weather',
          render: (data, type, row) => {
            if (!data) return 'N/A';
            return `${data} (${row.temperature_low || 0}°-${row.temperature_high || 0}°)`;
          }
        },
        { 
          data: 'status', 
          title: 'Status',
          render: (data) => {
            const statusClasses = {
              'draft': 'badge bg-secondary',
              'submitted': 'badge bg-primary',
              'approved': 'badge bg-success',
              'rejected': 'badge bg-danger'
            };
            return `<span class="${statusClasses[data] || 'badge bg-secondary'}">${data.toUpperCase()}</span>`;
          }
        },
        { 
          data: 'created_by', 
          title: 'Author',
          render: (data, type, row) => {
            if (!data) return 'Unknown';
            return row.created_by_name || 'Loading...';
          }
        },
        { 
          data: 'created_at', 
          title: 'Created',
          render: (data) => formatDate(data)
        }
      ],
      tableDomId: 'daily-reports-table',
      formDomId: 'daily-report-form',
      detailsDomId: 'daily-report-details',
      module: 'field',
      recordType: 'daily_report',
      defaultSort: { column: 'report_date', direction: 'desc' },
      relations: [
        { table: 'users', fields: ['first_name', 'last_name'], as: 'created_by_user' }
      ]
    });
    
    // Add custom methods and event listeners
    this.initCustomEventListeners();
  }
  
  // Initialize custom event listeners
  initCustomEventListeners() {
    // Labor and Equipment sections in form
    document.addEventListener('click', (e) => {
      // Add Labor button
      if (e.target.classList.contains('add-labor-btn') || e.target.closest('.add-labor-btn')) {
        e.preventDefault();
        this.addLaborRow();
      }
      
      // Remove Labor button
      if (e.target.classList.contains('remove-labor-btn') || e.target.closest('.remove-labor-btn')) {
        e.preventDefault();
        const row = e.target.closest('.labor-row');
        if (row) row.remove();
      }
      
      // Add Equipment button
      if (e.target.classList.contains('add-equipment-btn') || e.target.closest('.add-equipment-btn')) {
        e.preventDefault();
        this.addEquipmentRow();
      }
      
      // Remove Equipment button
      if (e.target.classList.contains('remove-equipment-btn') || e.target.closest('.remove-equipment-btn')) {
        e.preventDefault();
        const row = e.target.closest('.equipment-row');
        if (row) row.remove();
      }
    });
  }
  
  // Add a new labor row to the form
  addLaborRow() {
    const laborContainer = document.getElementById('labor-container');
    if (!laborContainer) return;
    
    const rowIndex = document.querySelectorAll('.labor-row').length;
    const newRow = document.createElement('div');
    newRow.className = 'labor-row row g-3 mb-2 align-items-end border-bottom pb-2';
    newRow.innerHTML = `
      <div class="col-md-3">
        <label class="form-label">Company</label>
        <select class="form-select company-dropdown" name="labor[${rowIndex}][company_id]">
          <option value="">Select Company</option>
          <!-- Options will be populated by JavaScript -->
        </select>
      </div>
      <div class="col-md-2">
        <label class="form-label">Trade</label>
        <input type="text" class="form-control" name="labor[${rowIndex}][trade]">
      </div>
      <div class="col-md-2">
        <label class="form-label">Workers</label>
        <input type="number" class="form-control" name="labor[${rowIndex}][workers_count]" min="1" value="1">
      </div>
      <div class="col-md-2">
        <label class="form-label">Hours</label>
        <input type="number" class="form-control" name="labor[${rowIndex}][hours_worked]" min="0" step="0.5" value="8">
      </div>
      <div class="col-md-2">
        <label class="form-label">Work Area</label>
        <input type="text" class="form-control" name="labor[${rowIndex}][work_area]">
      </div>
      <div class="col-md-1">
        <button type="button" class="btn btn-danger remove-labor-btn">
          <i class="bi bi-trash"></i>
        </button>
      </div>
    `;
    
    laborContainer.appendChild(newRow);
    
    // Populate company dropdown for the new row
    this.populateCompanyDropdowns();
  }
  
  // Add a new equipment row to the form
  addEquipmentRow() {
    const equipmentContainer = document.getElementById('equipment-container');
    if (!equipmentContainer) return;
    
    const rowIndex = document.querySelectorAll('.equipment-row').length;
    const newRow = document.createElement('div');
    newRow.className = 'equipment-row row g-3 mb-2 align-items-end border-bottom pb-2';
    newRow.innerHTML = `
      <div class="col-md-4">
        <label class="form-label">Equipment Type</label>
        <input type="text" class="form-control" name="equipment[${rowIndex}][equipment_type]">
      </div>
      <div class="col-md-2">
        <label class="form-label">Quantity</label>
        <input type="number" class="form-control" name="equipment[${rowIndex}][quantity]" min="1" value="1">
      </div>
      <div class="col-md-2">
        <label class="form-label">Hours Used</label>
        <input type="number" class="form-control" name="equipment[${rowIndex}][hours_used]" min="0" step="0.5" value="8">
      </div>
      <div class="col-md-3">
        <label class="form-label">Work Area</label>
        <input type="text" class="form-control" name="equipment[${rowIndex}][work_area]">
      </div>
      <div class="col-md-1">
        <button type="button" class="btn btn-danger remove-equipment-btn">
          <i class="bi bi-trash"></i>
        </button>
      </div>
    `;
    
    equipmentContainer.appendChild(newRow);
  }
  
  // Override to handle the form submission with labor and equipment data
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
      
      let dailyReportId;
      
      if (mode === 'edit') {
        const id = form.dataset.id;
        const { data, error } = await this.updateRecord(id, formData);
        
        if (error) throw error;
        dailyReportId = id;
      } else {
        const { data, error } = await this.createRecord(formData);
        
        if (error) throw error;
        dailyReportId = data.id;
      }
      
      // Process labor data
      await this.processLaborData(dailyReportId, form);
      
      // Process equipment data
      await this.processEquipmentData(dailyReportId, form);
      
      // Show success message
      this.showSuccessMessage(`Daily Report ${mode === 'edit' ? 'updated' : 'created'} successfully.`);
      
      // Close form and reload data
      this.closeForm();
      await this.loadData();
      
      appState.isLoading = false;
      this.showLoading(false);
    } catch (error) {
      console.error('Error submitting form:', error);
      this.showErrorMessage(`Failed to ${form.dataset.mode === 'edit' ? 'update' : 'create'} daily report. ${error.message}`);
      appState.isLoading = false;
      this.showLoading(false);
    }
  }
  
  // Process labor data from form
  async processLaborData(dailyReportId, form) {
    try {
      // Get labor inputs from form
      const laborRows = Array.from(form.querySelectorAll('.labor-row'));
      
      if (laborRows.length === 0) return;
      
      // First delete existing labor records for this report
      await supabase
        .from('daily_report_labor')
        .delete()
        .eq('daily_report_id', dailyReportId);
      
      // Process each labor row
      const laborData = laborRows.map(row => {
        const companyId = row.querySelector('select[name*="company_id"]').value || null;
        const trade = row.querySelector('input[name*="trade"]').value || null;
        const workersCount = parseInt(row.querySelector('input[name*="workers_count"]').value) || 0;
        const hoursWorked = parseFloat(row.querySelector('input[name*="hours_worked"]').value) || 0;
        const workArea = row.querySelector('input[name*="work_area"]').value || null;
        
        return {
          daily_report_id: dailyReportId,
          company_id: companyId ? parseInt(companyId) : null,
          trade,
          workers_count: workersCount,
          hours_worked: hoursWorked,
          work_area: workArea,
          created_at: new Date().toISOString()
        };
      });
      
      // Insert labor records
      if (laborData.length > 0) {
        const { error } = await supabase
          .from('daily_report_labor')
          .insert(laborData);
        
        if (error) throw error;
      }
    } catch (error) {
      console.error('Error processing labor data:', error);
      throw error;
    }
  }
  
  // Process equipment data from form
  async processEquipmentData(dailyReportId, form) {
    try {
      // Get equipment inputs from form
      const equipmentRows = Array.from(form.querySelectorAll('.equipment-row'));
      
      if (equipmentRows.length === 0) return;
      
      // First delete existing equipment records for this report
      await supabase
        .from('daily_report_equipment')
        .delete()
        .eq('daily_report_id', dailyReportId);
      
      // Process each equipment row
      const equipmentData = equipmentRows.map(row => {
        const equipmentType = row.querySelector('input[name*="equipment_type"]').value || null;
        const quantity = parseInt(row.querySelector('input[name*="quantity"]').value) || 0;
        const hoursUsed = parseFloat(row.querySelector('input[name*="hours_used"]').value) || 0;
        const workArea = row.querySelector('input[name*="work_area"]').value || null;
        
        return {
          daily_report_id: dailyReportId,
          equipment_type: equipmentType,
          quantity,
          hours_used: hoursUsed,
          work_area: workArea,
          created_at: new Date().toISOString()
        };
      });
      
      // Insert equipment records
      if (equipmentData.length > 0) {
        const { error } = await supabase
          .from('daily_report_equipment')
          .insert(equipmentData);
        
        if (error) throw error;
      }
    } catch (error) {
      console.error('Error processing equipment data:', error);
      throw error;
    }
  }
  
  // Override to load labor and equipment data when editing a record
  async openForm(data = null) {
    // Call parent method to open form
    super.openForm(data);
    
    // Clear existing labor and equipment rows
    const laborContainer = document.getElementById('labor-container');
    if (laborContainer) {
      laborContainer.innerHTML = '';
    }
    
    const equipmentContainer = document.getElementById('equipment-container');
    if (equipmentContainer) {
      equipmentContainer.innerHTML = '';
    }
    
    // If editing an existing report, load labor and equipment data
    if (data) {
      await this.loadLaborData(data.id);
      await this.loadEquipmentData(data.id);
    } else {
      // If creating a new report, add empty rows
      this.addLaborRow();
      this.addEquipmentRow();
    }
  }
  
  // Load labor data for a daily report
  async loadLaborData(reportId) {
    try {
      const { data: laborData, error } = await supabase
        .from('daily_report_labor')
        .select(`
          id,
          company_id,
          trade,
          workers_count,
          hours_worked,
          work_area,
          companies(name)
        `)
        .eq('daily_report_id', reportId)
        .order('id');
      
      if (error) throw error;
      
      if (laborData && laborData.length > 0) {
        // Add labor rows for each record
        laborData.forEach(labor => {
          this.addLaborRow();
        });
        
        // Fill in the data
        const laborRows = document.querySelectorAll('.labor-row');
        laborData.forEach((labor, index) => {
          if (index < laborRows.length) {
            const row = laborRows[index];
            const companySelect = row.querySelector('select[name*="company_id"]');
            const tradeInput = row.querySelector('input[name*="trade"]');
            const workersInput = row.querySelector('input[name*="workers_count"]');
            const hoursInput = row.querySelector('input[name*="hours_worked"]');
            const workAreaInput = row.querySelector('input[name*="work_area"]');
            
            if (companySelect) companySelect.value = labor.company_id || '';
            if (tradeInput) tradeInput.value = labor.trade || '';
            if (workersInput) workersInput.value = labor.workers_count || 1;
            if (hoursInput) hoursInput.value = labor.hours_worked || 0;
            if (workAreaInput) workAreaInput.value = labor.work_area || '';
          }
        });
      } else {
        // Add an empty row if no data
        this.addLaborRow();
      }
    } catch (error) {
      console.error('Error loading labor data:', error);
      this.showErrorMessage('Failed to load labor data. ' + error.message);
    }
  }
  
  // Load equipment data for a daily report
  async loadEquipmentData(reportId) {
    try {
      const { data: equipmentData, error } = await supabase
        .from('daily_report_equipment')
        .select('*')
        .eq('daily_report_id', reportId)
        .order('id');
      
      if (error) throw error;
      
      if (equipmentData && equipmentData.length > 0) {
        // Add equipment rows for each record
        equipmentData.forEach(equipment => {
          this.addEquipmentRow();
        });
        
        // Fill in the data
        const equipmentRows = document.querySelectorAll('.equipment-row');
        equipmentData.forEach((equipment, index) => {
          if (index < equipmentRows.length) {
            const row = equipmentRows[index];
            const typeInput = row.querySelector('input[name*="equipment_type"]');
            const quantityInput = row.querySelector('input[name*="quantity"]');
            const hoursInput = row.querySelector('input[name*="hours_used"]');
            const workAreaInput = row.querySelector('input[name*="work_area"]');
            
            if (typeInput) typeInput.value = equipment.equipment_type || '';
            if (quantityInput) quantityInput.value = equipment.quantity || 1;
            if (hoursInput) hoursInput.value = equipment.hours_used || 0;
            if (workAreaInput) workAreaInput.value = equipment.work_area || '';
          }
        });
      } else {
        // Add an empty row if no data
        this.addEquipmentRow();
      }
    } catch (error) {
      console.error('Error loading equipment data:', error);
      this.showErrorMessage('Failed to load equipment data. ' + error.message);
    }
  }
  
  // Override to customize how daily report details are displayed
  updateDetailsContent(container, record) {
    // Call parent method for common fields
    super.updateDetailsContent(container, record);
    
    // Update daily report-specific fields
    if (container) {
      // Report Number
      const reportNumber = container.querySelector('.report-number');
      if (reportNumber) {
        reportNumber.textContent = `Daily Report #${record.id}`;
      }
      
      // Report Date
      const reportDateElement = container.querySelector('.report-date');
      if (reportDateElement && record.report_date) {
        reportDateElement.textContent = formatDate(record.report_date);
      }
      
      // Weather
      const weatherElement = container.querySelector('.weather-conditions');
      if (weatherElement) {
        let weatherText = record.weather_conditions || 'Not recorded';
        if (record.temperature_low || record.temperature_high) {
          weatherText += ` (${record.temperature_low || 0}° - ${record.temperature_high || 0}°)`;
        }
        if (record.precipitation) {
          weatherText += `, ${record.precipitation}`;
        }
        if (record.wind_speed) {
          weatherText += `, Wind: ${record.wind_speed}`;
        }
        weatherElement.textContent = weatherText;
      }
      
      // Work Performed
      const workPerformedElement = container.querySelector('.work-performed');
      if (workPerformedElement && record.work_performed) {
        workPerformedElement.innerHTML = record.work_performed.replace(/\n/g, '<br>');
      }
      
      // Issues Encountered
      const issuesElement = container.querySelector('.issues-encountered');
      if (issuesElement) {
        if (record.issues_encountered) {
          issuesElement.innerHTML = record.issues_encountered.replace(/\n/g, '<br>');
        } else {
          issuesElement.innerHTML = '<em>No issues reported</em>';
        }
      }
      
      // Safety Incidents
      const safetyElement = container.querySelector('.safety-incidents');
      if (safetyElement) {
        if (record.safety_incidents) {
          safetyElement.innerHTML = record.safety_incidents.replace(/\n/g, '<br>');
        } else {
          safetyElement.innerHTML = '<em>No safety incidents reported</em>';
        }
      }
      
      // Visitors
      const visitorsElement = container.querySelector('.visitors');
      if (visitorsElement) {
        if (record.visitors) {
          visitorsElement.innerHTML = record.visitors.replace(/\n/g, '<br>');
        } else {
          visitorsElement.innerHTML = '<em>No visitors reported</em>';
        }
      }
      
      // Delay Factors
      const delayElement = container.querySelector('.delay-factors');
      if (delayElement) {
        if (record.delay_factors) {
          delayElement.innerHTML = record.delay_factors.replace(/\n/g, '<br>');
        } else {
          delayElement.innerHTML = '<em>No delays reported</em>';
        }
      }
      
      // Load labor and equipment data
      this.loadLaborDetails(record.id);
      this.loadEquipmentDetails(record.id);
    }
  }
  
  // Load labor details for display
  async loadLaborDetails(reportId) {
    try {
      const laborContainer = document.getElementById('labor-details');
      if (!laborContainer) return;
      
      laborContainer.innerHTML = '<div class="loading text-center p-3"><div class="spinner-border spinner-border-sm text-primary me-2"></div> Loading labor data...</div>';
      
      const { data: laborData, error } = await supabase
        .from('daily_report_labor')
        .select(`
          id,
          company_id,
          trade,
          workers_count,
          hours_worked,
          work_area,
          notes,
          companies(name)
        `)
        .eq('daily_report_id', reportId)
        .order('id');
      
      if (error) throw error;
      
      // Clear loading indicator
      laborContainer.innerHTML = '';
      
      if (!laborData || laborData.length === 0) {
        laborContainer.innerHTML = '<div class="no-data text-center p-3">No labor data recorded for this report</div>';
        return;
      }
      
      // Create labor table
      const laborTable = document.createElement('table');
      laborTable.className = 'table table-sm';
      laborTable.innerHTML = `
        <thead>
          <tr>
            <th>Company</th>
            <th>Trade</th>
            <th>Workers</th>
            <th>Hours</th>
            <th>Work Area</th>
          </tr>
        </thead>
        <tbody></tbody>
        <tfoot>
          <tr class="table-light">
            <th colspan="2">Totals:</th>
            <th></th>
            <th></th>
            <th></th>
          </tr>
        </tfoot>
      `;
      
      const tbody = laborTable.querySelector('tbody');
      
      // Calculate totals
      let totalWorkers = 0;
      let totalHours = 0;
      
      // Add labor rows
      laborData.forEach(labor => {
        const row = document.createElement('tr');
        row.innerHTML = `
          <td>${labor.companies ? labor.companies.name : 'N/A'}</td>
          <td>${labor.trade || 'N/A'}</td>
          <td>${labor.workers_count || 0}</td>
          <td>${labor.hours_worked || 0}</td>
          <td>${labor.work_area || 'N/A'}</td>
        `;
        
        tbody.appendChild(row);
        
        // Update totals
        totalWorkers += labor.workers_count || 0;
        totalHours += labor.hours_worked || 0;
      });
      
      // Update totals in footer
      const footerRow = laborTable.querySelector('tfoot tr');
      footerRow.innerHTML = `
        <th colspan="2">Totals:</th>
        <th>${totalWorkers}</th>
        <th>${totalHours}</th>
        <th></th>
      `;
      
      laborContainer.appendChild(laborTable);
    } catch (error) {
      console.error('Error loading labor details:', error);
      const laborContainer = document.getElementById('labor-details');
      if (laborContainer) {
        laborContainer.innerHTML = `<div class="error text-danger p-3">Error loading labor data: ${error.message}</div>`;
      }
    }
  }
  
  // Load equipment details for display
  async loadEquipmentDetails(reportId) {
    try {
      const equipmentContainer = document.getElementById('equipment-details');
      if (!equipmentContainer) return;
      
      equipmentContainer.innerHTML = '<div class="loading text-center p-3"><div class="spinner-border spinner-border-sm text-primary me-2"></div> Loading equipment data...</div>';
      
      const { data: equipmentData, error } = await supabase
        .from('daily_report_equipment')
        .select('*')
        .eq('daily_report_id', reportId)
        .order('id');
      
      if (error) throw error;
      
      // Clear loading indicator
      equipmentContainer.innerHTML = '';
      
      if (!equipmentData || equipmentData.length === 0) {
        equipmentContainer.innerHTML = '<div class="no-data text-center p-3">No equipment data recorded for this report</div>';
        return;
      }
      
      // Create equipment table
      const equipmentTable = document.createElement('table');
      equipmentTable.className = 'table table-sm';
      equipmentTable.innerHTML = `
        <thead>
          <tr>
            <th>Equipment Type</th>
            <th>Quantity</th>
            <th>Hours Used</th>
            <th>Work Area</th>
          </tr>
        </thead>
        <tbody></tbody>
        <tfoot>
          <tr class="table-light">
            <th>Totals:</th>
            <th></th>
            <th></th>
            <th></th>
          </tr>
        </tfoot>
      `;
      
      const tbody = equipmentTable.querySelector('tbody');
      
      // Calculate totals
      let totalQuantity = 0;
      let totalHours = 0;
      
      // Add equipment rows
      equipmentData.forEach(equipment => {
        const row = document.createElement('tr');
        row.innerHTML = `
          <td>${equipment.equipment_type || 'N/A'}</td>
          <td>${equipment.quantity || 0}</td>
          <td>${equipment.hours_used || 0}</td>
          <td>${equipment.work_area || 'N/A'}</td>
        `;
        
        tbody.appendChild(row);
        
        // Update totals
        totalQuantity += equipment.quantity || 0;
        totalHours += equipment.hours_used || 0;
      });
      
      // Update totals in footer
      const footerRow = equipmentTable.querySelector('tfoot tr');
      footerRow.innerHTML = `
        <th>Totals:</th>
        <th>${totalQuantity}</th>
        <th>${totalHours}</th>
        <th></th>
      `;
      
      equipmentContainer.appendChild(equipmentTable);
    } catch (error) {
      console.error('Error loading equipment details:', error);
      const equipmentContainer = document.getElementById('equipment-details');
      if (equipmentContainer) {
        equipmentContainer.innerHTML = `<div class="error text-danger p-3">Error loading equipment data: ${error.message}</div>`;
      }
    }
  }
  
  // Initialize related data for dropdowns
  async initRelatedData() {
    try {
      // Fetch companies for dropdowns
      const { data: companies, error } = await supabase
        .from('companies')
        .select('id, name, type')
        .order('name');
      
      if (error) throw error;
      
      // Populate company dropdowns
      this.companies = companies;
      this.populateCompanyDropdowns();
    } catch (error) {
      console.error('Error initializing related data:', error);
    }
  }
  
  // Populate company dropdowns
  populateCompanyDropdowns() {
    if (!this.companies) return;
    
    const companyDropdowns = document.querySelectorAll('.company-dropdown');
    
    companyDropdowns.forEach(dropdown => {
      // Preserve selected value
      const selectedValue = dropdown.value;
      
      // Clear existing options except the first one
      while (dropdown.options.length > 1) {
        dropdown.remove(1);
      }
      
      // Add company options
      this.companies.forEach(company => {
        const option = document.createElement('option');
        option.value = company.id;
        option.textContent = `${company.name} (${company.type})`;
        dropdown.appendChild(option);
      });
      
      // Restore selected value
      if (selectedValue) {
        dropdown.value = selectedValue;
      }
    });
  }
  
  // Override to customize the form data before submission
  getFormData(form) {
    const formData = super.getFormData(form);
    
    // Set default values for new daily reports
    if (form.dataset.mode === 'create') {
      formData.status = formData.status || 'draft';
      formData.report_date = formData.report_date || new Date().toISOString().split('T')[0];
    }
    
    return formData;
  }
}

// Photo Library Module
class PhotoLibraryModule extends CrudModule {
  constructor() {
    super({
      table: 'photos',
      primaryKey: 'id',
      columns: [
        { data: 'id', title: 'Photo #' },
        { 
          data: 'photo_url', 
          title: 'Photo',
          render: (data) => data ? `<img src="${data}" class="thumbnail" style="max-width: 100px; max-height: 60px;">` : 'No Image'
        },
        { data: 'title', title: 'Title' },
        { data: 'location', title: 'Location' },
        { 
          data: 'taken_at', 
          title: 'Date Taken',
          render: (data) => data ? formatDate(data) : formatDate(row.created_at)
        },
        { 
          data: 'created_by', 
          title: 'Uploaded By',
          render: (data, type, row) => {
            if (!data) return 'Unknown';
            return row.created_by_name || 'Loading...';
          }
        },
        { 
          data: 'created_at', 
          title: 'Uploaded On',
          render: (data) => formatDate(data)
        }
      ],
      tableDomId: 'photos-table',
      formDomId: 'photo-form',
      detailsDomId: 'photo-details',
      module: 'field',
      recordType: 'photo',
      defaultSort: { column: 'taken_at', direction: 'desc' },
      relations: [
        { table: 'users', fields: ['first_name', 'last_name'], as: 'created_by_user' }
      ],
      hasAttachments: false // Photos are handled differently than regular attachments
    });
    
    // Add custom methods and event listeners
    this.initCustomEventListeners();
  }
  
  // Initialize custom event listeners
  initCustomEventListeners() {
    // Photo upload preview
    const photoInput = document.getElementById('photo-upload');
    if (photoInput) {
      photoInput.addEventListener('change', (e) => {
        this.handlePhotoPreview(e);
      });
    }
    
    // Apply filters for photo gallery view
    const filterForm = document.getElementById('gallery-filter-form');
    if (filterForm) {
      filterForm.addEventListener('submit', (e) => {
        e.preventDefault();
        this.loadGalleryView();
      });
      
      const resetButton = filterForm.querySelector('.reset-filters');
      if (resetButton) {
        resetButton.addEventListener('click', () => {
          filterForm.reset();
          this.loadGalleryView();
        });
      }
    }
    
    // Toggle between table and gallery views
    const viewToggleButtons = document.querySelectorAll('.view-toggle-btn');
    viewToggleButtons.forEach(button => {
      button.addEventListener('click', (e) => {
        e.preventDefault();
        const viewType = button.dataset.view;
        this.toggleView(viewType);
      });
    });
  }
  
  // Handle photo preview in upload form
  handlePhotoPreview(e) {
    const photoPreview = document.getElementById('photo-preview');
    if (!photoPreview) return;
    
    const files = e.target.files;
    if (!files || files.length === 0) {
      photoPreview.innerHTML = '<div class="no-preview">No photo selected</div>';
      return;
    }
    
    const file = files[0];
    if (!file.type.startsWith('image/')) {
      photoPreview.innerHTML = '<div class="error-preview">Selected file is not an image</div>';
      return;
    }
    
    const reader = new FileReader();
    reader.onload = (e) => {
      photoPreview.innerHTML = `
        <img src="${e.target.result}" class="img-fluid preview-image" alt="Photo Preview">
      `;
    };
    reader.readAsDataURL(file);
  }
  
  // Override to handle photo upload
  async submitForm() {
    const form = document.getElementById(this.formDomId);
    if (!form) return;
    
    // Check form validity
    if (!form.checkValidity()) {
      form.reportValidity();
      return;
    }
    
    // Get form data
    const formData = this.getFormData(form);
    
    // Check if photo is provided for new photos
    const photoInput = document.getElementById('photo-upload');
    if (form.dataset.mode === 'create' && (!photoInput || !photoInput.files || photoInput.files.length === 0)) {
      this.showErrorMessage('Please select a photo to upload.');
      return;
    }
    
    try {
      appState.isLoading = true;
      this.showLoading(true);
      
      let photoRecord;
      
      if (form.dataset.mode === 'edit') {
        const id = form.dataset.id;
        
        // Update without changing the photo
        const { data, error } = await this.updateRecord(id, formData);
        
        if (error) throw error;
        photoRecord = data;
        
        // Check if a new photo was provided
        if (photoInput && photoInput.files && photoInput.files.length > 0) {
          // Upload new photo
          const photoUrl = await this.uploadPhoto(photoInput.files[0], id);
          
          // Update record with new photo URL
          const { error: updateError } = await supabase
            .from('photos')
            .update({ photo_url: photoUrl })
            .eq(this.primaryKey, id);
          
          if (updateError) throw updateError;
        }
      } else {
        // For new photos, we need to create the record first, then upload the photo
        // Store placeholder for photo URL, we'll update it after upload
        formData.photo_url = 'pending';
        
        // Create the record
        const { data, error } = await this.createRecord(formData);
        
        if (error) throw error;
        photoRecord = data;
        
        // Upload the photo
        const photoUrl = await this.uploadPhoto(photoInput.files[0], photoRecord.id);
        
        // Update record with actual photo URL
        const { error: updateError } = await supabase
          .from('photos')
          .update({ photo_url: photoUrl })
          .eq(this.primaryKey, photoRecord.id);
        
        if (updateError) throw updateError;
      }
      
      // Show success message
      this.showSuccessMessage(`Photo ${form.dataset.mode === 'edit' ? 'updated' : 'uploaded'} successfully.`);
      
      // Close form and reload data
      this.closeForm();
      await this.loadData();
      
      appState.isLoading = false;
      this.showLoading(false);
    } catch (error) {
      console.error('Error submitting form:', error);
      this.showErrorMessage(`Failed to ${form.dataset.mode === 'edit' ? 'update' : 'upload'} photo. ${error.message}`);
      appState.isLoading = false;
      this.showLoading(false);
    }
  }
  
  // Upload photo to storage
  async uploadPhoto(file, photoId) {
    try {
      // Generate unique file name
      const timestamp = new Date().getTime();
      const fileExtension = file.name.split('.').pop();
      const fileName = `photo_${photoId}_${timestamp}.${fileExtension}`;
      const filePath = `photos/${fileName}`;
      
      // Upload file to storage
      const { data, error } = await supabase.storage
        .from('photos')
        .upload(filePath, file, {
          cacheControl: '3600',
          upsert: false
        });
      
      if (error) throw error;
      
      // Get public URL
      const { data: urlData } = await supabase.storage
        .from('photos')
        .getPublicUrl(filePath);
      
      return urlData.publicUrl;
    } catch (error) {
      console.error('Error uploading photo:', error);
      throw error;
    }
  }
  
  // Toggle between table and gallery views
  toggleView(viewType) {
    const tableContainer = document.getElementById('table-view');
    const galleryContainer = document.getElementById('gallery-view');
    
    // Update active button
    const tableButton = document.querySelector('[data-view="table"]');
    const galleryButton = document.querySelector('[data-view="gallery"]');
    
    if (viewType === 'gallery') {
      if (tableContainer) tableContainer.style.display = 'none';
      if (galleryContainer) galleryContainer.style.display = 'block';
      
      if (tableButton) tableButton.classList.remove('active');
      if (galleryButton) galleryButton.classList.add('active');
      
      // Load gallery view
      this.loadGalleryView();
    } else {
      if (tableContainer) tableContainer.style.display = 'block';
      if (galleryContainer) galleryContainer.style.display = 'none';
      
      if (tableButton) tableButton.classList.add('active');
      if (galleryButton) galleryButton.classList.remove('active');
    }
  }
  
  // Load gallery view
  async loadGalleryView() {
    try {
      const galleryContainer = document.getElementById('photo-gallery');
      if (!galleryContainer) return;
      
      galleryContainer.innerHTML = '<div class="loading text-center p-5"><div class="spinner-border text-primary"></div><p class="mt-2">Loading photos...</p></div>';
      
      // Get filter values
      const filterForm = document.getElementById('gallery-filter-form');
      const filters = filterForm ? this.getFormData(filterForm) : {};
      
      // Start query
      let query = supabase
        .from('photos')
        .select(`
          id,
          title,
          description,
          photo_url,
          thumbnail_url,
          location,
          taken_at,
          created_at,
          users(first_name, last_name)
        `)
        .order('taken_at', { ascending: false });
      
      // Apply filters
      if (filters.search) {
        query = query.or(`title.ilike.%${filters.search}%,description.ilike.%${filters.search}%,location.ilike.%${filters.search}%`);
      }
      
      if (filters.location) {
        query = query.ilike('location', `%${filters.location}%`);
      }
      
      if (filters.date_from) {
        query = query.gte('taken_at', filters.date_from);
      }
      
      if (filters.date_to) {
        query = query.lte('taken_at', filters.date_to);
      }
      
      // Execute query
      const { data, error } = await query;
      
      if (error) throw error;
      
      // Clear loading indicator
      galleryContainer.innerHTML = '';
      
      // Check if no photos
      if (!data || data.length === 0) {
        galleryContainer.innerHTML = '<div class="no-photos text-center p-5"><i class="bi bi-image fs-1"></i><p class="mt-2">No photos found</p></div>';
        return;
      }
      
      // Create photo gallery
      const photoGrid = document.createElement('div');
      photoGrid.className = 'row g-3';
      
      data.forEach(photo => {
        const photoCol = document.createElement('div');
        photoCol.className = 'col-md-4 col-lg-3';
        
        const photoCard = document.createElement('div');
        photoCard.className = 'card photo-card h-100';
        photoCard.innerHTML = `
          <a href="#" class="photo-link" data-id="${photo.id}">
            <img src="${photo.thumbnail_url || photo.photo_url}" class="card-img-top" alt="${photo.title}">
          </a>
          <div class="card-body">
            <h6 class="card-title">${photo.title}</h6>
            <p class="card-text small text-muted">
              ${photo.location ? `<i class="bi bi-geo-alt me-1"></i>${photo.location}<br>` : ''}
              <i class="bi bi-calendar me-1"></i>${formatDate(photo.taken_at || photo.created_at)}
            </p>
          </div>
        `;
        
        photoCol.appendChild(photoCard);
        photoGrid.appendChild(photoCol);
      });
      
      galleryContainer.appendChild(photoGrid);
      
      // Add click event for photo links
      const photoLinks = galleryContainer.querySelectorAll('.photo-link');
      photoLinks.forEach(link => {
        link.addEventListener('click', (e) => {
          e.preventDefault();
          const photoId = link.dataset.id;
          this.viewRecord(photoId);
        });
      });
    } catch (error) {
      console.error('Error loading gallery view:', error);
      const galleryContainer = document.getElementById('photo-gallery');
      if (galleryContainer) {
        galleryContainer.innerHTML = `<div class="error text-danger p-5">Error loading photos: ${error.message}</div>`;
      }
    }
  }
  
  // Override to customize how photo details are displayed
  updateDetailsContent(container, record) {
    // Call parent method for common fields
    super.updateDetailsContent(container, record);
    
    // Update photo-specific fields
    if (container) {
      // Photo display
      const photoDisplay = container.querySelector('.photo-display');
      if (photoDisplay && record.photo_url) {
        photoDisplay.innerHTML = `
          <img src="${record.photo_url}" class="img-fluid" alt="${record.title}">
        `;
      }
      
      // Title
      const titleElement = container.querySelector('.record-title');
      if (titleElement) {
        titleElement.textContent = record.title;
      }
      
      // Description
      const descriptionElement = container.querySelector('.photo-description');
      if (descriptionElement) {
        if (record.description) {
          descriptionElement.innerHTML = record.description.replace(/\n/g, '<br>');
        } else {
          descriptionElement.innerHTML = '<em>No description</em>';
        }
      }
      
      // Location
      const locationElement = container.querySelector('.photo-location');
      if (locationElement) {
        locationElement.textContent = record.location || 'Not specified';
      }
      
      // Date taken
      const dateElement = container.querySelector('.photo-date');
      if (dateElement) {
        dateElement.textContent = formatDate(record.taken_at || record.created_at);
      }
      
      // Tags
      const tagsElement = container.querySelector('.photo-tags');
      if (tagsElement) {
        if (record.tags && record.tags.length > 0) {
          tagsElement.innerHTML = record.tags.map(tag => `<span class="badge bg-secondary me-1">${tag}</span>`).join('');
        } else {
          tagsElement.innerHTML = '<em>No tags</em>';
        }
      }
      
      // GPS coordinates
      const gpsElement = container.querySelector('.photo-gps');
      if (gpsElement) {
        if (record.latitude && record.longitude) {
          gpsElement.innerHTML = `
            <div>${record.latitude}, ${record.longitude}</div>
            <a href="https://maps.google.com/?q=${record.latitude},${record.longitude}" target="_blank" class="btn btn-sm btn-outline-primary mt-2">
              <i class="bi bi-map me-1"></i> View on Map
            </a>
          `;
        } else {
          gpsElement.innerHTML = '<em>No GPS data</em>';
        }
      }
    }
  }
}

// Initialize modules
const initFieldModules = () => {
  // Determine which module to initialize based on current page
  const currentPath = window.location.pathname;
  
  if (currentPath.includes('/field/daily-reports.html')) {
    return new DailyReportModule();
  } else if (currentPath.includes('/field/photo-library.html')) {
    return new PhotoLibraryModule();
  }
  // Add more module initializations as needed
};

export default initFieldModules;