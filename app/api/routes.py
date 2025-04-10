from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app.models.project import Project
from app.models.engineering import RFI, Submittal
from app.models.field import DailyReport, Punchlist
from app.models.safety import SafetyObservation, IncidentReport
from app.models.cost import Invoice, ChangeOrder
from app.extensions import db
from app.utils.access_control import role_required
from app.auth.routes import token_auth
from datetime import datetime, timedelta
import hashlib
import json

api_bp = Blueprint('api', __name__)

@api_bp.route('/projects')
@token_auth.login_required
def get_projects():
    """API endpoint to get projects list"""
    user = token_auth.current_user()
    
    if user.role == 'Admin':
        projects = Project.query.all()
    else:
        projects = Project.query.join(Project.users).filter(User.id == user.id).all()
    
    results = []
    for project in projects:
        results.append({
            'id': project.id,
            'name': project.name,
            'number': project.number,
            'status': project.status,
            'start_date': project.start_date.isoformat() if project.start_date else None,
            'end_date': project.end_date.isoformat() if project.end_date else None
        })
    
    return jsonify({
        'status': 'success',
        'data': results,
        'count': len(results)
    })

@api_bp.route('/projects/<int:id>')
@token_auth.login_required
def get_project(id):
    """API endpoint to get project details"""
    user = token_auth.current_user()
    project = Project.query.get_or_404(id)
    
    # Check if user has access
    if user.role != 'Admin' and user not in project.users:
        return jsonify({
            'status': 'error',
            'message': 'You do not have permission to access this project'
        }), 403
    
    # Get summary counts
    rfi_count = RFI.query.filter_by(project_id=id).count()
    submittal_count = Submittal.query.filter_by(project_id=id).count()
    daily_report_count = DailyReport.query.filter_by(project_id=id).count()
    
    result = {
        'id': project.id,
        'name': project.name,
        'number': project.number,
        'description': project.description,
        'address': project.address,
        'city': project.city,
        'state': project.state,
        'zip_code': project.zip_code,
        'status': project.status,
        'start_date': project.start_date.isoformat() if project.start_date else None,
        'end_date': project.end_date.isoformat() if project.end_date else None,
        'owner': project.owner.name if project.owner else None,
        'summary': {
            'rfi_count': rfi_count,
            'submittal_count': submittal_count,
            'daily_report_count': daily_report_count
        }
    }
    
    return jsonify({
        'status': 'success',
        'data': result
    })

@api_bp.route('/projects/<int:id>/rfis')
@token_auth.login_required
def get_project_rfis(id):
    """API endpoint to get RFIs for a project"""
    user = token_auth.current_user()
    project = Project.query.get_or_404(id)
    
    # Check if user has access
    if user.role != 'Admin' and user not in project.users:
        return jsonify({
            'status': 'error',
            'message': 'You do not have permission to access this project'
        }), 403
    
    rfis = RFI.query.filter_by(project_id=id).order_by(RFI.date_submitted.desc()).all()
    
    results = []
    for rfi in rfis:
        results.append({
            'id': rfi.id,
            'number': rfi.number,
            'subject': rfi.subject,
            'status': rfi.status,
            'date_submitted': rfi.date_submitted.isoformat(),
            'date_required': rfi.date_required.isoformat() if rfi.date_required else None,
            'date_answered': rfi.date_answered.isoformat() if rfi.date_answered else None,
            'has_answer': bool(rfi.answer and rfi.answer.strip())
        })
    
    return jsonify({
        'status': 'success',
        'data': results,
        'count': len(results)
    })

@api_bp.route('/projects/<int:id>/submittals')
@token_auth.login_required
def get_project_submittals(id):
    """API endpoint to get submittals for a project"""
    user = token_auth.current_user()
    project = Project.query.get_or_404(id)
    
    # Check if user has access
    if user.role != 'Admin' and user not in project.users:
        return jsonify({
            'status': 'error',
            'message': 'You do not have permission to access this project'
        }), 403
    
    submittals = Submittal.query.filter_by(project_id=id).order_by(Submittal.date_submitted.desc()).all()
    
    results = []
    for submittal in submittals:
        results.append({
            'id': submittal.id,
            'number': submittal.number,
            'title': submittal.title,
            'status': submittal.status,
            'specification_section': submittal.specification_section,
            'date_submitted': submittal.date_submitted.isoformat(),
            'date_required': submittal.date_required.isoformat() if submittal.date_required else None,
            'date_returned': submittal.date_returned.isoformat() if submittal.date_returned else None
        })
    
    return jsonify({
        'status': 'success',
        'data': results,
        'count': len(results)
    })

