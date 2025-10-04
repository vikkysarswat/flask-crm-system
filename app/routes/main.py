"""Main routes for dashboard and home pages.

Yeh module main application pages handle karta hai.

"""

from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from sqlalchemy import func
from datetime import datetime, timedelta
from app import db
from app.models.contact import Contact
from app.models.lead import Lead
from app.models.deal import Deal
from app.models.task import Task
from app.models.activity import Activity


main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Home page route.
    
    Application ka landing page.
    
    Returns:
        Response: Home page ya redirect to dashboard
    """
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('auth.login'))


@main_bp.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard with analytics and metrics.
    
    User ko CRM ka overview aur key metrics dikhata hai.
    Real-time statistics aur pending tasks display karta hai.
    
    Returns:
        Response: Dashboard page with analytics
    """
    # Get current user's data
    user_id = current_user.id
    is_admin = current_user.is_admin()
    
    # Calculate date ranges
    today = datetime.utcnow().date()
    thirty_days_ago = today - timedelta(days=30)
    
    # Build query filters based on role
    if is_admin:
        # Admin can see all data
        contact_filter = {}
        lead_filter = {}
        deal_filter = {}
        task_filter = {}
    else:
        # Regular users see only their data
        contact_filter = {'owner_id': user_id}
        lead_filter = {'owner_id': user_id}
        deal_filter = {'owner_id': user_id}
        task_filter = {'assigned_to': user_id}
    
    # Get counts for key metrics
    stats = {
        'total_contacts': Contact.query.filter_by(**contact_filter).count(),
        'active_leads': Lead.query.filter_by(
            status='new', **lead_filter
        ).count(),
        'open_deals': Deal.query.filter_by(
            status='open', **deal_filter
        ).count(),
        'pending_tasks': Task.query.filter_by(
            status='pending', **task_filter
        ).count()
    }
    
    # Calculate total pipeline value
    pipeline_value = db.session.query(
        func.sum(Deal.value)
    ).filter(
        Deal.status == 'open'
    ).filter_by(**deal_filter).scalar() or 0
    
    stats['pipeline_value'] = pipeline_value
    
    # Get recent activities (last 10)
    recent_activities = Activity.query.filter_by(
        user_id=user_id
    ).order_by(
        Activity.created_at.desc()
    ).limit(10).all()
    
    # Get upcoming tasks (next 7 days)
    next_week = today + timedelta(days=7)
    upcoming_tasks = Task.query.filter(
        Task.due_date.between(today, next_week),
        Task.status != 'completed'
    ).filter_by(**task_filter).order_by(
        Task.due_date.asc()
    ).limit(10).all()
    
    # Get overdue tasks
    overdue_tasks = Task.query.filter(
        Task.due_date < datetime.utcnow(),
        Task.status != 'completed'
    ).filter_by(**task_filter).order_by(
        Task.due_date.asc()
    ).limit(5).all()
    
    # Get hot leads (score >= 70)
    hot_leads = Lead.query.filter(
        Lead.score >= 70,
        Lead.status.in_(['new', 'contacted', 'qualified'])
    ).filter_by(**lead_filter).order_by(
        Lead.score.desc()
    ).limit(5).all()
    
    # Get deals closing this month
    end_of_month = today.replace(day=1) + timedelta(days=32)
    end_of_month = end_of_month.replace(day=1) - timedelta(days=1)
    
    closing_deals = Deal.query.filter(
        Deal.expected_close_date.between(today, end_of_month),
        Deal.status == 'open'
    ).filter_by(**deal_filter).order_by(
        Deal.expected_close_date.asc()
    ).limit(5).all()
    
    # Monthly performance (won deals this month)
    first_day_of_month = today.replace(day=1)
    monthly_won_deals = Deal.query.filter(
        Deal.status == 'won',
        Deal.actual_close_date >= first_day_of_month
    ).filter_by(**deal_filter).count()
    
    monthly_won_value = db.session.query(
        func.sum(Deal.value)
    ).filter(
        Deal.status == 'won',
        Deal.actual_close_date >= first_day_of_month
    ).filter_by(**deal_filter).scalar() or 0
    
    stats['monthly_won_deals'] = monthly_won_deals
    stats['monthly_revenue'] = monthly_won_value
    
    return render_template(
        'main/dashboard.html',
        stats=stats,
        recent_activities=recent_activities,
        upcoming_tasks=upcoming_tasks,
        overdue_tasks=overdue_tasks,
        hot_leads=hot_leads,
        closing_deals=closing_deals
    )


@main_bp.route('/search')
@login_required
def search():
    """Global search across all entities.
    
    Contacts, leads, deals mein search functionality.
    
    Returns:
        Response: Search results page
    """
    # TODO: Implement global search
    return render_template('main/search.html')
