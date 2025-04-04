created_by UUID REFERENCES users(id) ON DELETE SET NULL,
  updated_at TIMESTAMPTZ,
  updated_by UUID REFERENCES users(id) ON DELETE SET NULL
);

-- Invoice Line Items (G703)
CREATE TABLE invoice_line_items (
  id SERIAL PRIMARY KEY,
  invoice_id INTEGER REFERENCES invoices(id) ON DELETE CASCADE,
  cost_code VARCHAR(50),
  description VARCHAR(255) NOT NULL,
  scheduled_value DECIMAL(14, 2) NOT NULL,
  previous_work_completed DECIMAL(14, 2) DEFAULT 0,
  current_work_completed DECIMAL(14, 2) DEFAULT 0,
  materials_stored DECIMAL(14, 2) DEFAULT 0,
  total_completed_and_stored DECIMAL(14, 2) GENERATED ALWAYS AS (previous_work_completed + current_work_completed + materials_stored) STORED,
  percentage_complete DECIMAL(5, 2) GENERATED ALWAYS AS (CASE WHEN scheduled_value = 0 THEN 0 ELSE ((previous_work_completed + current_work_completed + materials_stored) / scheduled_value) * 100 END) STORED,
  balance_to_finish DECIMAL(14, 2) GENERATED ALWAYS AS (scheduled_value - (previous_work_completed + current_work_completed + materials_stored)) STORED,
  retainage DECIMAL(14, 2),
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Direct Costs
CREATE TABLE direct_costs (
  id SERIAL PRIMARY KEY,
  project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
  cost_type VARCHAR(30) NOT NULL,
  title VARCHAR(100) NOT NULL,
  vendor_id INTEGER REFERENCES companies(id),
  invoice_number VARCHAR(50),
  invoice_date DATE,
  due_date DATE,
  cost_code VARCHAR(50),
  description TEXT,
  amount DECIMAL(14, 2) NOT NULL,
  tax_amount DECIMAL(14, 2) DEFAULT 0,
  total_amount DECIMAL(14, 2) GENERATED ALWAYS AS (amount + tax_amount) STORED,
  status VARCHAR(30) DEFAULT 'pending',
  approved BOOLEAN DEFAULT FALSE,
  approved_by UUID REFERENCES users(id) ON DELETE SET NULL,
  approved_date DATE,
  paid BOOLEAN DEFAULT FALSE,
  paid_date DATE,
  payment_reference VARCHAR(50),
  notes TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  created_by UUID REFERENCES users(id) ON DELETE SET NULL,
  updated_at TIMESTAMPTZ,
  updated_by UUID REFERENCES users(id) ON DELETE SET NULL
);

-- Potential Changes
CREATE TABLE potential_changes (
  id SERIAL PRIMARY KEY,
  project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
  title VARCHAR(100) NOT NULL,
  description TEXT,
  change_type VARCHAR(50),
  reason_for_change TEXT,
  requester VARCHAR(100),
  request_date DATE,
  impact_on_scope TEXT,
  cost_impact DECIMAL(14, 2),
  schedule_impact INTEGER,
  status VARCHAR(30) DEFAULT 'draft',
  priority priority_level DEFAULT 'medium',
  assigned_to UUID REFERENCES users(id) ON DELETE SET NULL,
  related_rfi_id INTEGER,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  created_by UUID REFERENCES users(id) ON DELETE SET NULL,
  updated_at TIMESTAMPTZ,
  updated_by UUID REFERENCES users(id) ON DELETE SET NULL
);

-- Change Orders
CREATE TABLE change_orders (
  id SERIAL PRIMARY KEY,
  project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
  title VARCHAR(100) NOT NULL,
  change_order_number VARCHAR(50),
  description TEXT,
  contract_id INTEGER,
  contract_type VARCHAR(30),
  company_id INTEGER REFERENCES companies(id),
  potential_change_id INTEGER REFERENCES potential_changes(id) ON DELETE SET NULL,
  cost_impact DECIMAL(14, 2),
  schedule_impact INTEGER,
  status change_order_status DEFAULT 'draft',
  submitted_date DATE,
  approved_date DATE,
  approved_by UUID REFERENCES users(id) ON DELETE SET NULL,
  executed_date DATE,
  notes TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  created_by UUID REFERENCES users(id) ON DELETE SET NULL,
  updated_at TIMESTAMPTZ,
  updated_by UUID REFERENCES users(id) ON DELETE SET NULL
);

-- Change Order Line Items
CREATE TABLE change_order_line_items (
  id SERIAL PRIMARY KEY,
  change_order_id INTEGER REFERENCES change_orders(id) ON DELETE CASCADE,
  cost_code VARCHAR(50),
  description VARCHAR(255) NOT NULL,
  amount DECIMAL(14, 2) NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Approval Letters & Directives
CREATE TABLE approval_letters (
  id SERIAL PRIMARY KEY,
  project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
  title VARCHAR(100) NOT NULL,
  letter_type VARCHAR(50),
  letter_number VARCHAR(50),
  description TEXT,
  from_company_id INTEGER REFERENCES companies(id),
  to_company_id INTEGER REFERENCES companies(id),
  issue_date DATE,
  reference_number VARCHAR(50),
  reference_type VARCHAR(50),
  amount DECIMAL(14, 2),
  status VARCHAR(30) DEFAULT 'draft',
  notes TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  created_by UUID REFERENCES users(id) ON DELETE SET NULL,
  updated_at TIMESTAMPTZ,
  updated_by UUID REFERENCES users(id) ON DELETE SET NULL
);

-- Time and Materials Tickets
CREATE TABLE time_materials_tickets (
  id SERIAL PRIMARY KEY,
  project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
  ticket_number VARCHAR(50) NOT NULL,
  title VARCHAR(100) NOT NULL,
  company_id INTEGER REFERENCES companies(id),
  work_date DATE,
  description TEXT,
  location VARCHAR(100),
  approved_by VARCHAR(100),
  approved_date DATE,
  status VARCHAR(30) DEFAULT 'draft',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  created_by UUID REFERENCES users(id) ON DELETE SET NULL,
  updated_at TIMESTAMPTZ,
  updated_by UUID REFERENCES users(id) ON DELETE SET NULL
);

-- T&M Labor
CREATE TABLE tm_labor (
  id SERIAL PRIMARY KEY,
  ticket_id INTEGER REFERENCES time_materials_tickets(id) ON DELETE CASCADE,
  worker_name VARCHAR(100) NOT NULL,
  trade VARCHAR(50),
  classification VARCHAR(50),
  hours_regular DECIMAL(6, 2) DEFAULT 0,
  hours_overtime DECIMAL(6, 2) DEFAULT 0,
  hours_doubletime DECIMAL(6, 2) DEFAULT 0,
  rate_regular DECIMAL(10, 2),
  rate_overtime DECIMAL(10, 2),
  rate_doubletime DECIMAL(10, 2),
  total_amount DECIMAL(14, 2),
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- T&M Equipment
CREATE TABLE tm_equipment (
  id SERIAL PRIMARY KEY,
  ticket_id INTEGER REFERENCES time_materials_tickets(id) ON DELETE CASCADE,
  equipment_type VARCHAR(100) NOT NULL,
  description VARCHAR(255),
  quantity INTEGER DEFAULT 1,
  hours_used DECIMAL(6, 2),
  rate DECIMAL(10, 2),
  total_amount DECIMAL(14, 2),
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- T&M Materials
CREATE TABLE tm_materials (
  id SERIAL PRIMARY KEY,
  ticket_id INTEGER REFERENCES time_materials_tickets(id) ON DELETE CASCADE,
  material_type VARCHAR(100) NOT NULL,
  description VARCHAR(255),
  quantity DECIMAL(10, 3),
  unit VARCHAR(20),
  unit_price DECIMAL(10, 2),
  total_amount DECIMAL(14, 2),
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- BIM MODULE
-- BIM Models
CREATE TABLE bim_models (
  id SERIAL PRIMARY KEY,
  project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
  title VARCHAR(100) NOT NULL,
  model_url TEXT,
  model_type VARCHAR(50),
  version VARCHAR(20),
  version_date DATE,
  description TEXT,
  discipline VARCHAR(50),
  status VARCHAR(30) DEFAULT 'current',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  created_by UUID REFERENCES users(id) ON DELETE SET NULL,
  updated_at TIMESTAMPTZ,
  updated_by UUID REFERENCES users(id) ON DELETE SET NULL
);

-- BIM Coordination Issues
CREATE TABLE coordination_issues (
  id SERIAL PRIMARY KEY,
  project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
  title VARCHAR(100) NOT NULL,
  description TEXT,
  issue_type VARCHAR(50),
  location_x DECIMAL(10, 3),
  location_y DECIMAL(10, 3),
  location_z DECIMAL(10, 3),
  area VARCHAR(100),
  disciplines_involved TEXT[],
  priority priority_level DEFAULT 'medium',
  status VARCHAR(30) DEFAULT 'open',
  identified_date DATE,
  due_date DATE,
  resolved_date DATE,
  resolved_by UUID REFERENCES users(id) ON DELETE SET NULL,
  resolution_description TEXT,
  assigned_to UUID REFERENCES users(id) ON DELETE SET NULL,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  created_by UUID REFERENCES users(id) ON DELETE SET NULL,
  updated_at TIMESTAMPTZ,
  updated_by UUID REFERENCES users(id) ON DELETE SET NULL
);

-- CLOSEOUT MODULE
-- O&M Manuals
CREATE TABLE om_manuals (
  id SERIAL PRIMARY KEY,
  project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
  title VARCHAR(100) NOT NULL,
  description TEXT,
  system VARCHAR(100),
  equipment VARCHAR(100),
  manufacturer VARCHAR(100),
  supplier_id INTEGER REFERENCES companies(id),
  submittal_id INTEGER,
  status VARCHAR(30) DEFAULT 'draft',
  required_date DATE,
  received_date DATE,
  approved_date DATE,
  approved_by UUID REFERENCES users(id) ON DELETE SET NULL,
  notes TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  created_by UUID REFERENCES users(id) ON DELETE SET NULL,
  updated_at TIMESTAMPTZ,
  updated_by UUID REFERENCES users(id) ON DELETE SET NULL
);

-- Warranties
CREATE TABLE warranties (
  id SERIAL PRIMARY KEY,
  project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
  title VARCHAR(100) NOT NULL,
  description TEXT,
  system VARCHAR(100),
  equipment VARCHAR(100),
  warranty_provider_id INTEGER REFERENCES companies(id),
  start_date DATE,
  end_date DATE,
  duration_months INTEGER GENERATED ALWAYS AS (EXTRACT(YEAR FROM end_date - start_date) * 12 + EXTRACT(MONTH FROM end_date - start_date)) STORED,
  warranty_type VARCHAR(50),
  coverage_details TEXT,
  exclusions TEXT,
  submittal_id INTEGER,
  status VARCHAR(30) DEFAULT 'active',
  notes TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  created_by UUID REFERENCES users(id) ON DELETE SET NULL,
  updated_at TIMESTAMPTZ,
  updated_by UUID REFERENCES users(id) ON DELETE SET NULL
);

-- Attic Stock
CREATE TABLE attic_stock (
  id SERIAL PRIMARY KEY,
  project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
  title VARCHAR(100) NOT NULL,
  description TEXT,
  material_type VARCHAR(100),
  quantity DECIMAL(10, 3),
  unit VARCHAR(20),
  location VARCHAR(100),
  supplier_id INTEGER REFERENCES companies(id),
  submittal_id INTEGER,
  required_date DATE,
  received_date DATE,
  received_by UUID REFERENCES users(id) ON DELETE SET NULL,
  owner_accepted BOOLEAN DEFAULT FALSE,
  owner_accepted_date DATE,
  owner_representative VARCHAR(100),
  notes TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  created_by UUID REFERENCES users(id) ON DELETE SET NULL,
  updated_at TIMESTAMPTZ,
  updated_by UUID REFERENCES users(id) ON DELETE SET NULL
);

-- SETTINGS MODULE
-- CSI Divisions
CREATE TABLE csi_divisions (
  id SERIAL PRIMARY KEY,
  division_number VARCHAR(10) NOT NULL,
  division_name VARCHAR(100) NOT NULL,
  description TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ
);

-- CSI Subdivisions
CREATE TABLE csi_subdivisions (
  id SERIAL PRIMARY KEY,
  division_id INTEGER REFERENCES csi_divisions(id) ON DELETE CASCADE,
  subdivision_number VARCHAR(10) NOT NULL,
  subdivision_name VARCHAR(100) NOT NULL,
  description TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ
);

-- Cost Codes
CREATE TABLE cost_codes (
  id SERIAL PRIMARY KEY,
  project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
  code VARCHAR(20) NOT NULL,
  description VARCHAR(100) NOT NULL,
  csi_division VARCHAR(10),
  csi_subdivision VARCHAR(10),
  cost_type VARCHAR(30),
  parent_code VARCHAR(20),
  active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  created_by UUID REFERENCES users(id) ON DELETE SET NULL,
  updated_at TIMESTAMPTZ,
  updated_by UUID REFERENCES users(id) ON DELETE SET NULL
);

-- Labor Rates
CREATE TABLE labor_rates (
  id SERIAL PRIMARY KEY,
  project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
  trade VARCHAR(50) NOT NULL,
  classification VARCHAR(50) NOT NULL,
  company_id INTEGER REFERENCES companies(id),
  regular_rate DECIMAL(10, 2) NOT NULL,
  overtime_rate DECIMAL(10, 2),
  doubletime_rate DECIMAL(10, 2),
  burden_percentage DECIMAL(5, 2),
  effective_date DATE,
  expiration_date DATE,
  notes TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  created_by UUID REFERENCES users(id) ON DELETE SET NULL,
  updated_at TIMESTAMPTZ,
  updated_by UUID REFERENCES users(id) ON DELETE SET NULL
);

-- Material Rates
CREATE TABLE material_rates (
  id SERIAL PRIMARY KEY,
  project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
  material_name VARCHAR(100) NOT NULL,
  description TEXT,
  unit VARCHAR(20) NOT NULL,
  unit_cost DECIMAL(10, 2) NOT NULL,
  supplier_id INTEGER REFERENCES companies(id),
  markup_percentage DECIMAL(5, 2),
  effective_date DATE,
  expiration_date DATE,
  notes TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  created_by UUID REFERENCES users(id) ON DELETE SET NULL,
  updated_at TIMESTAMPTZ,
  updated_by UUID REFERENCES users(id) ON DELETE SET NULL
);

-- Equipment Rates
CREATE TABLE equipment_rates (
  id SERIAL PRIMARY KEY,
  project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
  equipment_name VARCHAR(100) NOT NULL,
  description TEXT,
  rate DECIMAL(10, 2) NOT NULL,
  rate_unit VARCHAR(20) NOT NULL,
  owner_id INTEGER REFERENCES companies(id),
  model VARCHAR(50),
  make VARCHAR(50),
  year INTEGER,
  effective_date DATE,
  expiration_date DATE,
  notes TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  created_by UUID REFERENCES users(id) ON DELETE SET NULL,
  updated_at TIMESTAMPTZ,
  updated_by UUID REFERENCES users(id) ON DELETE SET NULL
);

-- FUNCTIONS & PROCEDURES

-- Function to check user permission for a module
CREATE OR REPLACE FUNCTION check_user_permission(p_user_id UUID, p_module VARCHAR, p_required_level INTEGER)
RETURNS BOOLEAN AS $
DECLARE
  v_user_role user_role;
  v_permission_level INTEGER;
BEGIN
  -- Get user role
  SELECT role INTO v_user_role FROM users WHERE id = p_user_id;
  
  -- Check for custom permission
  SELECT permission_level INTO v_permission_level
  FROM user_permissions
  WHERE user_id = p_user_id AND module_id = p_module;
  
  -- If no custom permission, use role-based permission
  IF v_permission_level IS NULL THEN
    -- Define permissions based on role
    CASE
      WHEN v_user_role = 'owner' THEN
        v_permission_level := 6; -- Admin level
      WHEN v_user_role = 'owner_rep' THEN
        v_permission_level := 4; -- Create level
      WHEN v_user_role = 'general_contractor' THEN
        CASE
          WHEN p_module IN ('preconstruction', 'engineering', 'field', 'safety', 'closeout') THEN
            v_permission_level := 4; -- Create level
          WHEN p_module IN ('contracts', 'cost', 'bim') THEN
            v_permission_level := 3; -- Edit level
          WHEN p_module = 'settings' THEN
            v_permission_level := 2; -- Comment level
          WHEN p_module = 'reports' THEN
            v_permission_level := 4; -- Create level
          ELSE
            v_permission_level := 1; -- Read level
        END CASE;
      WHEN v_user_role = 'subcontractor' THEN
        CASE
          WHEN p_module = 'safety' THEN
            v_permission_level := 3; -- Edit level
          WHEN p_module IN ('preconstruction', 'engineering', 'field', 'bim', 'closeout') THEN
            v_permission_level := 2; -- Comment level
          WHEN p_module IN ('contracts', 'cost', 'settings', 'reports') THEN
            v_permission_level := 1; -- Read level
          ELSE
            v_permission_level := 1; -- Read level
        END CASE;
      WHEN v_user_role = 'design_team' THEN
        CASE
          WHEN p_module IN ('engineering', 'bim') THEN
            v_permission_level := 4; -- Create level
          WHEN p_module IN ('cost') THEN
            v_permission_level := 2; -- Comment level
          WHEN p_module IN ('preconstruction', 'field', 'closeout') THEN
            v_permission_level := 2; -- Comment level
          WHEN p_module IN ('safety', 'contracts', 'settings', 'reports') THEN
            v_permission_level := 1; -- Read level
          ELSE
            v_permission_level := 1; -- Read level
        END CASE;
      ELSE
        v_permission_level := 0; -- No access
    END CASE;
  END IF;
  
  -- Return true if user has sufficient permission
  RETURN v_permission_level >= p_required_level;
END;
$ LANGUAGE plpgsql;

-- Function to get project stats
CREATE OR REPLACE FUNCTION get_project_stats(p_project_id INTEGER)
RETURNS TABLE (
  project_name VARCHAR,
  start_date DATE,
  end_date DATE,
  total_budget DECIMAL,
  used_budget DECIMAL,
  total_rfis INTEGER,
  open_rfis INTEGER,
  total_submittals INTEGER,
  open_submittals INTEGER,
  total_change_orders INTEGER,
  change_order_amount DECIMAL
) AS $
BEGIN
  RETURN QUERY
  SELECT 
    p.name,
    p.start_date,
    p.end_date,
    COALESCE(SUM(b.current_amount), 0) AS total_budget,
    COALESCE(SUM(b.actual_amount), 0) AS used_budget,
    COUNT(DISTINCT r.id) AS total_rfis,
    COUNT(DISTINCT CASE WHEN r.status IN ('draft', 'submitted', 'in_review') THEN r.id END) AS open_rfis,
    COUNT(DISTINCT s.id) AS total_submittals,
    COUNT(DISTINCT CASE WHEN s.status IN ('draft', 'submitted', 'in_review', 'revise_and_resubmit') THEN s.id END) AS open_submittals,
    COUNT(DISTINCT co.id) AS total_change_orders,
    COALESCE(SUM(co.cost_impact), 0) AS change_order_amount
  FROM 
    projects p
    LEFT JOIN budget_line_items b ON p.id = b.project_id
    LEFT JOIN rfis r ON p.id = r.project_id
    LEFT JOIN submittals s ON p.id = s.project_id
    LEFT JOIN change_orders co ON p.id = co.project_id
  WHERE 
    p.id = p_project_id
  GROUP BY 
    p.name, p.start_date, p.end_date;
END;
$ LANGUAGE plpgsql;

-- Function to get task summary for a user
CREATE OR REPLACE FUNCTION get_task_summary(p_user_id UUID)
RETURNS TABLE (
  total_tasks INTEGER,
  completed_tasks INTEGER,
  overdue_tasks INTEGER,
  upcoming_tasks INTEGER
) AS $
DECLARE
  v_today DATE := CURRENT_DATE;
BEGIN
  RETURN QUERY
  SELECT
    COUNT(*) AS total_tasks,
    COUNT(CASE WHEN d.status = 'completed' THEN 1 END) AS completed_tasks,
    COUNT(CASE WHEN d.status != 'completed' AND d.due_date < v_today THEN 1 END) AS overdue_tasks,
    COUNT(CASE WHEN d.status != 'completed' AND d.due_date >= v_today THEN 1 END) AS upcoming_tasks
  FROM
    deadlines d
  WHERE
    d.assigned_to = p_user_id;
END;
$ LANGUAGE plpgsql;

-- Global search function
CREATE OR REPLACE FUNCTION global_search(search_query TEXT)
RETURNS TABLE (
  module VARCHAR,
  record_type VARCHAR,
  record_id INTEGER,
  title VARCHAR,
  subtitle VARCHAR,
  url TEXT
) AS $
BEGIN
  -- Search RFIs
  RETURN QUERY
  SELECT
    'engineering' AS module,
    'rfi' AS record_type,
    id AS record_id,
    title,
    'RFI #' || id::TEXT AS subtitle,
    '/pages/engineering/rfis.html?id=' || id::TEXT AS url
  FROM
    rfis
  WHERE
    title ILIKE '%' || search_query || '%'
    OR question ILIKE '%' || search_query || '%'
  LIMIT 5;
  
  -- Search Submittals
  RETURN QUERY
  SELECT
    'engineering' AS module,
    'submittal' AS record_type,
    id AS record_id,
    title,
    'Submittal #' || id::TEXT AS subtitle,
    '/pages/engineering/submittals.html?id=' || id::TEXT AS url
  FROM
    submittals
  WHERE
    title ILIKE '%' || search_query || '%'
    OR description ILIKE '%' || search_query || '%'
  LIMIT 5;
  
  -- Search Daily Reports
  RETURN QUERY
  SELECT
    'field' AS module,
    'daily_report' AS record_type,
    id AS record_id,
    'Daily Report - ' || TO_CHAR(report_date, 'MM/DD/YYYY') AS title,
    'Daily Report #' || id::TEXT AS subtitle,
    '/pages/field/daily-reports.html?id=' || id::TEXT AS url
  FROM
    daily_reports
  WHERE
    TO_CHAR(report_date, 'MM/DD/YYYY') ILIKE '%' || search_query || '%'
    OR work_performed ILIKE '%' || search_query || '%'
  LIMIT 5;
  
  -- Search Change Orders
  RETURN QUERY
  SELECT
    'cost' AS module,
    'change_order' AS record_type,
    id AS record_id,
    title,
    'Change Order #' || change_order_number AS subtitle,
    '/pages/cost/change-orders.html?id=' || id::TEXT AS url
  FROM
    change_orders
  WHERE
    title ILIKE '%' || search_query || '%'
    OR change_order_number ILIKE '%' || search_query || '%'
    OR description ILIKE '%' || search_query || '%'
  LIMIT 5;
  
  -- Add more tables as needed...
END;
$ LANGUAGE plpgsql;

-- Insert default values for CSI Divisions
INSERT INTO csi_divisions (division_number, division_name, description)
VALUES 
  ('01', 'General Requirements', 'Project management, coordination, temporary facilities'),
  ('02', 'Existing Conditions', 'Site surveys, demolition, hazardous material removal'),
  ('03', 'Concrete', 'Cast-in-place concrete, precast concrete, concrete forms'),
  ('04', 'Masonry', 'Masonry units, mortaring, reinforcement'),
  ('05', 'Metals', 'Structural steel, metal fabrications, ornamental metal'),
  ('06', 'Wood, Plastics, Composites', 'Rough carpentry, finish carpentry, architectural woodwork'),
  ('07', 'Thermal & Moisture Protection', 'Waterproofing, insulation, roofing, cladding'),
  ('08', 'Openings', 'Doors, windows, skylights, hardware'),
  ('09', 'Finishes', 'Plaster, ceiling, flooring, wall finishes, painting'),
  ('10', 'Specialties', 'Signage, partitions, toilet accessories, lockers'),
  ('11', 'Equipment', 'Kitchen equipment, laboratory equipment, window washing systems'),
  ('12', 'Furnishings', 'Furniture, casework, window treatments'),
  ('13', 'Special Construction', 'Pre-engineered structures, swimming pools, solar collectors'),
  ('14', 'Conveying Equipment', 'Elevators, escalators, lifts'),
  ('21', 'Fire Suppression', 'Fire protection pipework, sprinklers, fire pumps'),
  ('22', 'Plumbing', 'Pipes, fixtures, equipment'),
  ('23', 'Heating, Ventilating, and Air Conditioning', 'HVAC systems and equipment'),
  ('26', 'Electrical', 'Electrical power, lighting, low voltage'),
  ('27', 'Communications', 'Voice and data, audio/visual, alarm systems'),
  ('28', 'Electronic Safety and Security', 'Access control, security'),
  ('31', 'Earthwork', 'Excavation, grading, erosion control'),
  ('32', 'Exterior Improvements', 'Paving, landscaping, site furnishings'),
  ('33', 'Utilities', 'Water, sanitary, storm, electrical, communications');

-- Create triggers for updated_at timestamps
CREATE OR REPLACE FUNCTION trigger_set_timestamp()
RETURNS TRIGGER AS $
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$ LANGUAGE plpgsql;  email VARCHAR(100),
  website VARCHAR(100),
  tax_id VARCHAR(50),
  logo_url TEXT,
  notes TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Users Table (extends Supabase auth.users)
CREATE TABLE users (
  id UUID PRIMARY KEY REFERENCES auth.users,
  email VARCHAR(255) NOT NULL UNIQUE,
  first_name VARCHAR(50),
  last_name VARCHAR(50),
  role user_role NOT NULL,
  phone VARCHAR(30),
  company_id INTEGER REFERENCES companies(id),
  profile_image_url TEXT,
  job_title VARCHAR(100),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  last_login TIMESTAMPTZ
);

-- User Permissions (custom permissions that override role-based permissions)
CREATE TABLE user_permissions (
  id SERIAL PRIMARY KEY,
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  module_id VARCHAR(50) NOT NULL,
  permission_level INTEGER NOT NULL DEFAULT 1,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(user_id, module_id)
);

-- Project Users (linking users to projects)
CREATE TABLE project_users (
  id SERIAL PRIMARY KEY,
  project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  role user_role NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(project_id, user_id)
);

-- Notifications
CREATE TABLE notifications (
  id SERIAL PRIMARY KEY,
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
  title VARCHAR(100) NOT NULL,
  message TEXT NOT NULL,
  type VARCHAR(30),
  link TEXT,
  read BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Activity Log
CREATE TABLE activity_log (
  id SERIAL PRIMARY KEY,
  action VARCHAR(30) NOT NULL,
  module VARCHAR(50) NOT NULL,
  record_type VARCHAR(50) NOT NULL,
  record_id INTEGER NOT NULL,
  user_id UUID REFERENCES users(id) ON DELETE SET NULL,
  project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
  details JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Comments (generic comments for any record type)
CREATE TABLE comments (
  id SERIAL PRIMARY KEY,
  content TEXT NOT NULL,
  record_type VARCHAR(50) NOT NULL,
  record_id INTEGER NOT NULL,
  module VARCHAR(50) NOT NULL,
  user_id UUID REFERENCES users(id) ON DELETE SET NULL,
  project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
  parent_id INTEGER REFERENCES comments(id) ON DELETE CASCADE,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Attachments (generic file attachments for any record type)
CREATE TABLE attachments (
  id SERIAL PRIMARY KEY,
  file_name VARCHAR(255) NOT NULL,
  file_type VARCHAR(100),
  file_size INTEGER,
  file_url TEXT NOT NULL,
  file_path TEXT,
  bucket VARCHAR(50) DEFAULT 'attachments',
  record_type VARCHAR(50) NOT NULL,
  record_id INTEGER NOT NULL,
  module VARCHAR(50) NOT NULL,
  description TEXT,
  user_id UUID REFERENCES users(id) ON DELETE SET NULL,
  project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_by UUID REFERENCES users(id) ON DELETE SET NULL,
  updated_at TIMESTAMPTZ
);

-- Deadlines (generic deadlines for any record type)
CREATE TABLE deadlines (
  id SERIAL PRIMARY KEY,
  title VARCHAR(100) NOT NULL,
  due_date DATE NOT NULL,
  priority priority_level DEFAULT 'medium',
  description TEXT,
  record_type VARCHAR(50),
  record_id INTEGER,
  module VARCHAR(50),
  assigned_to UUID REFERENCES users(id) ON DELETE SET NULL,
  project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
  status VARCHAR(30) DEFAULT 'open',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  created_by UUID REFERENCES users(id) ON DELETE SET NULL,
  updated_at TIMESTAMPTZ,
  updated_by UUID REFERENCES users(id) ON DELETE SET NULL
);

-- Module-specific Tables

-- PRECONSTRUCTION MODULE
-- Qualified Bidders
CREATE TABLE qualified_bidders (
  id SERIAL PRIMARY KEY,
  company_id INTEGER REFERENCES companies(id) ON DELETE CASCADE,
  project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
  csi_division VARCHAR(20),
  csi_subdivision VARCHAR(20),
  trade VARCHAR(100),
  qualification_date DATE,
  status VARCHAR(30) DEFAULT 'active',
  prequalification_score INTEGER,
  notes TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  created_by UUID REFERENCES users(id) ON DELETE SET NULL,
  updated_at TIMESTAMPTZ,
  updated_by UUID REFERENCES users(id) ON DELETE SET NULL
);

-- Bid Packages
CREATE TABLE bid_packages (
  id SERIAL PRIMARY KEY,
  project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
  title VARCHAR(100) NOT NULL,
  description TEXT,
  csi_division VARCHAR(20),
  csi_subdivision VARCHAR(20),
  estimated_value DECIMAL(14, 2),
  status VARCHAR(30) DEFAULT 'draft',
  issue_date DATE,
  due_date DATE,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  created_by UUID REFERENCES users(id) ON DELETE SET NULL,
  updated_at TIMESTAMPTZ,
  updated_by UUID REFERENCES users(id) ON DELETE SET NULL
);

-- Bid Package Bidders
CREATE TABLE bid_package_bidders (
  id SERIAL PRIMARY KEY,
  bid_package_id INTEGER REFERENCES bid_packages(id) ON DELETE CASCADE,
  company_id INTEGER REFERENCES companies(id) ON DELETE CASCADE,
  contact_id UUID REFERENCES users(id) ON DELETE SET NULL,
  status VARCHAR(30) DEFAULT 'invited',
  bid_amount DECIMAL(14, 2),
  bid_date TIMESTAMPTZ,
  notes TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ
);

-- Bid Manuals
CREATE TABLE bid_manuals (
  id SERIAL PRIMARY KEY,
  project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
  title VARCHAR(100) NOT NULL,
  description TEXT,
  version VARCHAR(20),
  status VARCHAR(30) DEFAULT 'draft',
  issue_date DATE,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  created_by UUID REFERENCES users(id) ON DELETE SET NULL,
  updated_at TIMESTAMPTZ,
  updated_by UUID REFERENCES users(id) ON DELETE SET NULL
);

-- ENGINEERING MODULE
-- RFIs (Request for Information)
CREATE TABLE rfis (
  id SERIAL PRIMARY KEY,
  project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
  title VARCHAR(100) NOT NULL,
  question TEXT NOT NULL,
  answer TEXT,
  status rfi_status DEFAULT 'draft',
  priority priority_level DEFAULT 'medium',
  due_date DATE,
  submitted_date DATE,
  answered_date DATE,
  submitted_by UUID REFERENCES users(id) ON DELETE SET NULL,
  assigned_to UUID REFERENCES users(id) ON DELETE SET NULL,
  answered_by UUID REFERENCES users(id) ON DELETE SET NULL,
  csi_division VARCHAR(20),
  cost_impact BOOLEAN DEFAULT FALSE,
  schedule_impact BOOLEAN DEFAULT FALSE,
  cost_impact_amount DECIMAL(14, 2),
  schedule_impact_days INTEGER,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  created_by UUID REFERENCES users(id) ON DELETE SET NULL,
  updated_at TIMESTAMPTZ,
  updated_by UUID REFERENCES users(id) ON DELETE SET NULL
);

-- Submittals
CREATE TABLE submittals (
  id SERIAL PRIMARY KEY,
  project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
  title VARCHAR(100) NOT NULL,
  description TEXT,
  spec_section VARCHAR(50),
  status submittal_status DEFAULT 'draft',
  priority priority_level DEFAULT 'medium',
  due_date DATE,
  submitted_date DATE,
  reviewed_date DATE,
  submitted_by UUID REFERENCES users(id) ON DELETE SET NULL,
  reviewed_by UUID REFERENCES users(id) ON DELETE SET NULL,
  csi_division VARCHAR(20),
  revision_number INTEGER DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  created_by UUID REFERENCES users(id) ON DELETE SET NULL,
  updated_at TIMESTAMPTZ,
  updated_by UUID REFERENCES users(id) ON DELETE SET NULL
);

-- Drawings
CREATE TABLE drawings (
  id SERIAL PRIMARY KEY,
  project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
  title VARCHAR(100) NOT NULL,
  drawing_number VARCHAR(50) NOT NULL,
  description TEXT,
  drawing_type VARCHAR(50),
  discipline VARCHAR(50),
  revision VARCHAR(20),
  revision_date DATE,
  scale VARCHAR(30),
  sheet_size VARCHAR(20),
  status VARCHAR(30) DEFAULT 'current',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  created_by UUID REFERENCES users(id) ON DELETE SET NULL,
  updated_at TIMESTAMPTZ,
  updated_by UUID REFERENCES users(id) ON DELETE SET NULL
);

-- Specifications
CREATE TABLE specifications (
  id SERIAL PRIMARY KEY,
  project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
  title VARCHAR(100) NOT NULL,
  spec_number VARCHAR(50) NOT NULL,
  description TEXT,
  csi_division VARCHAR(20),
  csi_subdivision VARCHAR(20),
  revision VARCHAR(20),
  revision_date DATE,
  status VARCHAR(30) DEFAULT 'current',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  created_by UUID REFERENCES users(id) ON DELETE SET NULL,
  updated_at TIMESTAMPTZ,
  updated_by UUID REFERENCES users(id) ON DELETE SET NULL
);

-- Permits
CREATE TABLE permits (
  id SERIAL PRIMARY KEY,
  project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
  title VARCHAR(100) NOT NULL,
  permit_number VARCHAR(50),
  description TEXT,
  permit_type VARCHAR(50),
  issuing_authority VARCHAR(100),
  application_date DATE,
  issue_date DATE,
  expiration_date DATE,
  status VARCHAR(30) DEFAULT 'pending',
  fee_amount DECIMAL(14, 2),
  notes TEXT,
  assigned_to UUID REFERENCES users(id) ON DELETE SET NULL,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  created_by UUID REFERENCES users(id) ON DELETE SET NULL,
  updated_at TIMESTAMPTZ,
  updated_by UUID REFERENCES users(id) ON DELETE SET NULL
);

-- Meeting Minutes
CREATE TABLE meeting_minutes (
  id SERIAL PRIMARY KEY,
  project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
  title VARCHAR(100) NOT NULL,
  meeting_date TIMESTAMPTZ NOT NULL,
  location VARCHAR(100),
  meeting_type VARCHAR(50),
  attendees TEXT,
  agenda TEXT,
  minutes TEXT,
  next_meeting_date TIMESTAMPTZ,
  status VARCHAR(30) DEFAULT 'draft',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  created_by UUID REFERENCES users(id) ON DELETE SET NULL,
  updated_at TIMESTAMPTZ,
  updated_by UUID REFERENCES users(id) ON DELETE SET NULL
);

-- Transmittals
CREATE TABLE transmittals (
  id SERIAL PRIMARY KEY,
  project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
  transmittal_number VARCHAR(50) NOT NULL,
  title VARCHAR(100) NOT NULL,
  from_company_id INTEGER REFERENCES companies(id),
  from_user_id UUID REFERENCES users(id) ON DELETE SET NULL,
  to_company_id INTEGER REFERENCES companies(id),
  to_user_id UUID REFERENCES users(id) ON DELETE SET NULL,
  date_sent DATE,
  delivery_method VARCHAR(50),
  reason_for_transmittal TEXT,
  remarks TEXT,
  status VARCHAR(30) DEFAULT 'sent',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  created_by UUID REFERENCES users(id) ON DELETE SET NULL,
  updated_at TIMESTAMPTZ,
  updated_by UUID REFERENCES users(id) ON DELETE SET NULL
);

-- Transmittal Items
CREATE TABLE transmittal_items (
  id SERIAL PRIMARY KEY,
  transmittal_id INTEGER REFERENCES transmittals(id) ON DELETE CASCADE,
  description VARCHAR(255) NOT NULL,
  record_type VARCHAR(50),
  record_id INTEGER,
  copies INTEGER DEFAULT 1,
  status VARCHAR(30),
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- FIELD MODULE
-- Daily Reports
CREATE TABLE daily_reports (
  id SERIAL PRIMARY KEY,
  project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
  report_date DATE NOT NULL,
  weather_conditions VARCHAR(100),
  temperature_low INTEGER,
  temperature_high INTEGER,
  precipitation VARCHAR(30),
  wind_speed VARCHAR(30),
  work_performed TEXT,
  issues_encountered TEXT,
  visitors TEXT,
  safety_incidents TEXT,
  delay_factors TEXT,
  status VARCHAR(30) DEFAULT 'draft',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  created_by UUID REFERENCES users(id) ON DELETE SET NULL,
  updated_at TIMESTAMPTZ,
  updated_by UUID REFERENCES users(id) ON DELETE SET NULL
);

-- Daily Report Labor
CREATE TABLE daily_report_labor (
  id SERIAL PRIMARY KEY,
  daily_report_id INTEGER REFERENCES daily_reports(id) ON DELETE CASCADE,
  company_id INTEGER REFERENCES companies(id),
  trade VARCHAR(100),
  workers_count INTEGER NOT NULL,
  hours_worked DECIMAL(6, 2) NOT NULL,
  work_area TEXT,
  notes TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Daily Report Equipment
CREATE TABLE daily_report_equipment (
  id SERIAL PRIMARY KEY,
  daily_report_id INTEGER REFERENCES daily_reports(id) ON DELETE CASCADE,
  equipment_type VARCHAR(100) NOT NULL,
  quantity INTEGER NOT NULL,
  hours_used DECIMAL(6, 2),
  work_area TEXT,
  notes TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Photo Library
CREATE TABLE photos (
  id SERIAL PRIMARY KEY,
  project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
  title VARCHAR(100) NOT NULL,
  description TEXT,
  photo_url TEXT NOT NULL,
  thumbnail_url TEXT,
  location VARCHAR(100),
  taken_at TIMESTAMPTZ,
  latitude DECIMAL(10, 8),
  longitude DECIMAL(11, 8),
  tags TEXT[],
  created_at TIMESTAMPTZ DEFAULT NOW(),
  created_by UUID REFERENCES users(id) ON DELETE SET NULL,
  updated_at TIMESTAMPTZ,
  updated_by UUID REFERENCES users(id) ON DELETE SET NULL
);

-- Schedule Items
CREATE TABLE schedule_items (
  id SERIAL PRIMARY KEY,
  project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
  title VARCHAR(100) NOT NULL,
  description TEXT,
  start_date DATE NOT NULL,
  end_date DATE NOT NULL,
  actual_start_date DATE,
  actual_end_date DATE,
  duration INTEGER GENERATED ALWAYS AS (end_date - start_date) STORED,
  completion_percentage INTEGER DEFAULT 0,
  phase VARCHAR(50),
  wbs_code VARCHAR(50),
  predecessor_ids INTEGER[],
  successor_ids INTEGER[],
  assigned_to UUID REFERENCES users(id) ON DELETE SET NULL,
  company_id INTEGER REFERENCES companies(id),
  critical_path BOOLEAN DEFAULT FALSE,
  milestone BOOLEAN DEFAULT FALSE,
  status VARCHAR(30) DEFAULT 'not_started',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  created_by UUID REFERENCES users(id) ON DELETE SET NULL,
  updated_at TIMESTAMPTZ,
  updated_by UUID REFERENCES users(id) ON DELETE SET NULL
);

-- Checklists
CREATE TABLE checklists (
  id SERIAL PRIMARY KEY,
  project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
  title VARCHAR(100) NOT NULL,
  description TEXT,
  checklist_type VARCHAR(50),
  location VARCHAR(100),
  status VARCHAR(30) DEFAULT 'open',
  due_date DATE,
  completed_date DATE,
  assigned_to UUID REFERENCES users(id) ON DELETE SET NULL,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  created_by UUID REFERENCES users(id) ON DELETE SET NULL,
  updated_at TIMESTAMPTZ,
  updated_by UUID REFERENCES users(id) ON DELETE SET NULL
);

-- Checklist Items
CREATE TABLE checklist_items (
  id SERIAL PRIMARY KEY,
  checklist_id INTEGER REFERENCES checklists(id) ON DELETE CASCADE,
  description TEXT NOT NULL,
  sort_order INTEGER,
  completed BOOLEAN DEFAULT FALSE,
  completed_at TIMESTAMPTZ,
  completed_by UUID REFERENCES users(id) ON DELETE SET NULL,
  notes TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Punchlist
CREATE TABLE punchlist_items (
  id SERIAL PRIMARY KEY,
  project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
  title VARCHAR(100) NOT NULL,
  description TEXT,
  location VARCHAR(100),
  area VARCHAR(50),
  priority priority_level DEFAULT 'medium',
  status punchlist_status DEFAULT 'open',
  due_date DATE,
  assigned_to UUID REFERENCES users(id) ON DELETE SET NULL,
  responsible_company_id INTEGER REFERENCES companies(id),
  identification_date DATE,
  completion_date DATE,
  verification_date DATE,
  verified_by UUID REFERENCES users(id) ON DELETE SET NULL,
  cost_impact BOOLEAN DEFAULT FALSE,
  cost_amount DECIMAL(14, 2),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  created_by UUID REFERENCES users(id) ON DELETE SET NULL,
  updated_at TIMESTAMPTZ,
  updated_by UUID REFERENCES users(id) ON DELETE SET NULL
);

-- Pull Planning
CREATE TABLE pull_planning_sessions (
  id SERIAL PRIMARY KEY,
  project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
  title VARCHAR(100) NOT NULL,
  description TEXT,
  start_date DATE,
  end_date DATE,
  location VARCHAR(100),
  facilitator UUID REFERENCES users(id) ON DELETE SET NULL,
  status VARCHAR(30) DEFAULT 'planned',
  notes TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  created_by UUID REFERENCES users(id) ON DELETE SET NULL,
  updated_at TIMESTAMPTZ,
  updated_by UUID REFERENCES users(id) ON DELETE SET NULL
);

-- Pull Planning Items (sticky notes)
CREATE TABLE pull_planning_items (
  id SERIAL PRIMARY KEY,
  session_id INTEGER REFERENCES pull_planning_sessions(id) ON DELETE CASCADE,
  title VARCHAR(100) NOT NULL,
  description TEXT,
  duration INTEGER,
  manpower INTEGER,
  company_id INTEGER REFERENCES companies(id),
  assigned_to UUID REFERENCES users(id) ON DELETE SET NULL,
  color VARCHAR(20),
  x_position INTEGER,
  y_position INTEGER,
  prerequisites INTEGER[],
  successors INTEGER[],
  created_at TIMESTAMPTZ DEFAULT NOW(),
  created_by UUID REFERENCES users(id) ON DELETE SET NULL,
  updated_at TIMESTAMPTZ,
  updated_by UUID REFERENCES users(id) ON DELETE SET NULL
);

-- SAFETY MODULE
-- Safety Observations
CREATE TABLE safety_observations (
  id SERIAL PRIMARY KEY,
  project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
  title VARCHAR(100) NOT NULL,
  description TEXT,
  location VARCHAR(100),
  observation_type VARCHAR(50),
  severity VARCHAR(30),
  action_taken TEXT,
  reported_by UUID REFERENCES users(id) ON DELETE SET NULL,
  observation_date TIMESTAMPTZ,
  status VARCHAR(30) DEFAULT 'open',
  resolution_date TIMESTAMPTZ,
  follow_up_required BOOLEAN DEFAULT FALSE,
  follow_up_date TIMESTAMPTZ,
  follow_up_by UUID REFERENCES users(id) ON DELETE SET NULL,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  created_by UUID REFERENCES users(id) ON DELETE SET NULL,
  updated_at TIMESTAMPTZ,
  updated_by UUID REFERENCES users(id) ON DELETE SET NULL
);

-- PreTask Plans
CREATE TABLE pretask_plans (
  id SERIAL PRIMARY KEY,
  project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
  title VARCHAR(100) NOT NULL,
  description TEXT,
  task_date DATE,
  location VARCHAR(100),
  company_id INTEGER REFERENCES companies(id),
  foreman VARCHAR(100),
  crew_size INTEGER,
  equipment_used TEXT,
  hazards_identified TEXT,
  control_measures TEXT,
  ppe_required TEXT[],
  emergency_procedures TEXT,
  status VARCHAR(30) DEFAULT 'draft',
  approved BOOLEAN DEFAULT FALSE,
  approved_by UUID REFERENCES users(id) ON DELETE SET NULL,
  approved_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  created_by UUID REFERENCES users(id) ON DELETE SET NULL,
  updated_at TIMESTAMPTZ,
  updated_by UUID REFERENCES users(id) ON DELETE SET NULL
);

-- Job Hazard Analysis
CREATE TABLE job_hazard_analysis (
  id SERIAL PRIMARY KEY,
  project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
  title VARCHAR(100) NOT NULL,
  description TEXT,
  job_task VARCHAR(100),
  trade VARCHAR(50),
  location VARCHAR(100),
  required_ppe TEXT[],
  required_training TEXT[],
  required_permits TEXT[],
  status VARCHAR(30) DEFAULT 'draft',
  review_date DATE,
  approved BOOLEAN DEFAULT FALSE,
  approved_by UUID REFERENCES users(id) ON DELETE SET NULL,
  approved_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  created_by UUID REFERENCES users(id) ON DELETE SET NULL,
  updated_at TIMESTAMPTZ,
  updated_by UUID REFERENCES users(id) ON DELETE SET NULL
);

-- JHA Steps
CREATE TABLE jha_steps (
  id SERIAL PRIMARY KEY,
  jha_id INTEGER REFERENCES job_hazard_analysis(id) ON DELETE CASCADE,
  step_number INTEGER,
  task_description TEXT NOT NULL,
  hazards TEXT,
  control_measures TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Employee Orientations
CREATE TABLE employee_orientations (
  id SERIAL PRIMARY KEY,
  project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
  employee_name VARCHAR(100) NOT NULL,
  company_id INTEGER REFERENCES companies(id),
  orientation_date DATE,
  orientation_type VARCHAR(50),
  orientation_by UUID REFERENCES users(id) ON DELETE SET NULL,
  topics_covered TEXT[],
  test_score INTEGER,
  badge_issued BOOLEAN DEFAULT FALSE,
  badge_number VARCHAR(50),
  expiration_date DATE,
  status VARCHAR(30) DEFAULT 'completed',
  notes TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  created_by UUID REFERENCES users(id) ON DELETE SET NULL,
  updated_at TIMESTAMPTZ,
  updated_by UUID REFERENCES users(id) ON DELETE SET NULL
);

-- CONTRACTS MODULE
-- Prime Contracts
CREATE TABLE prime_contracts (
  id SERIAL PRIMARY KEY,
  project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
  title VARCHAR(100) NOT NULL,
  contract_number VARCHAR(50),
  description TEXT,
  contract_type contract_type NOT NULL,
  execution_date DATE,
  start_date DATE,
  substantial_completion_date DATE,
  final_completion_date DATE,
  owner_company_id INTEGER REFERENCES companies(id),
  contractor_company_id INTEGER REFERENCES companies(id),
  original_amount DECIMAL(14, 2),
  current_amount DECIMAL(14, 2),
  status VARCHAR(30) DEFAULT 'draft',
  payment_terms TEXT,
  retainage_percentage DECIMAL(5, 2),
  insurance_requirements TEXT,
  warranty_terms TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  created_by UUID REFERENCES users(id) ON DELETE SET NULL,
  updated_at TIMESTAMPTZ,
  updated_by UUID REFERENCES users(id) ON DELETE SET NULL
);

-- Subcontracts
CREATE TABLE subcontracts (
  id SERIAL PRIMARY KEY,
  project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
  title VARCHAR(100) NOT NULL,
  contract_number VARCHAR(50),
  description TEXT,
  contract_type contract_type NOT NULL,
  execution_date DATE,
  start_date DATE,
  completion_date DATE,
  contractor_company_id INTEGER REFERENCES companies(id),
  subcontractor_company_id INTEGER REFERENCES companies(id),
  scope_of_work TEXT,
  csi_codes TEXT[],
  original_amount DECIMAL(14, 2),
  current_amount DECIMAL(14, 2),
  status VARCHAR(30) DEFAULT 'draft',
  payment_terms TEXT,
  retainage_percentage DECIMAL(5, 2),
  insurance_requirements TEXT,
  warranty_terms TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  created_by UUID REFERENCES users(id) ON DELETE SET NULL,
  updated_at TIMESTAMPTZ,
  updated_by UUID REFERENCES users(id) ON DELETE SET NULL
);

-- Professional Service Agreements
CREATE TABLE professional_service_agreements (
  id SERIAL PRIMARY KEY,
  project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
  title VARCHAR(100) NOT NULL,
  agreement_number VARCHAR(50),
  description TEXT,
  service_type VARCHAR(50),
  execution_date DATE,
  start_date DATE,
  end_date DATE,
  client_company_id INTEGER REFERENCES companies(id),
  provider_company_id INTEGER REFERENCES companies(id),
  scope_of_services TEXT,
  fee_type VARCHAR(30),
  original_amount DECIMAL(14, 2),
  current_amount DECIMAL(14, 2),
  status VARCHAR(30) DEFAULT 'draft',
  payment_terms TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  created_by UUID REFERENCES users(id) ON DELETE SET NULL,
  updated_at TIMESTAMPTZ,
  updated_by UUID REFERENCES users(id) ON DELETE SET NULL
);

-- Lien Waivers
CREATE TABLE lien_waivers (
  id SERIAL PRIMARY KEY,
  project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
  title VARCHAR(100) NOT NULL,
  waiver_type VARCHAR(50),
  company_id INTEGER REFERENCES companies(id),
  contract_id INTEGER,
  contract_type VARCHAR(30),
  payment_amount DECIMAL(14, 2),
  payment_date DATE,
  through_date DATE,
  status VARCHAR(30) DEFAULT 'draft',
  signed BOOLEAN DEFAULT FALSE,
  signed_by VARCHAR(100),
  signed_date DATE,
  notarized BOOLEAN DEFAULT FALSE,
  notary_name VARCHAR(100),
  notary_date DATE,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  created_by UUID REFERENCES users(id) ON DELETE SET NULL,
  updated_at TIMESTAMPTZ,
  updated_by UUID REFERENCES users(id) ON DELETE SET NULL
);

-- Certificates of Insurance
CREATE TABLE certificates_of_insurance (
  id SERIAL PRIMARY KEY,
  project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
  company_id INTEGER REFERENCES companies(id) NOT NULL,
  title VARCHAR(100) NOT NULL,
  insurance_provider VARCHAR(100),
  policy_number VARCHAR(50),
  policy_type VARCHAR(50),
  effective_date DATE,
  expiration_date DATE,
  coverage_amount DECIMAL(14, 2),
  additional_insureds TEXT[],
  status VARCHAR(30) DEFAULT 'active',
  notes TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  created_by UUID REFERENCES users(id) ON DELETE SET NULL,
  updated_at TIMESTAMPTZ,
  updated_by UUID REFERENCES users(id) ON DELETE SET NULL
);

-- Letters of Intent
CREATE TABLE letters_of_intent (
  id SERIAL PRIMARY KEY,
  project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
  title VARCHAR(100) NOT NULL,
  to_company_id INTEGER REFERENCES companies(id),
  from_company_id INTEGER REFERENCES companies(id),
  issue_date DATE,
  expiration_date DATE,
  scope_of_work TEXT,
  estimated_value DECIMAL(14, 2),
  not_to_exceed_amount DECIMAL(14, 2),
  status VARCHAR(30) DEFAULT 'draft',
  notes TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  created_by UUID REFERENCES users(id) ON DELETE SET NULL,
  updated_at TIMESTAMPTZ,
  updated_by UUID REFERENCES users(id) ON DELETE SET NULL
);

-- COST MODULE
-- Budget
CREATE TABLE budget_line_items (
  id SERIAL PRIMARY KEY,
  project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
  cost_code VARCHAR(50),
  description VARCHAR(255) NOT NULL,
  csi_division VARCHAR(20),
  csi_subdivision VARCHAR(20),
  original_amount DECIMAL(14, 2) NOT NULL,
  current_amount DECIMAL(14, 2) NOT NULL,
  committed_amount DECIMAL(14, 2) DEFAULT 0,
  actual_amount DECIMAL(14, 2) DEFAULT 0,
  projected_amount DECIMAL(14, 2),
  variance_amount DECIMAL(14, 2) GENERATED ALWAYS AS (current_amount - COALESCE(actual_amount, 0) - COALESCE(projected_amount, 0)) STORED,
  notes TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  created_by UUID REFERENCES users(id) ON DELETE SET NULL,
  updated_at TIMESTAMPTZ,
  updated_by UUID REFERENCES users(id) ON DELETE SET NULL
);

-- Invoices (AIA G702/G703)
CREATE TABLE invoices (
  id SERIAL PRIMARY KEY,
  project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
  invoice_number VARCHAR(50) NOT NULL,
  title VARCHAR(100) NOT NULL,
  contract_id INTEGER,
  contract_type VARCHAR(30),
  company_id INTEGER REFERENCES companies(id),
  from_date DATE,
  to_date DATE,
  issue_date DATE,
  due_date DATE,
  previous_amount DECIMAL(14, 2) DEFAULT 0,
  current_amount DECIMAL(14, 2) DEFAULT 0,
  total_completed DECIMAL(14, 2) GENERATED ALWAYS AS (previous_amount + current_amount) STORED,
  retainage_percentage DECIMAL(5, 2),
  retainage_amount DECIMAL(14, 2),
  total_earned_less_retainage DECIMAL(14, 2),
  less_previous_certificates DECIMAL(14, 2),
  current_payment_due DECIMAL(14, 2),
  status VARCHAR(30) DEFAULT 'draft',
  approved BOOLEAN DEFAULT FALSE,
  approved_by UUID REFERENCES users(id) ON DELETE SET NULL,
  approved_date DATE,
  paid BOOLEAN DEFAULT FALSE,
  paid_date DATE,
  check_number VARCHAR(50),
  notes TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  created_by UUID REFERENCES users(id) ON DELETE SET NULL,-- Construction Project Management Database Schema
-- Supabase PostgreSQL Schema

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Enable pgcrypto for password hashing
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Enable trigram search
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- ENUMS
CREATE TYPE user_role AS ENUM (
  'owner',
  'owner_rep',
  'general_contractor',
  'subcontractor',
  'design_team'
);

CREATE TYPE company_type AS ENUM (
  'owner',
  'general_contractor',
  'subcontractor',
  'design_firm',
  'consultant',
  'vendor'
);

CREATE TYPE contract_type AS ENUM (
  'gmp',
  'cost_plus',
  'lump_sum',
  'cmar',
  'time_and_materials'
);

CREATE TYPE rfi_status AS ENUM (
  'draft',
  'submitted',
  'in_review',
  'answered',
  'closed'
);

CREATE TYPE submittal_status AS ENUM (
  'draft',
  'submitted',
  'in_review',
  'approved',
  'approved_as_noted',
  'revise_and_resubmit',
  'rejected',
  'closed'
);

CREATE TYPE change_order_status AS ENUM (
  'draft',
  'submitted',
  'in_review',
  'approved',
  'rejected',
  'void'
);

CREATE TYPE punchlist_status AS ENUM (
  'open',
  'in_progress',
  'completed',
  'verified'
);

CREATE TYPE priority_level AS ENUM (
  'low',
  'medium',
  'high',
  'critical'
);

-- Main Tables

-- Projects Table
CREATE TABLE projects (
  id SERIAL PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  address TEXT,
  city VARCHAR(50),
  state VARCHAR(30),
  zip VARCHAR(20),
  country VARCHAR(50) DEFAULT 'USA',
  description TEXT,
  start_date DATE,
  end_date DATE,
  status VARCHAR(30) DEFAULT 'active',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  owner_company_id INTEGER,
  gc_company_id INTEGER,
  primary_contact_id UUID
);

-- Companies Table
CREATE TABLE companies (
  id SERIAL PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  type company_type NOT NULL,
  address TEXT,
  city VARCHAR(50),
  state VARCHAR(30),
  zip VARCHAR(20),
  country VARCHAR(50) DEFAULT 'USA',
  phone VARCHAR(30),
  email VARCHAR(