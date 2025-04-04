-- Create triggers for updated_at timestamps
-- Apply timestamp triggers to all tables that have updated_at column

-- Projects
CREATE TRIGGER set_timestamp
BEFORE UPDATE ON projects
FOR EACH ROW
EXECUTE FUNCTION trigger_set_timestamp();

-- Companies
CREATE TRIGGER set_timestamp
BEFORE UPDATE ON companies
FOR EACH ROW
EXECUTE FUNCTION trigger_set_timestamp();

-- Users
CREATE TRIGGER set_timestamp
BEFORE UPDATE ON users
FOR EACH ROW
EXECUTE FUNCTION trigger_set_timestamp();

-- User Permissions
CREATE TRIGGER set_timestamp
BEFORE UPDATE ON user_permissions
FOR EACH ROW
EXECUTE FUNCTION trigger_set_timestamp();

-- Comments
CREATE TRIGGER set_timestamp
BEFORE UPDATE ON comments
FOR EACH ROW
EXECUTE FUNCTION trigger_set_timestamp();

-- Attachments
CREATE TRIGGER set_timestamp
BEFORE UPDATE ON attachments
FOR EACH ROW
EXECUTE FUNCTION trigger_set_timestamp();

-- Deadlines
CREATE TRIGGER set_timestamp
BEFORE UPDATE ON deadlines
FOR EACH ROW
EXECUTE FUNCTION trigger_set_timestamp();

-- Qualified Bidders
CREATE TRIGGER set_timestamp
BEFORE UPDATE ON qualified_bidders
FOR EACH ROW
EXECUTE FUNCTION trigger_set_timestamp();

-- Bid Packages
CREATE TRIGGER set_timestamp
BEFORE UPDATE ON bid_packages
FOR EACH ROW
EXECUTE FUNCTION trigger_set_timestamp();

-- Bid Package Bidders
CREATE TRIGGER set_timestamp
BEFORE UPDATE ON bid_package_bidders
FOR EACH ROW
EXECUTE FUNCTION trigger_set_timestamp();

-- Bid Manuals
CREATE TRIGGER set_timestamp
BEFORE UPDATE ON bid_manuals
FOR EACH ROW
EXECUTE FUNCTION trigger_set_timestamp();

-- RFIs
CREATE TRIGGER set_timestamp
BEFORE UPDATE ON rfis
FOR EACH ROW
EXECUTE FUNCTION trigger_set_timestamp();

-- Submittals
CREATE TRIGGER set_timestamp
BEFORE UPDATE ON submittals
FOR EACH ROW
EXECUTE FUNCTION trigger_set_timestamp();

-- Drawings
CREATE TRIGGER set_timestamp
BEFORE UPDATE ON drawings
FOR EACH ROW
EXECUTE FUNCTION trigger_set_timestamp();

-- Specifications
CREATE TRIGGER set_timestamp
BEFORE UPDATE ON specifications
FOR EACH ROW
EXECUTE FUNCTION trigger_set_timestamp();

-- Permits
CREATE TRIGGER set_timestamp
BEFORE UPDATE ON permits
FOR EACH ROW
EXECUTE FUNCTION trigger_set_timestamp();

-- Meeting Minutes
CREATE TRIGGER set_timestamp
BEFORE UPDATE ON meeting_minutes
FOR EACH ROW
EXECUTE FUNCTION trigger_set_timestamp();

-- Transmittals
CREATE TRIGGER set_timestamp
BEFORE UPDATE ON transmittals
FOR EACH ROW
EXECUTE FUNCTION trigger_set_timestamp();

-- Daily Reports
CREATE TRIGGER set_timestamp
BEFORE UPDATE ON daily_reports
FOR EACH ROW
EXECUTE FUNCTION trigger_set_timestamp();

-- Photos
CREATE TRIGGER set_timestamp
BEFORE UPDATE ON photos
FOR EACH ROW
EXECUTE FUNCTION trigger_set_timestamp();

-- Schedule Items
CREATE TRIGGER set_timestamp
BEFORE UPDATE ON schedule_items
FOR EACH ROW
EXECUTE FUNCTION trigger_set_timestamp();

