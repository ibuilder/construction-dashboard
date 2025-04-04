let invoiceId;
      
      if (mode === 'edit') {
        const id = form.dataset.id;
        const { data, error } = await this.updateRecord(id, formData);
        
        if (error) throw error;
        invoiceId = id;
      } else {
        const { data, error } = await this.createRecord(formData);
        
        if (error) throw error;
        invoiceId = data.id;
      }
      
      // Process line items
      await this.processLineItems(invoiceId, form);
      
      // Show success message
      this.showSuccessMessage(`Invoice ${mode === 'edit' ? 'updated' : 'created'} successfully.`);
      
      // Close form and reload data
      this.closeForm();
      await this.loadData();
      
      appState.isLoading = false;
      this.showLoading(false);
    } catch (error) {
      console.error('Error submitting form:', error);
      this.showErrorMessage(`Failed to ${form.dataset.mode === 'edit' ? 'update' : 'create'} invoice. ${error.message}`);
      appState.isLoading = false;
      this.showLoading(false);
    }
  }
  
  // Process line items from form
  async processLineItems(invoiceId, form) {
    try {
      // Get line item inputs from form
      const lineItemRows = Array.from(form.querySelectorAll('.line-item-row'));
      
      if (lineItemRows.length === 0) return;
      
      // First delete existing line items for this invoice
      await supabase
        .from('invoice_line_items')
        .delete()
        .eq('invoice_id', invoiceId);
      
      // Process each line item
      const lineItemsData = lineItemRows.map(row => {
        const costCode = row.querySelector('input[name*="cost_code"]').value || null;
        const description = row.querySelector('input[name*="description"]').value || null;
        const scheduledValue = parseFloat(row.querySelector('input[name*="scheduled_value"]').value) || 0;
        const previousWork = parseFloat(row.querySelector('input[name*="previous_work_completed"]').value) || 0;
        const currentWork = parseFloat(row.querySelector('input[name*="current_work_completed"]').value) || 0;
        const materialsStored = parseFloat(row.querySelector('input[name*="materials_stored"]').value) || 0;
        const retainagePercentage = parseFloat(row.querySelector('input[name*="retainage_percentage"]').value) || 0;
        
        // Calculate derived values
        const totalCompletedAndStored = previousWork + currentWork + materialsStored;
        const percentageComplete = scheduledValue > 0 ? (totalCompletedAndStored / scheduledValue) * 100 : 0;
        const balanceToFinish = scheduledValue - totalCompletedAndStored;
        const retainage = (totalCompletedAndStored * retainagePercentage) / 100;
        
        return {
          invoice_id: invoiceId,
          cost_code: costCode,
          description: description,
          scheduled_value: scheduledValue,
          previous_work_completed: previousWork,
          current_work_completed: currentWork,
          materials_stored: materialsStored,
          retainage: retainage
        };
      });
      
      // Insert line items
      if (lineItemsData.length > 0) {
        const { error } = await supabase
          .from('invoice_line_items')
          .insert(lineItemsData);
        
        if (error) throw error;
      }
    } catch (error) {
      console.error('Error processing line items:', error);
      throw error;
    }
  }
  
  // Override to load line items when editing an invoice
  async openForm(data = null) {
    // Call parent method to open form
    super.openForm(data);
    
    // Clear existing line items
    const lineItemsContainer = document.getElementById('line-items-container');
    if (lineItemsContainer) {
      lineItemsContainer.innerHTML = '';
    }
    
    // If editing an existing invoice, load line items
    if (data) {
      await this.loadLineItems(data.id);
      
      // Set contract selection if applicable
      if (data.contract_type && data.contract_id) {
        const contractTypeSelect = document.getElementById('contract_type');
        const contractIdSelect = document.getElementById('contract_id');
        
        if (contractTypeSelect) {
          contractTypeSelect.value = data.contract_type;
          // Trigger change event to load contracts
          const event = new Event('change');
          contractTypeSelect.dispatchEvent(event);
          
          // Set contract ID after options are loaded
          if (contractIdSelect) {
            setTimeout(() => {
              contractIdSelect.value = data.contract_id;
            }, 500);
          }
        }
      }
      
      // Set company if applicable
      if (data.company_id) {
        const companySelect = document.getElementById('company_id');
        if (companySelect) {
          companySelect.value = data.company_id;
        }
      }
    } else {
      // Add empty line item for new invoice
      this.addLineItemRow();
    }
  }
  
  // Load line items for an invoice
  async loadLineItems(invoiceId) {
    try {
      const { data: lineItems, error } = await supabase
        .from('invoice_line_items')
        .select('*')
        .eq('invoice_id', invoiceId)
        .order('id');
      
      if (error) throw error;
      
      if (lineItems && lineItems.length > 0) {
        // Add line item rows for each record
        lineItems.forEach(() => {
          this.addLineItemRow();
        });
        
        // Fill in the data
        const lineItemRows = document.querySelectorAll('.line-item-row');
        lineItems.forEach((item, index) => {
          if (index < lineItemRows.length) {
            const row = lineItemRows[index];
            
            row.querySelector('input[name*="cost_code"]').value = item.cost_code || '';
            row.querySelector('input[name*="description"]').value = item.description || '';
            row.querySelector('input[name*="scheduled_value"]').value = item.scheduled_value || 0;
            row.querySelector('input[name*="previous_work_completed"]').value = item.previous_work_completed || 0;
            row.querySelector('input[name*="current_work_completed"]').value = item.current_work_completed || 0;
            row.querySelector('input[name*="materials_stored"]').value = item.materials_stored || 0;
            
            // Calculate retainage percentage
            const retainagePercentage = item.scheduled_value > 0 ? 
              (item.retainage / (item.previous_work_completed + item.current_work_completed + item.materials_stored)) * 100 : 
              10;
              
            row.querySelector('input[name*="retainage_percentage"]').value = retainagePercentage.toFixed(2);
          }
        });
        
        // Recalculate totals
        this.recalculateInvoiceTotals();
      }
    } catch (error) {
      console.error('Error loading line items:', error);
      this.showErrorMessage('Failed to load line items. ' + error.message);
    }
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
      
      // Populate companies dropdown
      const companySelect = document.getElementById('company_id');
      if (companySelect) {
        // Clear existing options except the first one
        while (companySelect.options.length > 1) {
          companySelect.remove(1);
        }
        
        // Add company options
        companies.forEach(company => {
          const option = document.createElement('option');
          option.value = company.id;
          option.textContent = `${company.name} (${company.type})`;
          companySelect.appendChild(option);
        });
      }
    } catch (error) {
      console.error('Error initializing related data:', error);
    }
  }
  
  // Override to customize the form data before submission
  getFormData(form) {
    const formData = super.getFormData(form);
    
    // Set default values for new invoices
    if (form.dataset.mode === 'create') {
      formData.status = formData.status || 'draft';
      formData.issue_date = formData.issue_date || new Date().toISOString().split('T')[0];
      formData.due_date = formData.due_date || new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0];
      formData.paid = false;
    }
    
    return formData;
  }
}

// Change Orders Module
class ChangeOrderModule extends CrudModule {
  constructor() {
    super({
      table: 'change_orders',
      primaryKey: 'id',
      columns: [
        { data: 'change_order_number', title: 'CO #' },
        { data: 'title', title: 'Title' },
        { 
          data: 'company_id', 
          title: 'Company',
          render: (data, type, row) => {
            return row.company_name || 'Loading...';
          }
        },
        { 
          data: 'cost_impact', 
          title: 'Cost Impact',
          render: (data) => formatCurrency(data || 0)
        },
        { 
          data: 'schedule_impact', 
          title: 'Schedule Impact',
          render: (data) => data ? `${data} days` : 'None'
        },
        { 
          data: 'status', 
          title: 'Status',
          render: (data) => {
            const statusClasses = {
              'draft': 'badge bg-secondary',
              'submitted': 'badge bg-primary',
              'in_review': 'badge bg-warning text-dark',
              'approved': 'badge bg-success',
              'rejected': 'badge bg-danger',
              'void': 'badge bg-dark'
            };
            return `<span class="${statusClasses[data] || 'badge bg-secondary'}">${data.replace('_', ' ').toUpperCase()}</span>`;
          }
        },
        { 
          data: 'submitted_date', 
          title: 'Submitted',
          render: (data) => data ? formatDate(data) : 'N/A'
        },
        { 
          data: 'approved_date', 
          title: 'Approved',
          render: (data) => data ? formatDate(data) : 'N/A'
        }
      ],
      tableDomId: 'change-orders-table',
      formDomId: 'change-order-form',
      detailsDomId: 'change-order-details',
      module: 'cost',
      recordType: 'change_order',
      defaultSort: { column: 'change_order_number', direction: 'desc' },
      relations: [
        { table: 'companies', fields: ['name'], as: 'company' },
        { table: 'potential_changes', fields: ['title'], as: 'potential_change' }
      ]
    });
    
    // Add custom methods and event listeners
    this.initCustomEventListeners();
  }
  
