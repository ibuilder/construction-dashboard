from flask import current_app, g
import os
import json

# Default feature flags
DEFAULT_FLAGS = {
    'enable_blockchain': False,
    'enable_mobile_sync': True,
    'enable_push_notifications': False,
    'enable_weather_api': True,
    'enable_analytics': True,
    'show_cost_module': True,
    'show_safety_module': True,
    'show_rfis_module': True,
    'show_submittals_module': True,
    'enable_file_versioning': False
}

# Global variable to store flags
FEATURE_FLAGS = {}

def load_feature_flags():
    """Load feature flags from config file or environment"""
    global FEATURE_FLAGS
    
    # Start with defaults
    FEATURE_FLAGS = DEFAULT_FLAGS.copy()
    
    # Check for JSON config file
    config_file = os.environ.get('FEATURE_FLAGS_FILE') or 'instance/feature_flags.json'
    
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r') as f:
                file_flags = json.load(f)
                FEATURE_FLAGS.update(file_flags)
                current_app.logger.info(f"Loaded feature flags from {config_file}")
        except Exception as e:
            current_app.logger.error(f"Error loading feature flags from {config_file}: {e}")
    
    # Override with environment variables (ENV_FEATURE_FLAG_NAME)
    for flag in FEATURE_FLAGS.keys():
        env_var = f"FEATURE_{flag.upper()}"
        if env_var in os.environ:
            # Convert string to boolean if needed
            if isinstance(FEATURE_FLAGS[flag], bool):
                FEATURE_FLAGS[flag] = os.environ.get(env_var).lower() in ('true', '1', 'yes')
            else:
                FEATURE_FLAGS[flag] = os.environ.get(env_var)
    
    current_app.logger.debug(f"Active feature flags: {FEATURE_FLAGS}")

def is_enabled(flag_name):
    """Check if a feature flag is enabled"""
    if not FEATURE_FLAGS:
        load_feature_flags()
    
    return FEATURE_FLAGS.get(flag_name, False)

def get_all_flags():
    """Get all feature flags"""
    if not FEATURE_FLAGS:
        load_feature_flags()
    
    return FEATURE_FLAGS

def is_feature_enabled(feature_name):
    """Check if a feature flag is enabled
    
    Args:
        feature_name (str): Name of the feature to check
        
    Returns:
        bool: True if feature is enabled, False otherwise
    """
    # First check if we have cached the flags in the request context
    if not hasattr(g, 'feature_flags'):
        g.feature_flags = current_app.config.get('FEATURE_FLAGS', {})
    
    # Return feature status (default to False if not found)
    return g.feature_flags.get(feature_name, False)

def get_all_features():
    """Get all feature flags
    
    Returns:
        dict: Dictionary of all feature flags and their status
    """
    if not hasattr(g, 'feature_flags'):
        g.feature_flags = current_app.config.get('FEATURE_FLAGS', {})
    
    return g.feature_flags

def update_feature(feature_name, status):
    """Update a feature flag status (admin only)
    
    Args:
        feature_name (str): Name of the feature to update
        status (bool): New status for the feature
        
    Returns:
        bool: True if update was successful
    """
    # Only allow updating if feature exists in config
    config_flags = current_app.config.get('FEATURE_FLAGS', {})
    
    if feature_name not in config_flags:
        return False
    
    # Update feature flag in config
    config_flags[feature_name] = bool(status)
    current_app.config['FEATURE_FLAGS'] = config_flags
    
    # Also update in request context if it exists
    if hasattr(g, 'feature_flags'):
        g.feature_flags[feature_name] = bool(status)
    
    return True