-- Checklists
CREATE TRIGGER set_timestamp
BEFORE UPDATE ON checklists
FOR EACH ROW
EXECUTE FUNCTION trigger_set_timestamp();

-- Punchlist Items
CREATE TRIGGER set_timestamp
BEFORE UPDATE ON punchlist_items
FOR EACH ROW
EXECUTE FUNCTION trigger_set_timestamp();

-- Pull Planning Sessions
CREATE TRIGGER set_timestamp
BEFORE UPDATE ON pull_planning_sessions
FOR EACH ROW
EXECUTE FUNCTION trigger_set_timestamp();

-- Pull Planning Items
CREATE TRIGGER set_timestamp
BEFORE UPDATE ON pull_planning_items
FOR EACH ROW
EXECUTE FUNCTION trigger_set_timestamp();

-- Safety Observations
CREATE TRIGGER set_timestamp
BEFORE UPDATE ON safety_observations
FOR EACH ROW
EXECUTE FUNCTION trigger_set_timestamp();

-- PreTask Plans
CREATE TRIGGER set_timestamp
BEFORE UPDATE ON pretask_plans
FOR EACH ROW
EXECUTE FUNCTION trigger_set_timestamp();

-- Job Hazard Analysis
CREATE TRIGGER set_timestamp
BEFORE UPDATE ON job_hazard_analysis
FOR EACH ROW
EXECUTE FUNCTION trigger_set_timestamp();

-- Employee Orientations
CREATE TRIGGER set_timestamp
BEFORE UPDATE ON employee_orientations
FOR EACH ROW
EXECUTE FUNCTION trigger_set_timestamp();

-- Prime Contracts
CREATE TRIGGER set_timestamp
BEFORE UPDATE ON prime_contracts
FOR EACH ROW
EXECUTE FUNCTION trigger_set_timestamp();

-- Subcontracts
CREATE TRIGGER set_timestamp
BEFORE UPDATE ON subcontracts
FOR EACH ROW
EXECUTE FUNCTION trigger_set_timestamp();

-- Professional Service Agreements
CREATE TRIGGER set_timestamp
BEFORE UPDATE ON professional_service_agreements
FOR EACH ROW
EXECUTE FUNCTION trigger_set_timestamp();

-- Lien Waivers
CREATE TRIGGER set_timestamp
BEFORE UPDATE ON lien_waivers
FOR EACH ROW
EXECUTE FUNCTION trigger_set_timestamp();

-- Certificates of Insurance
CREATE TRIGGER set_timestamp
BEFORE UPDATE ON certificates_of_insurance
FOR EACH ROW
EXECUTE FUNCTION trigger_set_timestamp();

-- Letters of Intent
CREATE TRIGGER set_timestamp
BEFORE UPDATE ON letters_of_intent
FOR EACH ROW
EXECUTE FUNCTION trigger_set_timestamp();

-- Budget Line Items
CREATE TRIGGER set_timestamp
BEFORE UPDATE ON budget_line_items
FOR EACH ROW
EXECUTE FUNCTION trigger_set_timestamp();

-- Invoices
CREATE TRIGGER set_timestamp
BEFORE UPDATE ON invoices
FOR EACH ROW
EXECUTE FUNCTION trigger_set_timestamp();

-- Direct Costs
CREATE TRIGGER set_timestamp
BEFORE UPDATE ON direct_costs
FOR EACH ROW
EXECUTE FUNCTION trigger_set_timestamp();

-- Potential Changes
CREATE TRIGGER set_timestamp
BEFORE UPDATE ON potential_changes
FOR EACH ROW
EXECUTE FUNCTION trigger_set_timestamp();

-- Change Orders
CREATE TRIGGER set_timestamp
BEFORE UPDATE ON change_orders
FOR EACH ROW
EXECUTE FUNCTION trigger_set_timestamp();

-- Approval Letters
CREATE TRIGGER set_timestamp
BEFORE UPDATE ON approval_letters
FOR EACH ROW
EXECUTE FUNCTION trigger_set_timestamp();

