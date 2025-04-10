import os
from app.config import Config, DevelopmentConfig, TestingConfig, ProductionConfig

def get_config():
    """Return the appropriate configuration object based on environment variable"""
    config_map = {
        'development': DevelopmentConfig,
        'testing': TestingConfig,
        'production': ProductionConfig,
        'default': Config
    }
    
    env = os.environ.get('FLASK_ENV', 'default')
    return config_map.get(env, Config)