from app.models.user import User, Role
from app.models.project import Project, ProjectUser
from app.extensions import db
from faker import Faker
import random
from datetime import datetime, timedelta

fake = Faker()

def generate_test_data(options):
    """Generate test data for development purposes
    
    Args:
        options (dict): Configuration options
            - users (bool): Generate users
            - projects (bool): Generate projects
            - count (int): Number of records to generate
    
    Returns:
        dict: Count of generated records by entity type
    """
    result = {}
    
    # Ensure roles exist
    Role.insert_roles()
    
    # Get existing admin user or create one if needed
    admin = User.query.filter_by(email='admin@example.com').first()
    if not admin:
        admin = User(
            email='admin@example.com',
            name='Admin User',
            role=Role.query.filter_by(name='Admin').first()
        )
        admin.password = 'password'
        db.session.add(admin)
        db.session.commit()
    
    # Generate users if requested
    if options.get('users'):
        created_users = 0
        roles = Role.query.all()
        
        for _ in range(options.get('count', 10)):
            # Create a user with random data
            first_name = fake.first_name()
            last_name = fake.last_name()
            email = fake.email()
            
            # Skip if email already exists
            if User.query.filter_by(email=email).first():
                continue
                
            user = User(
                name=f"{first_name} {last_name}",
                email=email,
                role=random.choice(roles),
                is_active=random.choice([True, True, True, False])  # 75% active
            )
            user.password = 'password'  # Simple password for test users
            
            # Add some history
            user.last_seen = datetime.utcnow() - timedelta(days=random.randint(0, 30))
            
            db.session.add(user)
            created_users += 1
        
        db.session.commit()
        result['users'] = created_users
    
    # Generate projects if requested
    if options.get('projects'):
        created_projects = 0
        users = User.query.all()
        
        for _ in range(options.get('count', 10)):
            # Create a project with random data
            name = fake.catch_phrase()
            number = f"PRJ-{fake.unique.random_int(min=1000, max=9999)}"
            
            # Skip if number already exists
            if Project.query.filter_by(number=number).first():
                continue
                
            # Generate random dates
            start_date = fake.date_between(start_date='-1y', end_date='+30d')
            target_date = start_date + timedelta(days=random.randint(30, 365))
            
            # Random status based on dates
            today = datetime.utcnow().date()
            if start_date > today:
                status = 'planning'
            elif random.random() < 0.1:
                status = random.choice(['on_hold', 'cancelled'])
            elif target_date < today:
                status = 'completed'
            else:
                status = 'active'
                
            # Create project
            project = Project(
                name=name,
                number=number,
                description=fake.paragraph(),
                status=status,
                start_date=start_date,
                target_completion_date=target_date,
                address=fake.street_address(),
                city=fake.city(),
                state=fake.state(),
                zip_code=fake.zipcode(),
                client_name=fake.company(),
                client_contact_info=fake.name() + "\n" + fake.phone_number(),
                contract_amount=random.uniform(10000, 5000000),
                project_type=random.choice([
                    'residential', 'commercial', 'industrial', 
                    'infrastructure', 'renovation'
                ]),
                category=random.choice([
                    'new_construction', 'renovation', 'addition', 
                    'repair', 'maintenance'
                ])
            )
            
            db.session.add(project)
            db.session.flush()  # Get project ID without committing
            
            # Assign random users to project
            project_users = random.sample(users, min(random.randint(2, 5), len(users)))
            
            for i, user in enumerate(project_users):
                # First user is project manager, others are members
                role = 'manager' if i == 0 else 'member'
                
                project_user = ProjectUser(
                    user_id=user.id,
                    project_id=project.id,
                    role=role
                )
                db.session.add(project_user)
            
            created_projects += 1
        
        db.session.commit()
        result['projects'] = created_projects
    
    return result