-- Time and Materials Tickets
CREATE TRIGGER set_timestamp
BEFORE UPDATE ON time_materials_tickets
FOR EACH ROW
EXECUTE FUNCTION trigger_set_timestamp();

-- BIM Models
CREATE TRIGGER set_timestamp
BEFORE UPDATE ON bim_models
FOR EACH ROW
EXECUTE FUNCTION trigger_set_timestamp();

-- Coordination Issues
CREATE TRIGGER set_timestamp
BEFORE UPDATE ON coordination_issues
FOR EACH ROW
EXECUTE FUNCTION trigger_set_timestamp();

-- O&M Manuals
CREATE TRIGGER set_timestamp
BEFORE UPDATE ON om_manuals
FOR EACH ROW
EXECUTE FUNCTION trigger_set_timestamp();

-- Warranties
CREATE TRIGGER set_timestamp
BEFORE UPDATE ON warranties
FOR EACH ROW
EXECUTE FUNCTION trigger_set_timestamp();

-- Attic Stock
CREATE TRIGGER set_timestamp
BEFORE UPDATE ON attic_stock
FOR EACH ROW
EXECUTE FUNCTION trigger_set_timestamp();

-- CSI Divisions
CREATE TRIGGER set_timestamp
BEFORE UPDATE ON csi_divisions
FOR EACH ROW
EXECUTE FUNCTION trigger_set_timestamp();

-- CSI Subdivisions
CREATE TRIGGER set_timestamp
BEFORE UPDATE ON csi_subdivisions
FOR EACH ROW
EXECUTE FUNCTION trigger_set_timestamp();

-- Cost Codes
CREATE TRIGGER set_timestamp
BEFORE UPDATE ON cost_codes
FOR EACH ROW
EXECUTE FUNCTION trigger_set_timestamp();

-- Labor Rates
CREATE TRIGGER set_timestamp
BEFORE UPDATE ON labor_rates
FOR EACH ROW
EXECUTE FUNCTION trigger_set_timestamp();

-- Material Rates
CREATE TRIGGER set_timestamp
BEFORE UPDATE ON material_rates
FOR EACH ROW
EXECUTE FUNCTION trigger_set_timestamp();

-- Equipment Rates
CREATE TRIGGER set_timestamp
BEFORE UPDATE ON equipment_rates
FOR EACH ROW
EXECUTE FUNCTION trigger_set_timestamp();

