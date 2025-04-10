# Construction Dashboard

A comprehensive Flask-based web application for construction project management. This dashboard provides tools for tracking projects, managing documents, reporting on field activities, and coordinating team communications.

## Features

- **Project Management**: Track and manage construction projects
- **Document Control**: Manage RFIs, submittals, and other project documents
- **Field Reporting**: Daily reports, safety observations, and incident reporting
- **Cost Control**: Budget tracking, change orders, and invoice management
- **Mobile Integration**: Synchronize data with mobile devices for field use
- **User Management**: Role-based access control
- **Analytics**: Project performance metrics and dashboards
- **API**: RESTful API for integration with other systems
- **Blockchain Integration**: Optional document verification using blockchain technology

## Technology Stack

- **Backend**: Flask, Python 3.9+
- **Database**: SQLAlchemy ORM with PostgreSQL (production) or SQLite (development)
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Authentication**: Flask-Login, JSON Web Tokens
- **Task Processing**: Celery with Redis
- **Caching**: Redis or in-memory cache
- **Documentation**: Swagger/OpenAPI
- **Monitoring**: Custom monitoring system
- **Blockchain**: Optional Web3 integration for document verification

## Project Structure

```
construction-dashboard/
├── app/                            # Application package
│   ├── __init__.py                 # Application factory
│   ├── config.py                   # Configuration settings
│   ├── config_factory.py           # Configuration selector
│   ├── extensions.py               # Flask extensions
│   ├── api/                        # API package
│   │   ├── __init__.py
│   │   ├── routes.py               # API routes
│   │   ├── mobile_routes.py        # Mobile API routes
│   │   └── swagger.py              # API documentation
│   ├── auth/                       # Authentication package
│   │   ├── __init__.py
│   │   ├── routes.py               # Auth routes
│   │   ├── forms.py                # Auth forms
│   │   └── utils.py                # Auth utilities
│   ├── dashboard/                  # Dashboard views
│   │   ├── __init__.py
│   │   ├── forms.py                # Dashboard forms
│   │   └── routes.py               # Dashboard routes
│   ├── projects/                   # Projects module
│   │   ├── __init__.py
│   │   ├── forms.py                # Project forms
│   │   └── routes.py               # Project routes
│   ├── admin/                      # Admin module
│   │   ├── __init__.py
│   │   └── routes.py               # Admin routes
│   ├── errors/                     # Error handlers
│   │   ├── __init__.py
│   │   └── handlers.py             # Error handling routes
│   ├── models/                     # Database models
│   │   ├── __init__.py
│   │   ├── user.py                 # User model
│   │   ├── project.py              # Project model
│   │   ├── engineering.py          # Engineering models (RFI, Submittal)
│   │   ├── field.py                # Field models (DailyReport)
│   │   ├── safety.py               # Safety models
│   │   └── cost.py                 # Cost models (Budget, ChangeOrder)
│   ├── web3/                       # Blockchain integration
│   │   ├── __init__.py
│   │   └── contracts.py            # Smart contract interfaces
│   ├── static/                     # Static files
│   │   ├── css/                    # CSS files
│   │   ├── js/                     # JavaScript files
│   │   │   ├── dashboard.js
│   │   │   └── web3.js             # Blockchain integration
│   │   └── vendor/                 # Third-party libraries
│   ├── templates/                  # Jinja2 templates
│   │   ├── auth/                   # Auth templates
│   │   ├── dashboard/              # Dashboard templates
│   │   ├── projects/               # Project templates
│   │   ├── layout.html             # Base template
│   │   └── admin/                  # Admin templates
│   ├── uploads/                    # User uploads
│   │   ├── documents/              # Document uploads
│   │   ├── photos/                 # Photo uploads
│   │   └── temp/                   # Temporary files
│   └── utils/                      # Utility modules
│       ├── security.py             # Security utilities
│       ├── scheduler.py            # Task scheduler
│       ├── backup.py               # Backup utilities
│       ├── feature_flags.py        # Feature flag utilities
│       └── monitoring.py           # Monitoring utilities
├── migrations/                     # Database migrations
├── tests/                          # Test suite
│   ├── __init__.py
│   ├── conftest.py                 # Test configuration
│   ├── test_auth.py                # Auth tests
│   └── test_projects.py            # Project tests
├── logs/                           # Application logs
├── backups/                        # Database backups
├── .env.example                    # Example environment variables
├── .gitignore                      # Git ignore file
├── requirements.txt                # Python dependencies
├── run.py                          # Application entry point
├── Dockerfile                      # Docker configuration
├── docker-compose.yml              # Docker Compose configuration
├── nginx/                          # Nginx configuration
│   └── conf.d/                     # Nginx site configs
└── README.md                       # Project README
```