@api_bp.route('/projects/<int:id>/daily-reports')
@token_auth.login_required
def get_project_daily_reports(id):
    """API endpoint to get daily reports for a project"""
    user = token_auth.current_user()
    project = Project.query.get_or_404(id)
    
    # Check if user has access
    if user.role != 'Admin' and user not in project.users:
        return jsonify({
            'status': 'error',
            'message': 'You do not have permission to access this project'
        }), 403
    
    reports = DailyReport.query.filter_by(project_id=id).order_by(DailyReport.report_date.desc()).all()
    
    results = []
    for report in reports:
        results.append({
            'id': report.id,
            'report_number': report.report_number,
            'report_date': report.report_date.isoformat(),
            'weather_conditions': report.weather_conditions,
            'temperature_high': report.temperature_high,
            'temperature_low': report.temperature_low,
            'manpower_count': report.manpower_count,
            'delays': report.delays
        })
    
    return jsonify({
        'status': 'success',
        'data': results,
        'count': len(results)
    })

@api_bp.route('/daily-reports/<int:id>')
@token_auth.login_required
def get_daily_report(id):
    """API endpoint to get a specific daily report"""
    user = token_auth.current_user()
    report = DailyReport.query.get_or_404(id)
    project = Project.query.get(report.project_id)
    
    # Check if user has access
    if user.role != 'Admin' and user not in project.users:
        return jsonify({
            'status': 'error',
            'message': 'You do not have permission to access this report'
        }), 403
    
    # Get photos for this report
    photos = Photo.query.filter_by(daily_report_id=id).all()
    photos_data = []
    
    for photo in photos:
        photos_data.append({
            'id': photo.id,
            'title': photo.title,
            'description': photo.description,
            'file_path': photo.file_path,
            'taken_at': photo.taken_at.isoformat() if photo.taken_at else None
        })
    
    report_data = {
        'id': report.id,
        'report_number': report.report_number,
        'report_date': report.report_date.isoformat(),
        'weather_conditions': report.weather_conditions,
        'temperature_high': report.temperature_high,
        'temperature_low': report.temperature_low,
        'precipitation': report.precipitation,
        'wind_speed': report.wind_speed,
        'manpower_count': report.manpower_count,
        'delays': report.delays,
        'delay_description': report.delay_description,
        'work_performed': report.work_performed,
        'materials_received': report.materials_received,
        'equipment_used': report.equipment_used,
        'visitors': report.visitors,
        'safety_incidents': report.safety_incidents,
        'quality_issues': report.quality_issues,
        'created_by': report.creator.name if report.creator else 'Unknown',
        'created_at': report.created_at.isoformat() if report.created_at else None,
        'photos': photos_data
    }
    
    return jsonify({
        'status': 'success',
        'data': report_data
    })

@api_bp.route('/projects/<int:id>/safety/observations')
@token_auth.login_required
def get_project_safety_observations(id):
    """API endpoint to get safety observations for a project"""
    user = token_auth.current_user()
    project = Project.query.get_or_404(id)
    
    # Check if user has access
    if user.role != 'Admin' and user not in project.users:
        return jsonify({
            'status': 'error',
            'message': 'You do not have permission to access this project'
        }), 403
    
    observations = SafetyObservation.query.filter_by(project_id=id).order_by(
        SafetyObservation.observation_date.desc()).all()
    
    results = []
    for obs in observations:
        observer_name = User.query.get(obs.observed_by).name if obs.observed_by else "Unknown"
        results.append({
            'id': obs.id,
            'title': obs.title,
            'category': obs.category,
            'severity': obs.severity,
            'observation_date': obs.observation_date.isoformat(),
            'location': obs.location,
            'status': obs.status,
            'observed_by': observer_name
        })
    
    return jsonify({
        'status': 'success',
        'data': results,
        'count': len(results)
    })