  // Initialize custom event listeners
  initCustomEventListeners() {
    // Contract type selection
    document.addEventListener('change', (e) => {
      if (e.target.id === 'contract_type') {
        this.handleContractTypeChange(e.target);
      }
    });
    
    // Potential change selection
    document.addEventListener('change', (e) => {
      if (e.target.id === 'potential_change_id') {
        this.handlePotentialChangeSelection(e.target);
      }
    });
    
    // Add line item button
    document.addEventListener('click', (e) => {
      if (e.target.classList.contains('add-line-item-btn') || e.target.closest('.add-line-item-btn')) {
        e.preventDefault();
        this.addLineItemRow();
      }
      
      // Remove line item button
      if (e.target.classList.contains('remove-line-item-btn') || e.target.closest('.remove-line-item-btn')) {
        e.preventDefault();
        const row = e.target.closest('.line-item-row');
        if (row) row.remove();
        
        // Recalculate totals
        this.recalculateChangeOrderTotals();
      }
    });
    
    // Input changes in line items
    document.addEventListener('input', (e) => {
      if (e.target.closest('.line-item-row') && e.target.name.includes('amount')) {
        this.recalculateChangeOrderTotals();
      }
    });
    
    // Approve button
    document.addEventListener('click', (e) => {
      if (e.target.id === 'approve-change-order-btn' || e.target.closest('#approve-change-order-btn')) {
        e.preventDefault();
        this.approveChangeOrder();
      }
    });
    
    // Reject button
    document.addEventListener('click', (e) => {
      if (e.target.id === 'reject-change-order-btn' || e.target.closest('#reject-change-order-btn')) {
        e.preventDefault();
        this.rejectChangeOrder();
      }
    });
  }
  
  // Handle contract type change
  async handleContractTypeChange(selectElement) {
    const contractType = selectElement.value;
    const contractIdSelect = document.getElementById('contract_id');
    
    if (!contractIdSelect) return;
    
    // Clear existing options
    while (contractIdSelect.options.length > 1) {
      contractIdSelect.remove(1);
    }
    
    if (!contractType) {
      contractIdSelect.disabled = true;
      return;
    }
    
    try {
      contractIdSelect.disabled = true;
      
      // Determine which table to query based on contract type
      let table;
      let numberField;
      let titleField = 'title';
      
      if (contractType === 'prime_contract') {
        table = 'prime_contracts';
        numberField = 'contract_number';
      } else if (contractType === 'subcontract') {
        table = 'subcontracts';
        numberField = 'contract_number';
      } else if (contractType === 'purchase_order') {
        table = 'purchase_orders';
        numberField = 'po_number';
      } else {
        contractIdSelect.disabled = false;
        return;
      }
      
      // Fetch contracts of selected type
      const { data: contracts, error } = await supabase
        .from(table)
        .select(`id, ${numberField}, ${titleField}, company_id, companies(name)`)
        .eq('project_id', getProjectId());
      
      if (error) throw error;
      
      // Add contract options
      contracts.forEach(contract => {
        const option = document.createElement('option');
        option.value = contract.id;
        option.textContent = `${contract[numberField]} - ${contract[titleField]} (${contract.companies ? contract.companies.name : 'N/A'})`;
        option.dataset.companyId = contract.company_id;
        contractIdSelect.appendChild(option);
      });
      
      contractIdSelect.disabled = false;
    } catch (error) {
      console.error('Error loading contracts:', error);
      contractIdSelect.disabled = false;
    }
  }
  
  // Handle potential change selection
  async handlePotentialChangeSelection(selectElement) {
    const potentialChangeId = selectElement.value;
    
    if (!potentialChangeId) return;
    
    try {
      // Fetch potential change details
      const { data, error } = await supabase
        .from('potential_changes')
        .select('*')
        .eq('id', potentialChangeId)
        .single();
      
      if (error) throw error;
      
      // Populate form fields with data from potential change
      if (data) {
        const titleInput = document.getElementById('title');
        const descriptionTextarea = document.getElementById('description');
        const costImpactInput = document.getElementById('cost_impact');
        const scheduleImpactInput = document.getElementById('schedule_impact');
        
        if (titleInput && !titleInput.value) {
          titleInput.value = data.title;
        }
        
        if (descriptionTextarea && !descriptionTextarea.value) {
          descriptionTextarea.value = data.description || '';
        }
        
        if (costImpactInput && !costImpactInput.value) {
          costImpactInput.value = data.cost_impact || 0;
        }
        
        if (scheduleImpactInput && !scheduleImpactInput.value) {
          scheduleImpactInput.value = data.schedule_impact || 0;
        }
      }
    } catch (error) {
      console.error('Error loading potential change data:', error);
    }
  }
  
  // Add line item row to change order
  addLineItemRow() {
    const lineItemsContainer = document.getElementById('line-items-container');
    if (!lineItemsContainer) return;
    
    const rowIndex = document.querySelectorAll('.line-item-row').length;
    const newRow = document.createElement('div');
    newRow.className = 'line-item-row row g-3 mb-2 align-items-end border-bottom pb-2';
    newRow.innerHTML = `
      <div class="col-md-2">
        <label class="form-label">Cost Code</label>
        <input type="text" class="form-control" name="line_items[${rowIndex}][cost_code]">
      </div>
      <div class="col-md-6">
        <label class="form-label">Description</label>
        <input type="text" class="form-control" name="line_items[${rowIndex}][description]" required>
      </div>
      <div class="col-md-3">
        <label class="form-label">Amount</label>
        <div class="input-group">
          <span class="input-group-text">$</span>
          <input type="number" class="form-control" name="line_items[${rowIndex}][amount]" step="0.01" value="0">
        </div>
      </div>
      <div class="col-md-1">
        <button type="button" class="btn btn-danger remove-line-item-btn">
          <i class="bi bi-trash"></i>
        </button>
      </div>
    `;
    
    lineItemsContainer.appendChild(newRow);
    
    // Recalculate totals
    this.recalculateChangeOrderTotals();
  }
  
  // Recalculate change order totals
  recalculateChangeOrderTotals() {
    const form = document.getElementById(this.formDomId);
    if (!form) return;
    
    // Get all line items
    const lineItems = Array.from(form.querySelectorAll('.line-item-row'));
    
    // Calculate total amount
    let totalAmount = 0;
    
    lineItems.forEach(row => {
      const amount = parseFloat(row.querySelector('input[name*="amount"]').value) || 0;
      totalAmount += amount;
    });
    
    // Update cost impact field
    const costImpactInput = document.getElementById('cost_impact');
    if (costImpactInput) {
      costImpactInput.value = totalAmount.toFixed(2);
    }
    
    // Update summary on form
    const totalElement = document.getElementById('total-amount');
    if (totalElement) {
      totalElement.textContent = formatCurrency(totalAmount);
    }
  }
  
  // Approve change order
  async approveChangeOrder() {
    if (!this.currentRecord) return;
    
    try {
      // Show approval modal
      const approvalModal = new bootstrap.Modal(document.getElementById('approval-modal'));
      approvalModal.show();
      
      // Set up approval form submission
      const approvalForm = document.getElementById('approval-form');
      if (approvalForm) {
        approvalForm.onsubmit = async (e) => {
          e.preventDefault();
          
          const approvedDate = document.getElementById('approved_date').value;
          const approvalComments = document.getElementById('approval_comments').value;
          
          if (!approvedDate) {
            alert('Please enter the approval date');
            return;
          }
          
          try {
            // Update change order as approved
            const { data, error } = await supabase
              .from('change_orders')
              .update({
                status: 'approved',
                approved_date: approvedDate,
                approved_by: currentUser.id,
                approval_comments: approvalComments,
                updated_at: new Date().toISOString(),
                updated_by: currentUser.id
              })
              .eq('id', this.currentRecord.id)
              .select();
            
            if (error) throw error;
            
            // Update the budget if there is a cost impact
            if (this.currentRecord.cost_impact !== 0) {
              await this.updateBudgetWithChangeOrder(data[0]);
            }
            
            // Update current record
            this.currentRecord = data[0];
            
            // Update display
            this.displayRecordDetails(this.currentRecord);
            
            // Hide modal
            approvalModal.hide();
            
            // Show success message
            this.showSuccessMessage('Change order approved successfully');
          } catch (error) {
            console.error('Error approving change order:', error);
            alert('Error approving change order: ' + error.message);
          }
        };
      }
    } catch (error) {
      console.error('Error setting up approval modal:', error);
    }
  }
  