-- Create RLS (Row Level Security) policies
-- Enable RLS on all tables
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE companies ENABLE ROW LEVEL SECURITY;
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_permissions ENABLE ROW LEVEL SECURITY;
ALTER TABLE project_users ENABLE ROW LEVEL SECURITY;
ALTER TABLE notifications ENABLE ROW LEVEL SECURITY;
ALTER TABLE activity_log ENABLE ROW LEVEL SECURITY;
ALTER TABLE comments ENABLE ROW LEVEL SECURITY;
ALTER TABLE attachments ENABLE ROW LEVEL SECURITY;
ALTER TABLE deadlines ENABLE ROW LEVEL SECURITY;
ALTER TABLE qualified_bidders ENABLE ROW LEVEL SECURITY;
ALTER TABLE bid_packages ENABLE ROW LEVEL SECURITY;
ALTER TABLE bid_package_bidders ENABLE ROW LEVEL SECURITY;
ALTER TABLE bid_manuals ENABLE ROW LEVEL SECURITY;
ALTER TABLE rfis ENABLE ROW LEVEL SECURITY;
ALTER TABLE submittals ENABLE ROW LEVEL SECURITY;
ALTER TABLE drawings ENABLE ROW LEVEL SECURITY;
ALTER TABLE specifications ENABLE ROW LEVEL SECURITY;
ALTER TABLE permits ENABLE ROW LEVEL SECURITY;
ALTER TABLE meeting_minutes ENABLE ROW LEVEL SECURITY;
ALTER TABLE transmittals ENABLE ROW LEVEL SECURITY;
ALTER TABLE transmittal_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE daily_reports ENABLE ROW LEVEL SECURITY;
ALTER TABLE daily_report_labor ENABLE ROW LEVEL SECURITY;
ALTER TABLE daily_report_equipment ENABLE ROW LEVEL SECURITY;
ALTER TABLE photos ENABLE ROW LEVEL SECURITY;
ALTER TABLE schedule_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE checklists ENABLE ROW LEVEL SECURITY;
ALTER TABLE checklist_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE punchlist_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE pull_planning_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE pull_planning_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE safety_observations ENABLE ROW LEVEL SECURITY;
ALTER TABLE pretask_plans ENABLE ROW LEVEL SECURITY;
ALTER TABLE job_hazard_analysis ENABLE ROW LEVEL SECURITY;
ALTER TABLE jha_steps ENABLE ROW LEVEL SECURITY;
ALTER TABLE employee_orientations ENABLE ROW LEVEL SECURITY;
ALTER TABLE prime_contracts ENABLE ROW LEVEL SECURITY;
ALTER TABLE subcontracts ENABLE ROW LEVEL SECURITY;
ALTER TABLE professional_service_agreements ENABLE ROW LEVEL SECURITY;
ALTER TABLE lien_waivers ENABLE ROW LEVEL SECURITY;
ALTER TABLE certificates_of_insurance ENABLE ROW LEVEL SECURITY;
ALTER TABLE letters_of_intent ENABLE ROW LEVEL SECURITY;
ALTER TABLE budget_line_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE invoices ENABLE ROW LEVEL SECURITY;
ALTER TABLE invoice_line_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE direct_costs ENABLE ROW LEVEL SECURITY;
ALTER TABLE potential_changes ENABLE ROW LEVEL SECURITY;
ALTER TABLE change_orders ENABLE ROW LEVEL SECURITY;
ALTER TABLE change_order_line_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE approval_letters ENABLE ROW LEVEL SECURITY;
ALTER TABLE time_materials_tickets ENABLE ROW LEVEL SECURITY;
ALTER TABLE tm_labor ENABLE ROW LEVEL SECURITY;
ALTER TABLE tm_equipment ENABLE ROW LEVEL SECURITY;
ALTER TABLE tm_materials ENABLE ROW LEVEL SECURITY;
ALTER TABLE bim_models ENABLE ROW LEVEL SECURITY;
ALTER TABLE coordination_issues ENABLE ROW LEVEL SECURITY;
ALTER TABLE om_manuals ENABLE ROW LEVEL SECURITY;
ALTER TABLE warranties ENABLE ROW LEVEL SECURITY;
ALTER TABLE attic_stock ENABLE ROW LEVEL SECURITY;
ALTER TABLE csi_divisions ENABLE ROW LEVEL SECURITY;
ALTER TABLE csi_subdivisions ENABLE ROW LEVEL SECURITY;
ALTER TABLE cost_codes ENABLE ROW LEVEL SECURITY;
ALTER TABLE labor_rates ENABLE ROW LEVEL SECURITY;
ALTER TABLE material_rates ENABLE ROW LEVEL SECURITY;
ALTER TABLE equipment_rates ENABLE ROW LEVEL SECURITY;

-- Create policy for authenticated users to view their projects
CREATE POLICY "Users can view their projects" ON projects
  FOR SELECT
  USING (
    id IN (
      SELECT project_id FROM project_users WHERE user_id = auth.uid()
    )
  );

-- Create policy for users to view companies
CREATE POLICY "Users can view all companies" ON companies
  FOR SELECT
  USING (true);

-- Create policy for users to view user profiles
CREATE POLICY "Users can view all user profiles" ON users
  FOR SELECT
  USING (true);

-- Project users policies
CREATE POLICY "Users can view their project assignments" ON project_users
  FOR SELECT
  USING (true);

-- Policy for users to view their own notifications
CREATE POLICY "Users can view their own notifications" ON notifications
  FOR SELECT
  USING (user_id = auth.uid());

-- Activity log policies
CREATE POLICY "Users can view activity for their projects" ON activity_log
  FOR SELECT
  USING (
    project_id IN (
      SELECT project_id FROM project_users WHERE user_id = auth.uid()
    )
  );

