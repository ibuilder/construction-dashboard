// Supabase initialization and configuration
const SUPABASE_URL = 'https://your-project-url.supabase.co';
const SUPABASE_ANON_KEY = 'your-anon-key';

// Initialize the Supabase client
const supabase = supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

// User roles
const USER_ROLES = {
  OWNER: 'owner',
  OWNER_REP: 'owner_rep',
  GENERAL_CONTRACTOR: 'general_contractor',
  SUBCONTRACTOR: 'subcontractor',
  DESIGN_TEAM: 'design_team'
};

// Permission levels
const PERMISSION_LEVELS = {
  NONE: 0,
  READ: 1,
  COMMENT: 2,
  EDIT: 3,
  CREATE: 4,
  DELETE: 5,
  ADMIN: 6
};

// Module IDs for permission mapping
const MODULES = {
  PRECONSTRUCTION: 'preconstruction',
  ENGINEERING: 'engineering',
  FIELD: 'field',
  SAFETY: 'safety',
  CONTRACTS: 'contracts',
  COST: 'cost',
  BIM: 'bim',
  CLOSEOUT: 'closeout',
  SETTINGS: 'settings',
  REPORTS: 'reports'
};

// Default role permissions mapping
const DEFAULT_ROLE_PERMISSIONS = {
  [USER_ROLES.OWNER]: {
    [MODULES.PRECONSTRUCTION]: PERMISSION_LEVELS.ADMIN,
    [MODULES.ENGINEERING]: PERMISSION_LEVELS.ADMIN,
    [MODULES.FIELD]: PERMISSION_LEVELS.ADMIN,
    [MODULES.SAFETY]: PERMISSION_LEVELS.ADMIN,
    [MODULES.CONTRACTS]: PERMISSION_LEVELS.ADMIN,
    [MODULES.COST]: PERMISSION_LEVELS.ADMIN,
    [MODULES.BIM]: PERMISSION_LEVELS.ADMIN,
    [MODULES.CLOSEOUT]: PERMISSION_LEVELS.ADMIN,
    [MODULES.SETTINGS]: PERMISSION_LEVELS.ADMIN,
    [MODULES.REPORTS]: PERMISSION_LEVELS.ADMIN
  },
  [USER_ROLES.OWNER_REP]: {
    [MODULES.PRECONSTRUCTION]: PERMISSION_LEVELS.CREATE,
    [MODULES.ENGINEERING]: PERMISSION_LEVELS.CREATE,
    [MODULES.FIELD]: PERMISSION_LEVELS.CREATE,
    [MODULES.SAFETY]: PERMISSION_LEVELS.CREATE,
    [MODULES.CONTRACTS]: PERMISSION_LEVELS.CREATE,
    [MODULES.COST]: PERMISSION_LEVELS.CREATE,
    [MODULES.BIM]: PERMISSION_LEVELS.EDIT,
    [MODULES.CLOSEOUT]: PERMISSION_LEVELS.CREATE,
    [MODULES.SETTINGS]: PERMISSION_LEVELS.EDIT,
    [MODULES.REPORTS]: PERMISSION_LEVELS.CREATE
  },
  [USER_ROLES.GENERAL_CONTRACTOR]: {
    [MODULES.PRECONSTRUCTION]: PERMISSION_LEVELS.CREATE,
    [MODULES.ENGINEERING]: PERMISSION_LEVELS.CREATE,
    [MODULES.FIELD]: PERMISSION_LEVELS.CREATE,
    [MODULES.SAFETY]: PERMISSION_LEVELS.CREATE,
    [MODULES.CONTRACTS]: PERMISSION_LEVELS.EDIT,
    [MODULES.COST]: PERMISSION_LEVELS.EDIT,
    [MODULES.BIM]: PERMISSION_LEVELS.EDIT,
    [MODULES.CLOSEOUT]: PERMISSION_LEVELS.CREATE,
    [MODULES.SETTINGS]: PERMISSION_LEVELS.COMMENT,
    [MODULES.REPORTS]: PERMISSION_LEVELS.CREATE
  },
  [USER_ROLES.SUBCONTRACTOR]: {
    [MODULES.PRECONSTRUCTION]: PERMISSION_LEVELS.COMMENT,
    [MODULES.ENGINEERING]: PERMISSION_LEVELS.COMMENT,
    [MODULES.FIELD]: PERMISSION_LEVELS.COMMENT,
    [MODULES.SAFETY]: PERMISSION_LEVELS.EDIT,
    [MODULES.CONTRACTS]: PERMISSION_LEVELS.READ,
    [MODULES.COST]: PERMISSION_LEVELS.READ,
    [MODULES.BIM]: PERMISSION_LEVELS.COMMENT,
    [MODULES.CLOSEOUT]: PERMISSION_LEVELS.COMMENT,
    [MODULES.SETTINGS]: PERMISSION_LEVELS.READ,
    [MODULES.REPORTS]: PERMISSION_LEVELS.READ
  },
  [USER_ROLES.DESIGN_TEAM]: {
    [MODULES.PRECONSTRUCTION]: PERMISSION_LEVELS.COMMENT,
    [MODULES.ENGINEERING]: PERMISSION_LEVELS.CREATE,
    [MODULES.FIELD]: PERMISSION_LEVELS.COMMENT,
    [MODULES.SAFETY]: PERMISSION_LEVELS.READ,
    [MODULES.CONTRACTS]: PERMISSION_LEVELS.READ,
    [MODULES.COST]: PERMISSION_LEVELS.COMMENT,
    [MODULES.BIM]: PERMISSION_LEVELS.CREATE,
    [MODULES.CLOSEOUT]: PERMISSION_LEVELS.COMMENT,
    [MODULES.SETTINGS]: PERMISSION_LEVELS.READ,
    [MODULES.REPORTS]: PERMISSION_LEVELS.READ
  }
};

// Check if user has permission for a specific action on a module
async function hasPermission(userId, moduleId, requiredPermissionLevel) {
  try {
    // Get user's role
    const { data: userData, error: userError } = await supabase
      .from('users')
      .select('role')
      .eq('id', userId)
      .single();
    
    if (userError) throw userError;
    
    // Get custom permissions for this user if any
    const { data: customPermissions, error: permissionError } = await supabase
      .from('user_permissions')
      .select('permission_level')
      .eq('user_id', userId)
      .eq('module_id', moduleId)
      .single();
    
    // Use custom permission if exists, otherwise fallback to role-based permission
    let userPermissionLevel;
    
    if (!permissionError && customPermissions) {
      userPermissionLevel = customPermissions.permission_level;
    } else {
      userPermissionLevel = DEFAULT_ROLE_PERMISSIONS[userData.role][moduleId];
    }
    
    return userPermissionLevel >= requiredPermissionLevel;
  } catch (error) {
    console.error('Permission check error:', error);
    return false;
  }
}

// Initialize database schema if not exists
async function initializeDatabase() {
  // This function would run the necessary SQL to create tables
  // In production, you would use migrations rather than this approach
  console.log('Initializing database schema...');
  
  // Example of creating a table (in production you'd use migrations)
  /*
  const { error } = await supabase.rpc('init_schema');
  if (error) {
    console.error('Failed to initialize schema:', error);
  } else {
    console.log('Schema initialized successfully');
  }
  */
}

// Export functions and constants
export {
  supabase,
  USER_ROLES,
  PERMISSION_LEVELS,
  MODULES,
  hasPermission,
  initializeDatabase
};