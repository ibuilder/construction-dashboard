import os
import subprocess
import datetime
import boto3
from flask import current_app
import logging

logger = logging.getLogger(__name__)

def backup_database():
    """Back up database to file and optionally to S3"""
    try:
        # Ensure backup directory exists
        backup_dir = os.path.join(os.getcwd(), 'backups')
        os.makedirs(backup_dir, exist_ok=True)
        
        # Get database connection info
        db_url = current_app.config['SQLALCHEMY_DATABASE_URI']
        db_type = db_url.split('://')[0]
        
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f'backup_{timestamp}.sql'
        backup_path = os.path.join(backup_dir, backup_filename)
        
        if db_type == 'postgresql':
            # Parse connection info
            import re
            match = re.match(r'postgresql://([^:]+):([^@]+)@([^:]+):(\d+)/(.+)', db_url)
            if not match:
                logger.error("Could not parse PostgreSQL connection string")
                return False
                
            username, password, host, port, database = match.groups()
            
            # Set environment variable for password
            env = os.environ.copy()
            env['PGPASSWORD'] = password
            
            # Run pg_dump
            cmd = [
                'pg_dump',
                '-h', host,
                '-p', port,
                '-U', username,
                '-F', 'c',  # Custom format (compressed)
                '-b',  # Include large objects
                '-v',  # Verbose
                '-f', backup_path,
                database
            ]
            
            subprocess.run(cmd, env=env, check=True)
            logger.info(f"PostgreSQL backup created: {backup_path}")
            
        elif db_type == 'mysql':
            # Parse connection info
            import re
            match = re.match(r'mysql://([^:]+):([^@]+)@([^:]+):(\d+)/(.+)', db_url)
            if not match:
                logger.error("Could not parse MySQL connection string")
                return False
                
            username, password, host, port, database = match.groups()
            
            # Run mysqldump
            cmd = [
                'mysqldump',
                '-h', host,
                '-P', port,
                '-u', username,
                f'--password={password}',
                '--single-transaction',
                '--routines',
                '--triggers',
                '--events',
                database
            ]
            
            with open(backup_path, 'w') as f:
                subprocess.run(cmd, stdout=f, check=True)
            logger.info(f"MySQL backup created: {backup_path}")
            
        elif db_type == 'sqlite':
            # For SQLite, just copy the file
            import shutil
            db_path = db_url.replace('sqlite:///', '')
            shutil.copy2(db_path, backup_path)
            logger.info(f"SQLite backup created: {backup_path}")
            
        else:
            logger.error(f"Unsupported database type: {db_type}")
            return False
            
        # Upload to S3 if configured
        s3_bucket = current_app.config.get('BACKUP_S3_BUCKET')
        if s3_bucket:
            upload_to_s3(backup_path, backup_filename, s3_bucket)
            
        # Clean old backups
        clean_old_backups(backup_dir)
        
        return True
        
    except Exception as e:
        logger.error(f"Backup failed: {str(e)}")
        return False

def upload_to_s3(file_path, file_name, bucket_name):
    """Upload backup file to S3"""
    try:
        s3 = boto3.client(
            's3',
            aws_access_key_id=current_app.config.get('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=current_app.config.get('AWS_SECRET_ACCESS_KEY'),
            region_name=current_app.config.get('AWS_REGION', 'us-east-1')
        )
        
        # Create S3 path with date folder structure
        today = datetime.datetime.now()
        s3_path = f"backups/{today.strftime('%Y/%m/%d')}/{file_name}"
        
        # Upload file
        s3.upload_file(file_path, bucket_name, s3_path)
        logger.info(f"Backup uploaded to S3: {bucket_name}/{s3_path}")
        return True
    except Exception as e:
        logger.error(f"S3 upload failed: {str(e)}")
        return False

def clean_old_backups(backup_dir, retention_days=7):
    """Delete backups older than retention_days"""
    now = datetime.datetime.now()
    retention_delta = datetime.timedelta(days=retention_days)
    
    for filename in os.listdir(backup_dir):
        if not filename.startswith('backup_'):
            continue
            
        file_path = os.path.join(backup_dir, filename)
        file_modified = datetime.datetime.fromtimestamp(os.path.getmtime(file_path))
        
        if now - file_modified > retention_delta:
            os.remove(file_path)
            logger.info(f"Deleted old backup: {filename}")