@api_bp.route('/projects/<int:id>/cost/change-orders')
@token_auth.login_required
def get_project_change_orders(id):
    """API endpoint to get change orders for a project"""
    user = token_auth.current_user()
    project = Project.query.get_or_404(id)
    
    # Check if user has access and proper role for cost data
    if user.role not in ['Admin', 'Owner', 'Owners Representative', 'General Contractor'] or (user.role != 'Admin' and user not in project.users):
        return jsonify({
            'status': 'error',
            'message': 'You do not have permission to access this cost data'
        }), 403
    
    change_orders = ChangeOrder.query.filter_by(project_id=id).order_by(
        ChangeOrder.number).all()
    
    results = []
    for co in change_orders:
        results.append({
            'id': co.id,
            'number': co.number,
            'title': co.title,
            'amount': float(co.amount),
            'status': co.status,
            'date_issued': co.date_issued.isoformat(),
            'date_approved': co.date_approved.isoformat() if co.date_approved else None
        })
    
    return jsonify({
        'status': 'success',
        'data': results,
        'count': len(results)
    })

@api_bp.route('/verify-document', methods=['POST'])
@token_auth.login_required
def verify_document():
    """API endpoint to verify a document's blockchain hash"""
    data = request.get_json()
    
    if not data or not data.get('hash') or not data.get('document_type') or not data.get('document_id'):
        return jsonify({
            'status': 'error',
            'message': 'Missing required parameters'
        }), 400
    
    from app.utils.web3_utils import verify_document_hash
    
    success, result = verify_document_hash(
        data['document_type'],
        data['document_id'],
        data['hash']
    )
    
    if success:
        return jsonify({
            'status': 'success',
            'verified': True,
            'data': result
        })
    else:
        return jsonify({
            'status': 'error',
            'verified': False,
            'message': result
        }), 400

@api_bp.route('/daily-reports/create', methods=['POST'])
@token_auth.login_required
def create_daily_report():
    """API endpoint to create a daily report from mobile"""
    user = token_auth.current_user()
    data = request.get_json()
    
    if not data or not data.get('project_id'):
        return jsonify({
            'status': 'error',
            'message': 'Missing project_id'
        }), 400
    
    project_id = data.get('project_id')
    project = Project.query.get_or_404(project_id)
    
    # Check if user has access
    if user.role != 'Admin' and user not in project.users:
        return jsonify({
            'status': 'error',
            'message': 'You do not have permission to access this project'
        }), 403
    
    # Check if a report already exists for today
    today = datetime.now().date()
    existing_report = DailyReport.query.filter_by(
        project_id=project_id, report_date=today).first()
    
    if existing_report:
        return jsonify({
            'status': 'error',
            'message': 'A report for today already exists',
            'report_id': existing_report.id
        }), 400
    
    # Get next report number
    last_report = DailyReport.query.filter_by(project_id=project_id).order_by(
        DailyReport.id.desc()).first()
    next_number = f"DR-{(last_report.id + 1 if last_report else 1):04d}"
    
    report = DailyReport(
        project_id=project_id,
        report_date=today,
        report_number=next_number,
        weather_conditions=data.get('weather_conditions', ''),
        temperature_high=data.get('temperature_high'),
        temperature_low=data.get('temperature_low'),
        precipitation=data.get('precipitation', 0),
        wind_speed=data.get('wind_speed', 0),
        delays=data.get('delays', False),
        delay_description=data.get('delay_description'),
        manpower_count=data.get('manpower_count', 0),
        work_performed=data.get('work_performed', ''),
        materials_received=data.get('materials_received', ''),
        equipment_used=data.get('equipment_used', ''),
        visitors=data.get('visitors', ''),
        safety_incidents=data.get('safety_incidents', ''),
        quality_issues=data.get('quality_issues', ''),
        created_by=user.id
    )
    
    db.session.add(report)
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': 'Daily report created successfully',
        'report_id': report.id
    })