  // Reject change order
  async rejectChangeOrder() {
    if (!this.currentRecord) return;
    
    try {
      // Show rejection modal
      const rejectionModal = new bootstrap.Modal(document.getElementById('rejection-modal'));
      rejectionModal.show();
      
      // Set up rejection form submission
      const rejectionForm = document.getElementById('rejection-form');
      if (rejectionForm) {
        rejectionForm.onsubmit = async (e) => {
          e.preventDefault();
          
          const rejectionReason = document.getElementById('rejection_reason').value;
          
          if (!rejectionReason) {
            alert('Please enter a reason for rejection');
            return;
          }
          
          try {
            // Update change order as rejected
            const { data, error } = await supabase
              .from('change_orders')
              .update({
                status: 'rejected',
                rejection_reason: rejectionReason,
                updated_at: new Date().toISOString(),
                updated_by: currentUser.id
              })
              .eq('id', this.currentRecord.id)
              .select();
            
            if (error) throw error;
            
            // Update current record
            this.currentRecord = data[0];
            
            // Update display
            this.displayRecordDetails(this.currentRecord);
            
            // Hide modal
            rejectionModal.hide();
            
            // Show success message
            this.showSuccessMessage('Change order rejected');
          } catch (error) {
            console.error('Error rejecting change order:', error);
            alert('Error rejecting change order: ' + error.message);
          }
        };
      }
    } catch (error) {
      console.error('Error setting up rejection modal:', error);
    }
  }
  
  // Update budget with change order amounts
  async updateBudgetWithChangeOrder(changeOrder) {
    try {
      // Get change order line items
      const { data: lineItems, error: lineItemsError } = await supabase
        .from('change_order_line_items')
        .select('*')
        .eq('change_order_id', changeOrder.id);
      
      if (lineItemsError) throw lineItemsError;
      
      // Process each line item
      for (const item of lineItems) {
        // Check if there is a budget line for this cost code
        const { data: budgetLines, error: budgetError } = await supabase
          .from('budget_line_items')
          .select('*')
          .eq('project_id', getProjectId())
          .eq('cost_code', item.cost_code)
          .maybeSingle();
        
        if (budgetError) throw budgetError;
        
        if (budgetLines) {
          // Update existing budget line
          const { error: updateError } = await supabase
            .from('budget_line_items')
            .update({
              current_amount: budgetLines.current_amount + item.amount,
              updated_at: new Date().toISOString(),
              updated_by: currentUser.id
            })
            .eq('id', budgetLines.id);
          
          if (updateError) throw updateError;
        } else {
          // Create new budget line
          const { error: insertError } = await supabase
            .from('budget_line_items')
            .insert({
              project_id: getProjectId(),
              cost_code: item.cost_code,
              description: `Change Order #${changeOrder.change_order_number}: ${item.description}`,
              original_amount: item.amount,
              current_amount: item.amount,
              committed_amount: item.amount,
              actual_amount: 0,
              projected_amount: 0,
              created_at: new Date().toISOString(),
              created_by: currentUser.id
            });
          
          if (insertError) throw insertError;
        }
      }
    } catch (error) {
      console.error('Error updating budget with change order:', error);
      throw error;
    }
  }
  
  // Override to handle form submission with line items
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
      
      let changeOrderId;
      
      if (mode === 'edit') {
        const id = form.dataset.id;
        const { data, error } = await this.updateRecord(id, formData);
        
        if (error) throw error;
        changeOrderId = id;
      } else {
        const { data, error } = await this.createRecord(formData);
        
        if (error) throw error;
        changeOrderId = data.id;
      }
      
      // Process line items
      await this.processLineItems(changeOrderId, form);
      
      // Show success message
      this.showSuccessMessage(`Change order ${mode === 'edit' ? 'updated' : 'created'} successfully.`);
      
      // Close form and reload data
      this.closeForm();
      await this.loadData();
      