-- Comments policies
CREATE POLICY "Users can view comments for their projects" ON comments
  FOR SELECT
  USING (
    project_id IN (
      SELECT project_id FROM project_users WHERE user_id = auth.uid()
    )
  );

CREATE POLICY "Users can create comments for their projects" ON comments
  FOR INSERT
  WITH CHECK (
    project_id IN (
      SELECT project_id FROM project_users WHERE user_id = auth.uid()
    )
  );

CREATE POLICY "Users can update their own comments" ON comments
  FOR UPDATE
  USING (user_id = auth.uid());

CREATE POLICY "Users can delete their own comments" ON comments
  FOR DELETE
  USING (user_id = auth.uid());

-- Attachments policies
CREATE POLICY "Users can view attachments for their projects" ON attachments
  FOR SELECT
  USING (
    project_id IN (
      SELECT project_id FROM project_users WHERE user_id = auth.uid()
    )
  );

CREATE POLICY "Users can upload attachments to their projects" ON attachments
  FOR INSERT
  WITH CHECK (
    project_id IN (
      SELECT project_id FROM project_users WHERE user_id = auth.uid()
    )
  );

-- Apply similar policies to other tables based on project access
-- This is a pattern that can be applied to all project-related tables

-- Function to check if user has permission to access a module for a project
CREATE OR REPLACE FUNCTION check_project_module_permission(p_user_id UUID, p_project_id INTEGER, p_module VARCHAR, p_required_level INTEGER)
RETURNS BOOLEAN AS $
DECLARE
  v_is_project_member BOOLEAN;
  v_has_permission BOOLEAN;
BEGIN
  -- Check if user is a member of the project
  SELECT EXISTS(
    SELECT 1 FROM project_users WHERE user_id = p_user_id AND project_id = p_project_id
  ) INTO v_is_project_member;
  
  -- If not a project member, deny access
  IF NOT v_is_project_member THEN
    RETURN FALSE;
  END IF;
  
  -- Check if user has required permission level for this module
  SELECT check_user_permission(p_user_id, p_module, p_required_level) INTO v_has_permission;
  
  RETURN v_has_permission;
END;
$ LANGUAGE plpgsql;

-- Create before insert trigger for activity logging
CREATE OR REPLACE FUNCTION log_activity_insert()
RETURNS TRIGGER AS $
DECLARE
  v_module VARCHAR;
  v_record_type VARCHAR;
BEGIN
  -- Determine module and record type from table name
  v_record_type := TG_TABLE_NAME;
  
  -- Map table to module
  CASE
    WHEN TG_TABLE_NAME IN ('qualified_bidders', 'bid_packages', 'bid_manuals') THEN
      v_module := 'preconstruction';
    WHEN TG_TABLE_NAME IN ('rfis', 'submittals', 'drawings', 'specifications', 'permits', 'meeting_minutes', 'transmittals') THEN
      v_module := 'engineering';
    WHEN TG_TABLE_NAME IN ('daily_reports', 'photos', 'schedule_items', 'checklists', 'punchlist_items', 'pull_planning_sessions') THEN
      v_module := 'field';
    WHEN TG_TABLE_NAME IN ('safety_observations', 'pretask_plans', 'job_hazard_analysis', 'employee_orientations') THEN
      v_module := 'safety';
    WHEN TG_TABLE_NAME IN ('prime_contracts', 'subcontracts', 'professional_service_agreements', 'lien_waivers', 'certificates_of_insurance', 'letters_of_intent') THEN
      v_module := 'contracts';
    WHEN TG_TABLE_NAME IN ('budget_line_items', 'invoices', 'direct_costs', 'potential_changes', 'change_orders', 'approval_letters', 'time_materials_tickets') THEN
      v_module := 'cost';
    WHEN TG_TABLE_NAME IN ('bim_models', 'coordination_issues') THEN
      v_module := 'bim';
    WHEN TG_TABLE_NAME IN ('om_manuals', 'warranties', 'attic_stock') THEN
      v_module := 'closeout';
    ELSE
      v_module := 'other';
  END CASE;
  
  -- Insert activity log entry
  INSERT INTO activity_log (
    action,
    module,
    record_type,
    record_id,
    user_id,
    project_id,
    created_at
  ) VALUES (
    'create',
    v_module,
    v_record_type,
    NEW.id,
    auth.uid(),
    NEW.project_id,
    NOW()
  );
  
  RETURN NEW;