## Installation

### Prerequisites

- Python 3.9+
- PostgreSQL (for production)
- Redis (for production caching and task queue)

### Local Development Setup

1. Clone the repository:
   ```
   git clone <repository-url>
   cd construction-dashboard
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Create a `.env` file based on .env.example:
   ```
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. Initialize the database:
   ```
   flask db upgrade
   ```

6. Create an admin user:
   ```
   flask user create admin@example.com password "Admin User" --admin
   ```

7. Run the development server:
   ```
   flask run
   ```

8. Access the application at http://localhost:5000

### Docker Deployment

1. Build and start the containers:
   ```
   docker-compose up -d
   ```

2. Run database migrations:
   ```
   docker-compose exec web flask db upgrade
   ```

3. Create an admin user:
   ```
   docker-compose exec web flask user create admin@example.com password "Admin User" --admin
   ```

4. Access the application at http://localhost

## Environment Variables

Key environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| FLASK_ENV | Environment (development, production, testing) | development |
| SECRET_KEY | Secret key for session security | your-secret-key |
| DATABASE_URL | Database connection string | sqlite:///app.db |
| MAIL_SERVER | SMTP server for sending emails | None |
| MAIL_PORT | SMTP port | 25 |
| MAIL_USERNAME | SMTP username | None |
| MAIL_PASSWORD | SMTP password | None |
| MAIL_USE_TLS | Use TLS for SMTP | False |
| COMPANY_NAME | Company name for branding | Construction Dashboard |
| WEB3_PROVIDER_URL | Blockchain provider URL | http://127.0.0.1:8545 |
| PUSH_SERVICE_URL | Push notification service URL | None |
| CACHE_TYPE | Cache type (simple, redis, filesystem) | simple |

See .env.example for a complete list of configuration options.

## Usage

### User Roles and Permissions

- **Admin**: Full access to all features and settings
- **Project Manager**: Create and manage projects, approve documents
- **Field User**: Submit daily reports and safety observations
- **Office User**: Process RFIs, submittals, and change orders
- **Client**: View project progress and approved documents

### Key Features

1. **Dashboard**: Overview of all projects and recent activities
2. **Projects**: Detailed project information and documents
3. **Field Reports**: Daily reports, photos, and weather conditions
4. **Documents**: RFIs, submittals, and project documentation
5. **Safety**: Safety observations and incident reports
6. **Cost Control**: Budgets, change orders, and invoices
7. **Admin Panel**: User management and system settings

## Development

### Testing

Run the test suite:

```
pytest
```

Run with coverage report:

```
pytest --cov=app tests/
```

### Database Migrations

After changing models, create a new migration:

```
flask db migrate -m "Description of changes"
```

Apply migrations:

```
flask db upgrade
```

### CLI Commands

The application includes several CLI commands:

```
# User management
flask user create <email> <password> <name> [--admin]
flask user list
flask user deactivate <email>

# Database management
flask db-manage seed  # Seed database with initial data

# Setup commands
flask setup directories  # Create required directories

# Maintenance
flask maintenance clean-temp-files  # Clean temporary files
flask backup db  # Create database backup
```

## API Documentation

API documentation is available at `/api/docs` when the application is running. The API supports:

- Authentication with JWT tokens
- CRUD operations on projects, documents, and reports
- Mobile device synchronization
- File uploads and downloads

## Monitoring and Performance

The application includes monitoring tools to track:

- Request performance and slow endpoints
- Error rates and types
- System resource usage
- Database query performance

Access monitoring data at `/admin/monitoring` (admin users only).

## Security Features

- CSRF protection
- Rate limiting
- SQL injection prevention
- Secure file upload validation
- Content Security Policy headers
- IP allowlist for admin functions
- HTTPS enforcement in production

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit your changes: `git commit -am 'Add feature'`
4. Push to the branch: `git push origin feature-name`
5. Submit a pull request

Please ensure your code follows the project's style guidelines and includes appropriate tests.

## License

This project is licensed under the MIT License. See the LICENSE file for details.