      appState.isLoading = false;
      this.showLoading(false);
    } catch (error) {
      console.error('Error submitting form:', error);
      this.showErrorMessage(`Failed to ${form.dataset.mode === 'edit' ? 'update' : 'create'} change order. ${error.message}`);
      appState.isLoading = false;
      this.showLoading(false);
    }
  }
  
  // Process line items from form
  async processLineItems(changeOrderId, form) {
    try {
      // Get line item inputs from form
      const lineItemRows = Array.from(form.querySelectorAll('.line-item-row'));
      
      if (lineItemRows.length === 0) return;
      
      // First delete existing line items for this change order
      await supabase
        .from('change_order_line_items')
        .delete()
        .eq('change_order_id', changeOrderId);
      
      // Process each line item
      const lineItemsData = lineItemRows.map(row => {
        const costCode = row.querySelector('input[name*="cost_code"]').value || null;
        const description = row.querySelector('input[name*="description"]').value || null;
        const amount = parseFloat(row.querySelector('input[name*="amount"]').value) || 0;
        
        return {
          change_order_id: changeOrderId,
          cost_code: costCode,
          description: description,
          amount: amount,
          created_at: new Date().toISOString()
        };
      });
      
      // Insert line items
      if (lineItemsData.length > 0) {
        const { error } = await supabase
          .from('change_order_line_items')
          .insert(lineItemsData);
        
        if (error) throw error;
      }
    } catch (error) {
      console.error('Error processing line items:', error);
      throw error;
    }
  }
  
  // Override to load line items when editing a change order
  async openForm(data = null) {
    // Call parent method to open form
    super.openForm(data);
    
    // Clear existing line items
    const lineItemsContainer = document.getElementById('line-items-container');
    if (lineItemsContainer) {
      lineItemsContainer.innerHTML = '';
    }
    
    // If editing an existing change order, load line items
    if (data) {
      await this.loadLineItems(data.id);
      
      // Set contract selection if applicable
      if (data.contract_type && data.contract_id) {
        const contractTypeSelect = document.getElementById('contract_type');
        const contractIdSelect = document.getElementById('contract_id');
        
        if (contractTypeSelect) {
          contractTypeSelect.value = data.contract_type;
          // Trigger change event to load contracts
          const event = new Event('change');
          contractTypeSelect.dispatchEvent(event);
          
          // Set contract ID after options are loaded
          if (contractIdSelect) {
            setTimeout(() => {
              contractIdSelect.value = data.contract_id;
            }, 500);
          }
        }
      }
      
      // Set company if applicable
      if (data.company_id) {
        const companySelect = document.getElementById('company_id');
        if (companySelect) {
          companySelect.value = data.company_id;
        }
      }
      
      // Set potential change if applicable
      if (data.potential_change_id) {
        const potentialChangeSelect = document.getElementById('potential_change_id');
        if (potentialChangeSelect) {
          potentialChangeSelect.value = data.potential_change_id;
        }
      }
    } else {
      // Add empty line item for new change order
      this.addLineItemRow();
      
      // Set default values for new change order
      const changeOrderNumberInput = document.getElementById('change_order_number');
      if (changeOrderNumberInput && !changeOrderNumberInput.value) {
        // Generate next change order number
        this.generateNextChangeOrderNumber().then(number => {
          changeOrderNumberInput.value = number;
        });
      }
    }
  }
  
  // Load line items for a change order
  async loadLineItems(changeOrderId) {
    try {
      const { data: lineItems, error } = await supabase
        .from('change_order_line_items')
        .select('*')
        .eq('change_order_id', changeOrderId)
        .order('id');
      
      if (error) throw error;
      
      if (lineItems && lineItems.length > 0) {
        // Add line item rows for each record
        lineItems.forEach(() => {
          this.addLineItemRow();
        });
        
        // Fill in the data
        const lineItemRows = document.querySelectorAll('.line-item-row');
        lineItems.forEach((item, index) => {
          if (index < lineItemRows.length) {
            const row = lineItemRows[index];
            
            row.querySelector('input[name*="cost_code"]').value = item.cost_code || '';
            row.querySelector('input[name*="description"]').value = item.description || '';
            row.querySelector('input[name*="amount"]').value = item.amount || 0;
          }
        });
        
        // Recalculate totals
        this.recalculateChangeOrderTotals();
      }
    } catch (error) {
      console.error('Error loading line items:', error);
      this.showErrorMessage('Failed to load line items. ' + error.message);
    }
  }
  
  // Generate next change order number
  async generateNextChangeOrderNumber() {
    try {
      // Get current max change order number
      const { data, error } = await supabase
        .from('change_orders')
        .select('change_order_number')
        .eq('project_id', getProjectId())
        .order('change_order_number', { ascending: false })
        .limit(1);
      
      if (error) throw error;
      
      // Parse number and increment
      let nextNumber = 1;
      if (data && data.length > 0 && data[0].change_order_number) {
        const currentNumber = parseInt(data[0].change_order_number.replace(/\D/g, ''), 10);
        if (!isNaN(currentNumber)) {
          nextNumber = currentNumber + 1;
        }
      }
      
      // Format with leading zeros
      return nextNumber.toString().padStart(3, '0');
    } catch (error) {
      console.error('Error generating change order number:', error);
      return 'TBD';
    }
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
      
      // Populate companies dropdown
      const companySelect = document.getElementById('company_id');
      if (companySelect) {
        // Clear existing options except the first one
        while (companySelect.options.length > 1) {
          companySelect.remove(1);
        }
        
        // Add company options
        companies.forEach(company => {
          const option = document.createElement('option');
          option.value = company.id;
          option.textContent = `${company.name} (${company.type})`;
          companySelect.appendChild(option);
        });
      }
      
      // Fetch potential changes for dropdown
      const { data: potentialChanges, error: pcError } = await supabase
        .from('potential_changes')
        .select('id, title, cost_impact, status')
        .eq('project_id', getProjectId())
        .neq('status', 'closed')
        .order('id', { ascending: false });
      
      if (pcError) throw pcError;
      
      // Populate potential changes dropdown
      const pcSelect = document.getElementById('potential_change_id');
      if (pcSelect) {
        // Clear existing options except the first one
        while (pcSelect.options.length > 1) {
          pcSelect.remove(1);
        }
        
        // Add potential change options
        potentialChanges.forEach(pc => {
          const option = document.createElement('option');
          option.value = pc.id;
          option.textContent = `PC #${pc.id} - ${pc.title} (${formatCurrency(pc.cost_impact || 0)})`;
          pcSelect.appendChild(option);
        });
      }
    } catch (error) {
      console.error('Error initializing related data:', error);
    }
  }
  
  // Override to customize the form data before submission
  getFormData(form) {
    const formData = super.getFormData(form);
    
    // Set default values for new change orders
    if (form.dataset.mode === 'create') {
      formData.status = formData.status || 'draft';
      formData.submitted_date = formData.submitted_date || new Date().toISOString().split('T')[0];
    }
    
    return formData;
  }
  
  // Override to customize how change order details are displayed
  updateDetailsContent(container, record) {
    // Call parent method for common fields
    super.updateDetailsContent(container, record);
    
    // Update change order-specific fields
    if (container) {
      // Change Order Number
      const coNumberElement = container.querySelector('.change-order-number');
      if (coNumberElement) {
        coNumberElement.textContent = `Change Order #${record.change_order_number}`;
      }
      
      // Title
      const titleElement = container.querySelector('.record-title');
      if (titleElement) {
        titleElement.textContent = record.title;
      }
      
      // Description
      const descriptionElement = container.querySelector('.change-order-description');
      if (descriptionElement && record.description) {
        descriptionElement.innerHTML = record.description.replace(/\n/g, '<br>');
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
          'rejected': 'status-rejected',
          'void': 'status-void'
        };
        
        statusElement.className = `record-status ${statusClasses[record.status] || ''}`;
      }
      
      // Cost Impact
      const costImpactElement = container.querySelector('.cost-impact');
      if (costImpactElement) {
        costImpactElement.textContent = formatCurrency(record.cost_impact || 0);
      }
      
      // Schedule Impact
      const scheduleImpactElement = container.querySelector('.schedule-impact');
      if (scheduleImpactElement) {
        if (record.schedule_impact) {
          scheduleImpactElement.textContent = `${record.schedule_impact} days`;
        } else {
          scheduleImpactElement.textContent = 'None';
        }
      }
      
      // Contract
      const contractElement = container.querySelector('.contract-info');
      if (contractElement) {
        if (record.contract_type && record.contract_id) {
          contractElement.textContent = `${record.contract_type.replace(/_/g, ' ')} #${record.contract_id}`;
        } else {
          contractElement.textContent = 'N/A';
        }
      }
      
      // Potential Change
      const potentialChangeElement = container.querySelector('.potential-change');
      if (potentialChangeElement) {
        if (record.potential_change_id) {
          potentialChangeElement.innerHTML = `<a href="./potential-changes.html?id=${record.potential_change_id}">PC #${record.potential_change_id}</a>`;
        } else {
          potentialChangeElement.textContent = 'N/A';
        }
      }
      
      // Dates & People
      this.updateDateElement(container, '.submitted-date', record.submitted_date);
      this.updateDateElement(container, '.approved-date', record.approved_date);
      this.updateDateElement(container, '.executed-date', record.executed_date);
      
      // Load line items
      this.loadLineItemDetails(record.id);
      
      // Show/hide approval buttons based on status
      this.updateApprovalButtons(record);
    }
  }
  
  // Load line item details for display
  async loadLineItemDetails(changeOrderId) {
    try {
      const lineItemsContainer = document.getElementById('line-items-details');
      if (!lineItemsContainer) return;
      
      lineItemsContainer.innerHTML = '<div class="loading text-center p-3"><div class="spinner-border spinner-border-sm text-primary me-2"></div> Loading line items...</div>';
      
      const { data: lineItems, error } = await supabase
        .from('change_order_line_items')
        .select('*')
        .eq('change_order_id', changeOrderId)
        .order('id');
      
      if (error) throw error;
      
      // Clear loading indicator
      lineItemsContainer.innerHTML = '';
      
      if (!lineItems || lineItems.length === 0) {
        lineItemsContainer.innerHTML = '<div class="no-data text-center p-3">No line items for this change order</div>';
        return;
      }
      
      // Create line items table
      const lineItemsTable = document.createElement('table');
      lineItemsTable.className = 'table';
      lineItemsTable.innerHTML = `
        <thead>
          <tr>
            <th>Cost Code</th>
            <th>Description</th>
            <th class="text-end">Amount</th>
          </tr>
        </thead>
        <tbody></tbody>
        <tfoot>
          <tr class="table-light">
            <th colspan="2" class="text-end">Total:</th>
            <th class="text-end"></th>
          </tr>
        </tfoot>
      `;
      
      const tbody = lineItemsTable.querySelector('tbody');
      
      // Calculate total
      let totalAmount = 0;
      
      // Add line item rows
      lineItems.forEach(item => {
        const row = document.createElement('tr');
        
        row.innerHTML = `
          <td>${item.cost_code || 'N/A'}</td>
          <td>${item.description || 'N/A'}</td>
          <td class="text-end">${formatCurrency(item.amount || 0)}</td>
        `;
        
        tbody.appendChild(row);
        
        // Update total
        totalAmount += item.amount || 0;
      });
      
      // Update total in footer
      const footerRow = lineItemsTable.querySelector('tfoot tr');
      footerRow.innerHTML = `
        <th colspan="2" class="text-end">Total:</th>
        <th class="text-end">${formatCurrency(totalAmount)}</th>
      `;
      
      lineItemsContainer.appendChild(lineItemsTable);
    } catch (error) {
      console.error('Error loading line item details:', error);
      const lineItemsContainer = document.getElementById('line-items-details');
      if (lineItemsContainer) {
        lineItemsContainer.innerHTML = `<div class="error text-danger p-3">Error loading line items: ${error.message}</div>`;
      }
    }
  }
  
  // Update approval buttons based on change order status
  updateApprovalButtons(record) {
    const actionsContainer = document.getElementById('approval-actions');
    if (!actionsContainer) return;
    
    // Clear existing content
    actionsContainer.innerHTML = '';
    
    // Show different buttons based on status
    if (record.status === 'submitted' || record.status === 'in_review') {
      // Check if user has permission to approve (owner, owner_rep, or general_contractor with proper role)
      if (currentUser.role === 'owner' || currentUser.role === 'owner_rep' || 
          (currentUser.role === 'general_contractor' && record.company_id !== currentUser.company_id)) {
        
        actionsContainer.innerHTML = `
          <button type="button" class="btn btn-success me-2" id="approve-change-order-btn">
            <i class="bi bi-check-circle me-1"></i> Approve Change Order
          </button>
          <button type="button" class="btn btn-danger" id="reject-change-order-btn">
            <i class="bi bi-x-circle me-1"></i> Reject Change Order
          </button>
        `;
      }
    } else if (record.status === 'approved') {
      // Show approved badge and maybe an "execute" button
      actionsContainer.innerHTML = `
        <div class="alert alert-success mb-0">
          <i class="bi bi-check-circle-fill me-2"></i>
          <strong>Approved on ${formatDate(record.approved_date)}</strong>
          ${record.approved_by ? ` by ${record.approved_by_name || 'User'}` : ''}
        </div>
      `;
    } else if (record.status === 'rejected') {
      // Show rejected badge with reason
      actionsContainer.innerHTML = `
        <div class="alert alert-danger mb-0">
          <i class="bi bi-x-circle-fill me-2"></i>
          <strong>Rejected</strong>
          ${record.rejection_reason ? `: ${record.rejection_reason}` : ''}
        </div>
      `;
    }
  }
}