END;
$ LANGUAGE plpgsql;

-- Apply activity log triggers to main module tables
CREATE TRIGGER log_rfi_insert
AFTER INSERT ON rfis
FOR EACH ROW
EXECUTE FUNCTION log_activity_insert();

CREATE TRIGGER log_submittal_insert
AFTER INSERT ON submittals
FOR EACH ROW
EXECUTE FUNCTION log_activity_insert();

CREATE TRIGGER log_daily_report_insert
AFTER INSERT ON daily_reports
FOR EACH ROW
EXECUTE FUNCTION log_activity_insert();

CREATE TRIGGER log_change_order_insert
AFTER INSERT ON change_orders
FOR EACH ROW
EXECUTE FUNCTION log_activity_insert();

-- Add more triggers for other important tables as needed

-- Function to notify users on important events
CREATE OR REPLACE FUNCTION notify_users_on_event()
RETURNS TRIGGER AS $
DECLARE
  v_title TEXT;
  v_message TEXT;
  v_link TEXT;
  v_type TEXT;
  v_user_id UUID;
  v_users UUID[];
BEGIN
  -- Determine notification type based on table and action
  IF TG_TABLE_NAME = 'rfis' THEN
    IF TG_OP = 'INSERT' THEN
      v_title := 'New RFI Created';
      v_message := 'A new RFI "' || NEW.title || '" has been created';
      v_link := '/pages/engineering/rfis.html?id=' || NEW.id;
      v_type := 'rfi';
      
      -- Get users to notify (e.g., design team)
      SELECT ARRAY_AGG(user_id) INTO v_users
      FROM project_users
      WHERE project_id = NEW.project_id AND role = 'design_team';
    ELSIF TG_OP = 'UPDATE' AND OLD.status != NEW.status AND NEW.status = 'answered' THEN
      v_title := 'RFI Answered';
      v_message := 'RFI "' || NEW.title || '" has been answered';
      v_link := '/pages/engineering/rfis.html?id=' || NEW.id;
      v_type := 'rfi';
      
      -- Notify the creator
      v_users := ARRAY[NEW.created_by];
    END IF;
  ELSIF TG_TABLE_NAME = 'submittals' THEN
    IF TG_OP = 'UPDATE' AND OLD.status != NEW.status THEN
      v_title := 'Submittal Status Updated';
      v_message := 'Submittal "' || NEW.title || '" is now ' || NEW.status;
      v_link := '/pages/engineering/submittals.html?id=' || NEW.id;
      v_type := 'submittal';
      
      -- Notify creator and assignees
      v_users := ARRAY[NEW.created_by, NEW.submitted_by];
    END IF;
  END IF;
  
  -- Create notifications for each user
  IF v_users IS NOT NULL THEN
    FOREACH v_user_id IN ARRAY v_users
    LOOP
      IF v_user_id IS NOT NULL THEN
        INSERT INTO notifications (
          user_id,
          project_id,
          title,
          message,
          type,
          link,
          read,
          created_at
        ) VALUES (
          v_user_id,
          NEW.project_id,
          v_title,
          v_message,
          v_type,
          v_link,
          FALSE,
          NOW()
        );
      END IF;
    END LOOP;
  END IF;
  
  RETURN NEW;
END;
$ LANGUAGE plpgsql;

-- Apply notification triggers
CREATE TRIGGER notify_on_rfi_change
AFTER INSERT OR UPDATE ON rfis
FOR EACH ROW
EXECUTE FUNCTION notify_users_on_event();

CREATE TRIGGER notify_on_submittal_change
AFTER INSERT OR UPDATE ON submittals
FOR EACH ROW
EXECUTE FUNCTION notify_users_on_event();

-- Add more notification triggers for other important tables as needed