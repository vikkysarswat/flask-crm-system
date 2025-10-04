"""REST API routes.

Yeh module RESTful API endpoints provide karta hai.

"""

from flask import Blueprint, jsonify, request, current_app
from flask_login import login_required, current_user
from app import db
from app.models.contact import Contact
from app.models.lead import Lead
from app.models.deal import Deal
from app.models.notification import Notification
from datetime import datetime


api_bp = Blueprint('api', __name__, url_prefix='/api/v1')


@api_bp.route('/contacts', methods=['GET'])
@login_required
def api_list_contacts():
    """List contacts API endpoint.
    
    Returns:
        JSON: List of contacts
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    query = Contact.query
    
    if not current_user.is_admin():
        query = query.filter_by(owner_id=current_user.id)
    
    contacts = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'contacts': [c.to_dict() for c in contacts.items],
        'total': contacts.total,
        'pages': contacts.pages,
        'current_page': page
    })


@api_bp.route('/contacts/<int:contact_id>', methods=['GET'])
@login_required
def api_get_contact(contact_id):
    """Get contact by ID.
    
    Args:
        contact_id (int): Contact ID
        
    Returns:
        JSON: Contact data
    """
    contact = Contact.query.get_or_404(contact_id)
    
    if not current_user.is_admin() and contact.owner_id != current_user.id:
        return jsonify({'error': 'Permission denied'}), 403
    
    return jsonify(contact.to_dict())


@api_bp.route('/leads', methods=['GET'])
@login_required
def api_list_leads():
    """List leads API endpoint.
    
    Returns:
        JSON: List of leads
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    query = Lead.query
    
    if not current_user.is_admin():
        query = query.filter_by(owner_id=current_user.id)
    
    leads = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'leads': [l.to_dict() for l in leads.items],
        'total': leads.total,
        'pages': leads.pages,
        'current_page': page
    })


@api_bp.route('/deals', methods=['GET'])
@login_required
def api_list_deals():
    """List deals API endpoint.
    
    Returns:
        JSON: List of deals
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    query = Deal.query
    
    if not current_user.is_admin():
        query = query.filter_by(owner_id=current_user.id)
    
    deals = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'deals': [d.to_dict() for d in deals.items],
        'total': deals.total,
        'pages': deals.pages,
        'current_page': page
    })


@api_bp.route('/notifications', methods=['GET'])
@login_required
def api_list_notifications():
    """List user notifications.
    
    Returns:
        JSON: List of notifications
    """
    unread_only = request.args.get('unread', 'false').lower() == 'true'
    
    query = Notification.query.filter_by(user_id=current_user.id)
    
    if unread_only:
        query = query.filter_by(is_read=False)
    
    notifications = query.order_by(
        Notification.created_at.desc()
    ).limit(50).all()
    
    return jsonify({
        'notifications': [n.to_dict() for n in notifications]
    })


@api_bp.route('/notifications/<int:notification_id>/read', methods=['POST'])
@login_required
def api_mark_notification_read(notification_id):
    """Mark notification as read.
    
    Args:
        notification_id (int): Notification ID
        
    Returns:
        JSON: Success status
    """
    notification = Notification.query.get_or_404(notification_id)
    
    if notification.user_id != current_user.id:
        return jsonify({'error': 'Permission denied'}), 403
    
    try:
        notification.mark_as_read()
        db.session.commit()
        
        return jsonify({'success': True})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@api_bp.route('/stats', methods=['GET'])
@login_required
def api_get_stats():
    """Get dashboard statistics.
    
    Returns:
        JSON: Statistics data
    """
    # Build filters
    if current_user.is_admin():
        contact_filter = {}
        lead_filter = {}
        deal_filter = {}
    else:
        contact_filter = {'owner_id': current_user.id}
        lead_filter = {'owner_id': current_user.id}
        deal_filter = {'owner_id': current_user.id}
    
    stats = {
        'total_contacts': Contact.query.filter_by(**contact_filter).count(),
        'total_leads': Lead.query.filter_by(**lead_filter).count(),
        'open_deals': Deal.query.filter_by(status='open', **deal_filter).count(),
        'won_deals': Deal.query.filter_by(status='won', **deal_filter).count(),
    }
    
    return jsonify(stats)