// Initialize modules based on current page
const initCostModules = () => {
  // Determine which module to initialize based on current page
  const currentPath = window.location.pathname;
  
  if (currentPath.includes('/cost/budget-forecast.html')) {
    return new BudgetModule();
  } else if (currentPath.includes('/cost/invoicing.html')) {
    return new InvoicingModule();
  } else if (currentPath.includes('/cost/change-orders.html')) {
    return new ChangeOrderModule();
  }
  // Add more module initializations as needed
};

export default initCostModules;        scales: {
          y: {
            beginAtZero: true,
            ticks: {
              callback: function(value) {
                return formatCurrency(value);
              }
            }
          }
        },
        plugins: {
          tooltip: {
            callbacks: {
              label: function(context) {
                return context.dataset.label + ': ' + formatCurrency(context.raw);
              }
            }
          }
        }
      }
    });
  }
  
  // Initialize budget vs actual chart
  async initBudgetVsActualChart(canvas) {
    try {
      // Fetch budget summary data by division
      const { data, error } = await supabase.rpc('get_budget_summary_by_division', {
        p_project_id: getProjectId()
      });
      
      if (error) throw error;
      
      // Prepare chart data
      const labels = data.map(item => `Div ${item.csi_division}`);
      const budgetValues = data.map(item => item.current_amount);
      const actualValues = data.map(item => item.actual_amount);
      const varianceValues = data.map(item => item.current_amount - item.actual_amount);
      
      // Create chart
      const ctx = canvas.getContext('2d');
      new Chart(ctx, {
        type: 'line',
        data: {
          labels: labels,
          datasets: [
            {
              label: 'Budget',
              data: budgetValues,
              backgroundColor: 'rgba(75, 192, 192, 0.2)',
              borderColor: 'rgba(75, 192, 192, 1)',
              borderWidth: 2,
              fill: false,
              tension: 0.1
            },
            {
              label: 'Actual',
              data: actualValues,
              backgroundColor: 'rgba(255, 99, 132, 0.2)',
              borderColor: 'rgba(255, 99, 132, 1)',
              borderWidth: 2,
              fill: false,
              tension: 0.1
            },
            {
              label: 'Variance',
              data: varianceValues,
              backgroundColor: 'rgba(54, 162, 235, 0.2)',
              borderColor: 'rgba(54, 162, 235, 1)',
              borderWidth: 2,
              fill: false,
              tension: 0.1
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            y: {
              ticks: {
                callback: function(value) {
                  return formatCurrency(value);
                }
              }
            }
          },
          plugins: {
            tooltip: {
              callbacks: {
                label: function(context) {
                  return context.dataset.label + ': ' + formatCurrency(context.raw);
                }
              }
            }
          }
        }
      });
    } catch (error) {
      console.error('Error initializing budget vs actual chart:', error);
    }
  }
  
  // Update CSI subdivisions based on selected division
  async updateCsiSubdivisions(divisionNumber) {
    const subdivisionSelect = document.getElementById('csi_subdivision');
    if (!subdivisionSelect) return;
    
    // Clear existing options except the first one
    while (subdivisionSelect.options.length > 1) {
      subdivisionSelect.remove(1);
    }
    
    // If no division selected, disable subdivision select
    if (!divisionNumber) {
      subdivisionSelect.disabled = true;
      return;
    }
    
    try {
      subdivisionSelect.disabled = true;
      
      // Fetch subdivisions for selected division
      const { data: subdivisions, error } = await supabase
        .from('csi_subdivisions')
        .select('subdivision_number, subdivision_name')
        .eq('division_id', divisionNumber)
        .order('subdivision_number');
      
      if (error) throw error;
      
      // Add subdivision options
      subdivisions.forEach(sub => {
        const option = document.createElement('option');
        option.value = sub.subdivision_number;
        option.textContent = `${sub.subdivision_number} - ${sub.subdivision_name}`;
        subdivisionSelect.appendChild(option);
      });
      
      // Enable subdivision select if there are options
      subdivisionSelect.disabled = subdivisions.length === 0;
    } catch (error) {
      console.error('Error updating CSI subdivisions:', error);
    }
  }
  
  // Override to customize how budget details are displayed
  updateDetailsContent(container, record) {
    // Call parent method for common fields
    super.updateDetailsContent(container, record);
    
    // Update budget-specific fields
    if (container) {
      // Cost Code
      const costCodeElement = container.querySelector('.cost-code');
      if (costCodeElement) {
        costCodeElement.textContent = record.cost_code || 'N/A';
      }
      
      // Description
      const descriptionElement = container.querySelector('.budget-description');
      if (descriptionElement) {
        descriptionElement.textContent = record.description || 'N/A';
      }
      
      // CSI Division
      const csiDivisionElement = container.querySelector('.csi-division');
      if (csiDivisionElement) {
        if (record.csi_division) {
          let csiText = record.csi_division;
          if (record.csi_subdivision) {
            csiText += `.${record.csi_subdivision}`;
          }
          csiDivisionElement.textContent = csiText;
        } else {
          csiDivisionElement.textContent = 'N/A';
        }
      }
      
      // Budget amounts
      this.updateAmountElement(container, '.original-amount', record.original_amount);
      this.updateAmountElement(container, '.current-amount', record.current_amount);
      this.updateAmountElement(container, '.committed-amount', record.committed_amount);
      this.updateAmountElement(container, '.actual-amount', record.actual_amount);
      this.updateAmountElement(container, '.projected-amount', record.projected_amount);
      
      // Variance
      const varianceElement = container.querySelector('.variance-amount');
      if (varianceElement) {
        const variance = record.variance_amount;
        varianceElement.textContent = formatCurrency(variance);
        
        // Add color class based on value
        if (variance < 0) {
          varianceElement.classList.add('text-danger');
          varianceElement.classList.remove('text-success');
        } else {
          varianceElement.classList.add('text-success');
          varianceElement.classList.remove('text-danger');
        }
      }
      
      // Notes
      const notesElement = container.querySelector('.budget-notes');
      if (notesElement) {
        if (record.notes) {
          notesElement.innerHTML = record.notes.replace(/\n/g, '<br>');
        } else {
          notesElement.innerHTML = '<em>No notes</em>';
        }
      }
      
      // Initialize details chart
      const detailsChartCanvas = document.getElementById('budget-details-chart');
      if (detailsChartCanvas) {
        this.initBudgetDetailsChart(detailsChartCanvas);
      }
      
      // Load related transactions
      this.loadRelatedTransactions(record.id);
    }
  }
  
  // Helper method to update amount elements with proper formatting
  updateAmountElement(container, selector, amount) {
    const element = container.querySelector(selector);
    if (element) {
      element.textContent = formatCurrency(amount || 0);
    }
  }
  
  // Load related transactions (commits, actuals, changes)
  async loadRelatedTransactions(budgetId) {
    try {
      const transactionsContainer = document.getElementById('related-transactions');
      if (!transactionsContainer) return;
      
      transactionsContainer.innerHTML = '<div class="loading text-center p-3"><div class="spinner-border spinner-border-sm text-primary me-2"></div> Loading transactions...</div>';
      
      // Fetch related transactions
      const { data, error } = await supabase.rpc('get_budget_transactions', {
        p_budget_id: budgetId
      });
      
      if (error) throw error;
      
      // Clear loading indicator
      transactionsContainer.innerHTML = '';
      
      if (!data || data.length === 0) {
        transactionsContainer.innerHTML = '<div class="no-data text-center p-3">No transactions found for this budget line</div>';
        return;
      }
      
      // Create transactions table
      const transactionsTable = document.createElement('table');
      transactionsTable.className = 'table table-sm';
      transactionsTable.innerHTML = `
        <thead>
          <tr>
            <th>Date</th>
            <th>Type</th>
            <th>Reference</th>
            <th>Description</th>
            <th class="text-end">Amount</th>
          </tr>
        </thead>
        <tbody></tbody>
      `;
      
      const tbody = transactionsTable.querySelector('tbody');
      
      // Add transaction rows
      data.forEach(transaction => {
        const row = document.createElement('tr');
        
        // Determine link based on transaction type
        let referenceLink = '#';
        if (transaction.transaction_type === 'contract') {
          referenceLink = `../contracts/subcontracts.html?id=${transaction.reference_id}`;
        } else if (transaction.transaction_type === 'invoice') {
          referenceLink = `./invoicing.html?id=${transaction.reference_id}`;
        } else if (transaction.transaction_type === 'change_order') {
          referenceLink = `./change-orders.html?id=${transaction.reference_id}`;
        } else if (transaction.transaction_type === 'direct_cost') {
          referenceLink = `./direct-costs.html?id=${transaction.reference_id}`;
        }
        
        row.innerHTML = `
          <td>${formatDate(transaction.transaction_date)}</td>
          <td>${this.formatTransactionType(transaction.transaction_type)}</td>
          <td><a href="${referenceLink}">${transaction.reference_number}</a></td>
          <td>${transaction.description || ''}</td>
          <td class="text-end ${transaction.amount < 0 ? 'text-danger' : ''}">${formatCurrency(transaction.amount)}</td>
        `;
        
        tbody.appendChild(row);
      });
      
      transactionsContainer.appendChild(transactionsTable);
    } catch (error) {
      console.error('Error loading related transactions:', error);
      const transactionsContainer = document.getElementById('related-transactions');
      if (transactionsContainer) {
        transactionsContainer.innerHTML = `<div class="error text-danger p-3">Error loading transactions: ${error.message}</div>`;
      }
    }
  }
  
  // Format transaction type for display
  formatTransactionType(type) {
    switch (type) {
      case 'contract': return 'Contract';
      case 'invoice': return 'Invoice';
      case 'change_order': return 'Change Order';
      case 'direct_cost': return 'Direct Cost';
      case 'budget_adjustment': return 'Budget Adjustment';
      default: return type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    }
  }
  
  // Initialize related data for dropdowns
  async initRelatedData() {
    try {
      // Fetch CSI divisions for dropdown
      const { data: divisions, error: divError } = await supabase
        .from('csi_divisions')
        .select('division_number, division_name')
        .order('division_number');
      
      if (divError) throw divError;
      
      // Populate CSI Division dropdown
      const divisionSelect = document.getElementById('csi_division');
      if (divisionSelect) {
        // Clear existing options except the first one
        while (divisionSelect.options.length > 1) {
          divisionSelect.remove(1);
        }
        
        // Add division options
        divisions.forEach(division => {
          const option = document.createElement('option');
          option.value = division.division_number;
          option.textContent = `${division.division_number} - ${division.division_name}`;
          divisionSelect.appendChild(option);
        });
      }
      
      // Fetch cost codes for dropdown
      const { data: costCodes, error: ccError } = await supabase
        .from('cost_codes')
        .select('code, description')
        .eq('project_id', getProjectId())
        .eq('active', true)
        .order('code');
      
      if (ccError) throw ccError;
      
      // Populate Cost Code dropdown
      const costCodeSelect = document.getElementById('cost_code');
      if (costCodeSelect) {
        // Clear existing options except the first one
        while (costCodeSelect.options.length > 1) {
          costCodeSelect.remove(1);
        }
        
        // Add cost code options
        costCodes.forEach(cc => {
          const option = document.createElement('option');
          option.value = cc.code;
          option.textContent = `${cc.code} - ${cc.description}`;
          costCodeSelect.appendChild(option);
        });
      }
    } catch (error) {
      console.error('Error initializing related data:', error);
    }
  }
  
  // Override to customize the form data before submission
  getFormData(form) {
    const formData = super.getFormData(form);
    
    // Set default values for new budget items
    if (form.dataset.mode === 'create') {
      formData.original_amount = formData.original_amount || 0;
      formData.current_amount = formData.current_amount || formData.original_amount;
      formData.committed_amount = formData.committed_amount || 0;
      formData.actual_amount = formData.actual_amount || 0;
      formData.projected_amount = formData.projected_amount || 0;
    }
    
    return formData;
  }
}

