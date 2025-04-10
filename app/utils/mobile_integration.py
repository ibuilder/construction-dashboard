from flask import current_app
import requests
import json
import os
import base64
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename

def send_push_notification(user_ids, title, message, data=None):
    """Send push notification to mobile app users
    
    Args:
        user_ids (list): List of user IDs to notify
        title (str): Notification title
        message (str): Notification message
        data (dict, optional): Additional data to send
    
    Returns:
        bool: Success status
    """
    try:
        # Configure your push notification service (Firebase, OneSignal, etc.)
        push_service_url = current_app.config.get('PUSH_SERVICE_URL')
        api_key = current_app.config.get('PUSH_API_KEY')
        
        if not push_service_url or not api_key:
            current_app.logger.error("Push notification service not configured")
            return False
        
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'user_ids': user_ids,
            'notification': {
                'title': title,
                'body': message
            }
        }
        
        if data:
            payload['data'] = data
        
        response = requests.post(
            push_service_url,
            headers=headers,
            data=json.dumps(payload)
        )
        
        if response.status_code == 200:
            return True
        else:
            current_app.logger.error(f"Push notification failed: {response.text}")
            return False
            
    except Exception as e:
        current_app.logger.error(f"Error sending push notification: {str(e)}")
        return False

def notify_rfi_assigned(rfi_id, assigned_user_id):
    """Notify user when RFI is assigned to them"""
    from app.models.engineering import RFI
    
    rfi = RFI.query.get(rfi_id)
    if not rfi:
        return False
        
    return send_push_notification(
        [assigned_user_id],
        "RFI Assigned",
        f"You have been assigned RFI #{rfi.number}: {rfi.subject}",
        {
            'type': 'rfi_assigned',
            'rfi_id': rfi_id,
            'project_id': rfi.project_id
        }
    )

def notify_safety_incident(incident_id, project_id):
    """Notify project team about safety incident"""
    from app.models.safety import IncidentReport
    from app.models.project import Project
    
    incident = IncidentReport.query.get(incident_id)
    if not incident:
        return False
    
    project = Project.query.get(project_id)
    if not project:
        return False
        
    # Get IDs of all users on the project
    user_ids = [user.id for user in project.users]
    
    return send_push_notification(
        user_ids,
        "Safety Incident Reported",
        f"A {incident.severity} safety incident has been reported on {project.name}",
        {
            'type': 'safety_incident',
            'incident_id': incident_id,
            'project_id': project_id
        }
    )

def notify_submittal_returned(submittal_id):
    """Notify relevant users when a submittal is returned"""
    from app.models.engineering import Submittal
    from app.models.user import User
    
    submittal = Submittal.query.get(submittal_id)
    if not submittal:
        return False
    
    # Notify the submitter and anyone assigned
    user_ids = []
    if submittal.submitted_by:
        user_ids.append(submittal.submitted_by)
    if submittal.assigned_to:
        user_ids.append(submittal.assigned_to)
        
    # Add project manager to notification
    from app.models.project import ProjectRole
    project_managers = User.query.join(ProjectRole).filter(
        ProjectRole.project_id == submittal.project_id,
        ProjectRole.role == 'Project Manager'
    ).all()
    
    for pm in project_managers:
        if pm.id not in user_ids:
            user_ids.append(pm.id)
    
    if not user_ids:
        return False
        
    status_display = {
        'approved': 'Approved',
        'approved_with_comments': 'Approved with Comments',
        'revise_and_resubmit': 'Revise and Resubmit',
        'rejected': 'Rejected'
    }
    
    return send_push_notification(
        user_ids,
        f"Submittal {submittal.number} Returned",
        f"Submittal '{submittal.title}' has been returned with status: {status_display.get(submittal.status, submittal.status)}",
        {
            'type': 'submittal_returned',
            'submittal_id': submittal_id,
            'project_id': submittal.project_id,
            'status': submittal.status
        }
    )

def notify_daily_report_created(report_id):
    """Notify project managers when a daily report is submitted"""
    from app.models.field import DailyReport
    from app.models.user import User
    from app.models.project import ProjectRole
    
    report = DailyReport.query.get(report_id)
    if not report:
        return False
    
    # Find project managers and superintendents
    project_leaders = User.query.join(ProjectRole).filter(
        ProjectRole.project_id == report.project_id,
        ProjectRole.role.in_(['Project Manager', 'Superintendent'])
    ).all()
    
    user_ids = [u.id for u in project_leaders]
    if not user_ids:
        return False
    
    return send_push_notification(
        user_ids,
        "Daily Report Submitted",
        f"Daily Report for {report.report_date.strftime('%m/%d/%Y')} has been submitted",
        {
            'type': 'daily_report_created',
            'report_id': report_id,
            'project_id': report.project_id,
            'date': report.report_date.isoformat()
        }
    )

def notify_punchlist_item_completed(item_id):
    """Notify relevant users when a punchlist item is marked complete"""
    from app.models.field import PunchlistItem, Punchlist
    
    item = PunchlistItem.query.get(item_id)
    if not item or not item.punchlist_id:
        return False
    
    punchlist = Punchlist.query.get(item.punchlist_id)
    if not punchlist:
        return False
    
    # Notify the creator and anyone assigned
    user_ids = []
    if punchlist.created_by:
        user_ids.append(punchlist.created_by)
    if item.assigned_to:
        user_ids.append(item.assigned_to)
    
    if not user_ids:
        return False
        
    return send_push_notification(
        user_ids,
        "Punchlist Item Completed",
        f"Item '{item.description}' has been marked as complete",
        {
            'type': 'punchlist_item_completed',
            'item_id': item_id,
            'punchlist_id': item.punchlist_id,
            'project_id': punchlist.project_id
        }
    )

def notify_change_order_approved(co_id):
    """Notify relevant users when a change order is approved"""
    from app.models.cost import ChangeOrder
    from app.models.user import User
    from app.models.project import ProjectRole
    
    co = ChangeOrder.query.get(co_id)
    if not co:
        return False
    
    # Notify project managers, financial managers, and owner representatives
    stakeholders = User.query.join(ProjectRole).filter(
        ProjectRole.project_id == co.project_id,
        ProjectRole.role.in_(['Project Manager', 'Financial Manager', 'Owners Representative'])
    ).all()
    
    user_ids = [u.id for u in stakeholders]
    if co.created_by and co.created_by not in user_ids:
        user_ids.append(co.created_by)
    
    if not user_ids:
        return False
        
    return send_push_notification(
        user_ids,
        "Change Order Approved",
        f"Change Order {co.number} for ${co.amount:,.2f} has been approved",
        {
            'type': 'change_order_approved',
            'change_order_id': co_id,
            'project_id': co.project_id,
            'amount': float(co.amount)
        }
    )