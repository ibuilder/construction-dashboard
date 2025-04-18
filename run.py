from app import create_app
from app.config_factory import get_config
from app.cli import register_commands

def main():
    # Get appropriate config based on environment
    config = get_config()
    app = create_app(config)
    register_commands(app)
    
    app.run(host='0.0.0.0')

if __name__ == '__main__':
    main()