// Invoicing Module (AIA G702/G703)
class InvoicingModule extends CrudModule {
  constructor() {
    super({
      table: 'invoices',
      primaryKey: 'id',
      columns: [
        { data: 'invoice_number', title: 'Invoice #' },
        { data: 'title', title: 'Title' },
        { 
          data: 'company_id', 
          title: 'Company',
          render: (data, type, row) => {
            return row.company_name || 'Loading...';
          }
        },
        { 
          data: 'issue_date', 
          title: 'Issue Date',
          render: (data) => formatDate(data)
        },
        { 
          data: 'due_date', 
          title: 'Due Date',
          render: (data) => formatDate(data)
        },
        { 
          data: 'current_payment_due', 
          title: 'Amount Due',
          render: (data) => formatCurrency(data)
        },
        { 
          data: 'status', 
          title: 'Status',
          render: (data) => {
            const statusClasses = {
              'draft': 'badge bg-secondary',
              'submitted': 'badge bg-primary',
              'approved': 'badge bg-success',
              'paid': 'badge bg-info',
              'rejected': 'badge bg-danger'
            };
            return `<span class="${statusClasses[data] || 'badge bg-secondary'}">${data.toUpperCase()}</span>`;
          }
        },
        { 
          data: 'paid', 
          title: 'Paid',
          render: (data) => data ? '<i class="bi bi-check-circle-fill text-success"></i>' : '<i class="bi bi-x-circle text-danger"></i>'
        }
      ],
      tableDomId: 'invoices-table',
      formDomId: 'invoice-form',
      detailsDomId: 'invoice-details',
      module: 'cost',
      recordType: 'invoice',
      defaultSort: { column: 'issue_date', direction: 'desc' },
      relations: [
        { table: 'companies', fields: ['name'], as: 'company' }
      ]
    });
    
    // Add custom methods and event listeners
    this.initCustomEventListeners();
  }
  
  // Initialize custom event listeners
  initCustomEventListeners() {
    // Contract type selection
    document.addEventListener('change', (e) => {
      if (e.target.id === 'contract_type') {
        this.handleContractTypeChange(e.target);
      }
    });
    
    // Add line item button
    document.addEventListener('click', (e) => {
      if (e.target.classList.contains('add-line-item-btn') || e.target.closest('.add-line-item-btn')) {
        e.preventDefault();
        this.addLineItemRow();
      }
      
      // Remove line item button
      if (e.target.classList.contains('remove-line-item-btn') || e.target.closest('.remove-line-item-btn')) {
        e.preventDefault();
        const row = e.target.closest('.line-item-row');
        if (row) row.remove();
        
        // Recalculate totals
        this.recalculateInvoiceTotals();
      }
    });
    
    // Input changes in line items
    document.addEventListener('input', (e) => {
      if (e.target.closest('.line-item-row') && 
          (e.target.name.includes('scheduled_value') || 
           e.target.name.includes('previous_work') || 
           e.target.name.includes('current_work') || 
           e.target.name.includes('materials_stored'))) {
        this.recalculateInvoiceTotals();
      }
    });
    
    // Mark as paid button
    document.addEventListener('click', (e) => {
      if (e.target.id === 'mark-as-paid-btn' || e.target.closest('#mark-as-paid-btn')) {
        e.preventDefault();
        this.markInvoiceAsPaid();
      }
    });
  }
  
  // Handle contract type change
  async handleContractTypeChange(selectElement) {
    const contractType = selectElement.value;
    const contractIdSelect = document.getElementById('contract_id');
    
    if (!contractIdSelect) return;
    
    // Clear existing options
    while (contractIdSelect.options.length > 1) {
      contractIdSelect.remove(1);
    }
    
    if (!contractType) {
      contractIdSelect.disabled = true;
      return;
    }
    
    try {
      contractIdSelect.disabled = true;
      
      // Determine which table to query based on contract type
      let table;
      let numberField;
      let titleField = 'title';
      
      if (contractType === 'prime_contract') {
        table = 'prime_contracts';
        numberField = 'contract_number';
      } else if (contractType === 'subcontract') {
        table = 'subcontracts';
        numberField = 'contract_number';
      } else if (contractType === 'purchase_order') {
        table = 'purchase_orders';
        numberField = 'po_number';
      } else {
        contractIdSelect.disabled = false;
        return;
      }
      
      // Fetch contracts of selected type
      const { data: contracts, error } = await supabase
        .from(table)
        .select(`id, ${numberField}, ${titleField}, company_id, companies(name)`)
        .eq('project_id', getProjectId());
      
      if (error) throw error;
      
      // Add contract options
      contracts.forEach(contract => {
        const option = document.createElement('option');
        option.value = contract.id;
        option.textContent = `${contract[numberField]} - ${contract[titleField]} (${contract.companies ? contract.companies.name : 'N/A'})`;
        option.dataset.companyId = contract.company_id;
        contractIdSelect.appendChild(option);
      });
      
      contractIdSelect.disabled = false;
    } catch (error) {
      console.error('Error loading contracts:', error);
      contractIdSelect.disabled = false;
    }
  }
  
  // Add line item row to invoice
  addLineItemRow() {
    const lineItemsContainer = document.getElementById('line-items-container');
    if (!lineItemsContainer) return;
    
    const rowIndex = document.querySelectorAll('.line-item-row').length;
    const newRow = document.createElement('div');
    newRow.className = 'line-item-row row g-3 mb-2 align-items-end border-bottom pb-2';
    newRow.innerHTML = `
      <div class="col-md-2">
        <label class="form-label">Cost Code</label>
        <input type="text" class="form-control" name="line_items[${rowIndex}][cost_code]">
      </div>
      <div class="col-md-3">
        <label class="form-label">Description</label>
        <input type="text" class="form-control" name="line_items[${rowIndex}][description]" required>
      </div>
      <div class="col-md-1">
        <label class="form-label">Scheduled Value</label>
        <input type="number" class="form-control" name="line_items[${rowIndex}][scheduled_value]" step="0.01" min="0" value="0">
      </div>
      <div class="col-md-1">
        <label class="form-label">Previous Work</label>
        <input type="number" class="form-control" name="line_items[${rowIndex}][previous_work_completed]" step="0.01" min="0" value="0">
      </div>
      <div class="col-md-1">
        <label class="form-label">Current Work</label>
        <input type="number" class="form-control" name="line_items[${rowIndex}][current_work_completed]" step="0.01" min="0" value="0">
      </div>
      <div class="col-md-1">
        <label class="form-label">Materials</label>
        <input type="number" class="form-control" name="line_items[${rowIndex}][materials_stored]" step="0.01" min="0" value="0">
      </div>
      <div class="col-md-2">
        <label class="form-label">Retainage (%)</label>
        <input type="number" class="form-control" name="line_items[${rowIndex}][retainage_percentage]" step="0.01" min="0" max="100" value="10">
      </div>
      <div class="col-md-1">
        <button type="button" class="btn btn-danger remove-line-item-btn">
          <i class="bi bi-trash"></i>
        </button>
      </div>
    `;
    
    lineItemsContainer.appendChild(newRow);
    
    // Recalculate totals
    this.recalculateInvoiceTotals();
  }
  
  // Recalculate invoice totals
  recalculateInvoiceTotals() {
    const form = document.getElementById(this.formDomId);
    if (!form) return;
    
    // Get all line items
    const lineItems = Array.from(form.querySelectorAll('.line-item-row'));
    
    // Calculate totals
    let totalScheduledValue = 0;
    let totalPreviousWork = 0;
    let totalCurrentWork = 0;
    let totalMaterialsStored = 0;
    let totalCompletedAndStored = 0;
    let totalRetainage = 0;
    
    lineItems.forEach(row => {
      const scheduledValue = parseFloat(row.querySelector('input[name*="scheduled_value"]').value) || 0;
      const previousWork = parseFloat(row.querySelector('input[name*="previous_work_completed"]').value) || 0;
      const currentWork = parseFloat(row.querySelector('input[name*="current_work_completed"]').value) || 0;
      const materialsStored = parseFloat(row.querySelector('input[name*="materials_stored"]').value) || 0;
      const retainagePercentage = parseFloat(row.querySelector('input[name*="retainage_percentage"]').value) || 0;
      
      const completedAndStored = previousWork + currentWork + materialsStored;
      const retainage = (completedAndStored * retainagePercentage) / 100;
      
      totalScheduledValue += scheduledValue;
      totalPreviousWork += previousWork;
      totalCurrentWork += currentWork;
      totalMaterialsStored += materialsStored;
      totalCompletedAndStored += completedAndStored;
      totalRetainage += retainage;
    });
    
    // Update summary fields
    const retainagePercentage = document.getElementById('retainage_percentage');
    const retainageAmount = document.getElementById('retainage_amount');
    const totalEarnedLessRetainage = document.getElementById('total_earned_less_retainage');
    const lessPreviousCertificates = document.getElementById('less_previous_certificates');
    const currentPaymentDue = document.getElementById('current_payment_due');
    
    if (retainageAmount) retainageAmount.value = totalRetainage.toFixed(2);
    
    if (totalEarnedLessRetainage) {
      const earnedLessRetainage = totalCompletedAndStored - totalRetainage;
      totalEarnedLessRetainage.value = earnedLessRetainage.toFixed(2);
    }
    
    if (lessPreviousCertificates) lessPreviousCertificates.value = totalPreviousWork.toFixed(2);
    
    if (currentPaymentDue && totalEarnedLessRetainage && lessPreviousCertificates) {
      const earnedLessRetainage = parseFloat(totalEarnedLessRetainage.value) || 0;
      const previousCertificates = parseFloat(lessPreviousCertificates.value) || 0;
      const payment = earnedLessRetainage - previousCertificates;
      
      currentPaymentDue.value = payment.toFixed(2);
    }
    
    // Update total on form
    const formSummary = document.getElementById('invoice-summary');
    if (formSummary) {
      const scheduledValueEl = formSummary.querySelector('.total-scheduled-value');
      const previousWorkEl = formSummary.querySelector('.total-previous-work');
      const currentWorkEl = formSummary.querySelector('.total-current-work');
      const materialsStoredEl = formSummary.querySelector('.total-materials-stored');
      const completedAndStoredEl = formSummary.querySelector('.total-completed-and-stored');
      const percentCompleteEl = formSummary.querySelector('.total-percent-complete');
      const balanceToFinishEl = formSummary.querySelector('.total-balance-to-finish');
      const retainageEl = formSummary.querySelector('.total-retainage');
      
      if (scheduledValueEl) scheduledValueEl.textContent = formatCurrency(totalScheduledValue);
      if (previousWorkEl) previousWorkEl.textContent = formatCurrency(totalPreviousWork);
      if (currentWorkEl) currentWorkEl.textContent = formatCurrency(totalCurrentWork);
      if (materialsStoredEl) materialsStoredEl.textContent = formatCurrency(totalMaterialsStored);
      if (completedAndStoredEl) completedAndStoredEl.textContent = formatCurrency(totalCompletedAndStored);
      
      if (percentCompleteEl && totalScheduledValue > 0) {
        const percentComplete = (totalCompletedAndStored / totalScheduledValue) * 100;
        percentCompleteEl.textContent = percentComplete.toFixed(2) + '%';
      } else if (percentCompleteEl) {
        percentCompleteEl.textContent = '0%';
      }
      
      if (balanceToFinishEl) {
        const balanceToFinish = totalScheduledValue - totalCompletedAndStored;
        balanceToFinishEl.textContent = formatCurrency(balanceToFinish);
      }
      
      if (retainageEl) retainageEl.textContent = formatCurrency(totalRetainage);
    }
  }
  
  // Mark invoice as paid
  async markInvoiceAsPaid() {
    if (!this.currentRecord) return;
    
    try {
      // Show payment modal
      const paymentModal = new bootstrap.Modal(document.getElementById('payment-modal'));
      paymentModal.show();
      
      // Set up payment form submission
      const paymentForm = document.getElementById('payment-form');
      if (paymentForm) {
        paymentForm.onsubmit = async (e) => {
          e.preventDefault();
          
          const paidDate = document.getElementById('paid_date').value;
          const checkNumber = document.getElementById('check_number').value;
          
          if (!paidDate) {
            alert('Please enter the payment date');
            return;
          }
          
          try {
            // Update invoice as paid
            const { data, error } = await supabase
              .from('invoices')
              .update({
                paid: true,
                paid_date: paidDate,
                check_number: checkNumber,
                status: 'paid',
                updated_at: new Date().toISOString(),
                updated_by: currentUser.id
              })
              .eq('id', this.currentRecord.id)
              .select();
            
            if (error) throw error;
            
            // Update current record
            this.currentRecord = data[0];
            
            // Update display
            this.displayRecordDetails(this.currentRecord);
            
            // Hide modal
            paymentModal.hide();
            
            // Show success message
            this.showSuccessMessage('Invoice marked as paid successfully');
          } catch (error) {
            console.error('Error marking invoice as paid:', error);
            alert('Error marking invoice as paid: ' + error.message);
          }
        };
      }
    } catch (error) {
      console.error('Error setting up payment modal:', error);
    }
  }
  
  // Override to handle form submission with line items
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
      
      let invoiceId;import CrudModule from '../components/crud.js';
import { supabase } from '../../../supabase/init.js';
import { currentUser } from '../auth.js';
import { formatDate, formatCurrency } from '../app.js';

// Budget and Forecast Module
class BudgetModule extends CrudModule {
  constructor() {
    super({
      table: 'budget_line_items',
      primaryKey: 'id',
      columns: [
        { data: 'cost_code', title: 'Cost Code' },
        { data: 'description', title: 'Description' },
        { 
          data: 'csi_division', 
          title: 'CSI Division',
          render: (data, type, row) => {
            return row.csi_subdivision ? 
              `${data}.${row.csi_subdivision}` : 
              data || '';
          }
        },
        { 
          data: 'original_amount', 
          title: 'Original Budget',
          render: (data) => formatCurrency(data)
        },
        { 
          data: 'current_amount', 
          title: 'Current Budget',
          render: (data) => formatCurrency(data)
        },
        { 
          data: 'committed_amount', 
          title: 'Committed',
          render: (data) => formatCurrency(data)
        },
        { 
          data: 'actual_amount', 
          title: 'Actual',
          render: (data) => formatCurrency(data)
        },
        { 
          data: 'projected_amount', 
          title: 'Projected',
          render: (data) => formatCurrency(data || 0)
        },
        { 
          data: 'variance_amount', 
          title: 'Variance',
          render: (data) => {
            const color = data < 0 ? 'text-danger' : 'text-success';
            return `<span class="${color}">${formatCurrency(data)}</span>`;
          }
        }
      ],
      tableDomId: 'budget-table',
      formDomId: 'budget-form',
      detailsDomId: 'budget-details',
      module: 'cost',
      recordType: 'budget_line_item',
      defaultSort: { column: 'cost_code', direction: 'asc' }
    });
    
    // Add custom methods and event listeners
    this.initCustomEventListeners();
  }
  
  // Initialize custom event listeners
  initCustomEventListeners() {
    // Budget summary chart
    const chartCanvas = document.getElementById('budget-summary-chart');
    if (chartCanvas) {
      this.initBudgetSummaryChart(chartCanvas);
    }
    
    // Budget details chart
    const detailsChartCanvas = document.getElementById('budget-details-chart');
    if (detailsChartCanvas) {
      this.initBudgetDetailsChart(detailsChartCanvas);
    }
    
    // Budget vs Actual chart
    const budgetVsActualCanvas = document.getElementById('budget-vs-actual-chart');
    if (budgetVsActualCanvas) {
      this.initBudgetVsActualChart(budgetVsActualCanvas);
    }
    
    // CSI Division selector
    const csiDivisionSelect = document.getElementById('csi_division');
    if (csiDivisionSelect) {
      csiDivisionSelect.addEventListener('change', () => {
        this.updateCsiSubdivisions(csiDivisionSelect.value);
      });
    }
  }
  
  // Initialize budget summary chart
  async initBudgetSummaryChart(canvas) {
    try {
      // Fetch budget summary data by division
      const { data, error } = await supabase.rpc('get_budget_summary_by_division', {
        p_project_id: getProjectId()
      });
      
      if (error) throw error;
      
      // Prepare chart data
      const labels = data.map(item => `Div ${item.csi_division}`);
      const originalBudget = data.map(item => item.original_amount);
      const currentBudget = data.map(item => item.current_amount);
      const actualAmount = data.map(item => item.actual_amount);
      const projectedAmount = data.map(item => item.projected_amount);
      
      // Create chart
      const ctx = canvas.getContext('2d');
      new Chart(ctx, {
        type: 'bar',
        data: {
          labels: labels,
          datasets: [
            {
              label: 'Original Budget',
              data: originalBudget,
              backgroundColor: 'rgba(54, 162, 235, 0.2)',
              borderColor: 'rgba(54, 162, 235, 1)',
              borderWidth: 1
            },
            {
              label: 'Current Budget',
              data: currentBudget,
              backgroundColor: 'rgba(75, 192, 192, 0.2)',
              borderColor: 'rgba(75, 192, 192, 1)',
              borderWidth: 1
            },
            {
              label: 'Actual',
              data: actualAmount,
              backgroundColor: 'rgba(255, 99, 132, 0.2)',
              borderColor: 'rgba(255, 99, 132, 1)',
              borderWidth: 1
            },
            {
              label: 'Projected',
              data: projectedAmount,
              backgroundColor: 'rgba(255, 206, 86, 0.2)',
              borderColor: 'rgba(255, 206, 86, 1)',
              borderWidth: 1
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            y: {
              beginAtZero: true,
              ticks: {
                callback: function(value) {
                  return formatCurrency(value);
                }
              }
            }
          },
          plugins: {
            tooltip: {
              callbacks: {
                label: function(context) {
                  return context.dataset.label + ': ' + formatCurrency(context.raw);
                }
              }
            }
          }
        }
      });
    } catch (error) {
      console.error('Error initializing budget summary chart:', error);
    }
  }
  
  // Initialize budget details chart for a specific line item
  initBudgetDetailsChart(canvas) {
    if (!this.currentRecord) return;
    
    const record = this.currentRecord;
    
    // Prepare chart data
    const data = {
      labels: ['Budget Breakdown'],
      datasets: [
        {
          label: 'Original Budget',
          data: [record.original_amount],
          backgroundColor: 'rgba(54, 162, 235, 0.2)',
          borderColor: 'rgba(54, 162, 235, 1)',
          borderWidth: 1
        },
        {
          label: 'Committed',
          data: [record.committed_amount],
          backgroundColor: 'rgba(153, 102, 255, 0.2)',
          borderColor: 'rgba(153, 102, 255, 1)',
          borderWidth: 1
        },
        {
          label: 'Actual',
          data: [record.actual_amount],
          backgroundColor: 'rgba(255, 99, 132, 0.2)',
          borderColor: 'rgba(255, 99, 132, 1)',
          borderWidth: 1
        },
        {
          label: 'Projected',
          data: [record.projected_amount || 0],
          backgroundColor: 'rgba(255, 206, 86, 0.2)',
          borderColor: 'rgba(255, 206, 86, 1)',
          borderWidth: 1
        }
      ]
    };
    
    // Create chart
    const ctx = canvas.getContext('2d');
    new Chart(ctx, {
      type: 'bar',
      data: data,
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {