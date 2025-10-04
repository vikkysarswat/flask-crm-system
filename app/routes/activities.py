"""Activity tracking routes.

Yeh module activities aur tasks manage karta hai.

"""

from flask import (
    Blueprint, render_template, redirect, url_for,
    flash, request, jsonify, current_app
)
from flask_login import login_required, current_user
from app import db
from app.models.activity import Activity
from app.models.task import Task
from app.models.contact import Contact
from app.models.lead import Lead
from app.models.deal import Deal
from datetime import datetime


activities_bp = Blueprint('activities', __name__, url_prefix='/activities')


@activities_bp.route('/')
@login_required
def list_activities():
    """List all activities.
    
    Returns:
        Response: Activities list page
    """
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config.get('ITEMS_PER_PAGE', 20)
    
    # Filters
    activity_type = request.args.get('type', '')
    completed = request.args.get('completed', '')
    
    # Base query
    query = Activity.query.filter_by(user_id=current_user.id)
    
    if activity_type:
        query = query.filter_by(activity_type=activity_type)
    
    if completed == 'yes':
        query = query.filter_by(is_completed=True)
    elif completed == 'no':
        query = query.filter_by(is_completed=False)
    
    # Pagination
    activities = query.order_by(
        Activity.created_at.desc()
    ).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )
    
    return render_template(
        'activities/list.html',
        activities=activities,
        activity_type=activity_type,
        completed=completed
    )


@activities_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_activity():
    """Create new activity.
    
    Returns:
        Response: Create form ya redirect
    """
    if request.method == 'POST':
        # Get form data
        activity_type = request.form.get('activity_type')
        subject = request.form.get('subject', '').strip()
        description = request.form.get('description', '').strip()
        duration = request.form.get('duration', type=int)
        scheduled_at = request.form.get('scheduled_at')
        contact_id = request.form.get('contact_id', type=int)
        lead_id = request.form.get('lead_id', type=int)
        deal_id = request.form.get('deal_id', type=int)
        
        # Validation
        if not all([activity_type, subject]):
            flash('Activity type and subject are required.', 'error')
            return render_template('activities/create.html')
        
        # Parse scheduled time
        sched_time = None
        if scheduled_at:
            try:
                sched_time = datetime.strptime(
                    scheduled_at, '%Y-%m-%dT%H:%M'
                )
            except ValueError:
                flash('Invalid date/time format.', 'error')
        
        # Create activity
        try:
            activity = Activity(
                activity_type=activity_type,
                subject=subject,
                description=description,
                duration=duration,
                scheduled_at=sched_time,
                user_id=current_user.id,
                contact_id=contact_id,
                lead_id=lead_id,
                deal_id=deal_id
            )
            
            db.session.add(activity)
            db.session.commit()
            
            flash('Activity created successfully!', 'success')
            return redirect(url_for('activities.list_activities'))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Error creating activity: {str(e)}')
            flash('An error occurred.', 'error')
    
    return render_template('activities/create.html')


@activities_bp.route('/<int:activity_id>/complete', methods=['POST'])
@login_required
def complete_activity(activity_id):
    """Mark activity as completed.
    
    Args:
        activity_id (int): Activity ID
        
    Returns:
        Response: Redirect back
    """
    activity = Activity.query.get_or_404(activity_id)
    
    if activity.user_id != current_user.id and not current_user.is_admin():
        flash('You do not have permission.', 'error')
        return redirect(url_for('activities.list_activities'))
    
    outcome = request.form.get('outcome', '').strip()
    
    try:
        activity.mark_completed(outcome=outcome)
        db.session.commit()
        flash('Activity marked as completed!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash('An error occurred.', 'error')
    
    return redirect(request.referrer or url_for('activities.list_activities'))


@activities_bp.route('/tasks')
@login_required
def list_tasks():
    """List all tasks.
    
    Returns:
        Response: Tasks list page
    """
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config.get('ITEMS_PER_PAGE', 20)
    
    # Filters
    status = request.args.get('status', '')
    priority = request.args.get('priority', '')
    
    # Base query
    query = Task.query.filter_by(assigned_to=current_user.id)
    
    if status:
        query = query.filter_by(status=status)
    
    if priority:
        query = query.filter_by(priority=priority)
    
    # Pagination
    tasks = query.order_by(
        Task.due_date.asc()
    ).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )
    
    return render_template(
        'activities/tasks.html',
        tasks=tasks,
        status=status,
        priority=priority
    )


@activities_bp.route('/tasks/create', methods=['GET', 'POST'])
@login_required
def create_task():
    """Create new task.
    
    Returns:
        Response: Create form ya redirect
    """
    if request.method == 'POST':
        # Get form data
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        priority = request.form.get('priority', 'medium')
        due_date = request.form.get('due_date')
        assigned_to = request.form.get('assigned_to', type=int) or current_user.id
        contact_id = request.form.get('contact_id', type=int)
        lead_id = request.form.get('lead_id', type=int)
        deal_id = request.form.get('deal_id', type=int)
        
        # Validation
        if not title:
            flash('Task title is required.', 'error')
            return render_template('activities/create_task.html')
        
        # Parse due date
        due_dt = None
        if due_date:
            try:
                due_dt = datetime.strptime(due_date, '%Y-%m-%dT%H:%M')
            except ValueError:
                flash('Invalid date/time format.', 'error')
        
        # Create task
        try:
            task = Task(
                title=title,
                description=description,
                priority=priority,
                due_date=due_dt,
                assigned_to=assigned_to,
                created_by=current_user.id,
                contact_id=contact_id,
                lead_id=lead_id,
                deal_id=deal_id
            )
            
            db.session.add(task)
            db.session.commit()
            
            flash('Task created successfully!', 'success')
            return redirect(url_for('activities.list_tasks'))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Error creating task: {str(e)}')
            flash('An error occurred.', 'error')
    
    return render_template('activities/create_task.html')


@activities_bp.route('/tasks/<int:task_id>/complete', methods=['POST'])
@login_required
def complete_task(task_id):
    """Mark task as completed.
    
    Args:
        task_id (int): Task ID
        
    Returns:
        Response: Redirect back
    """
    task = Task.query.get_or_404(task_id)
    
    if task.assigned_to != current_user.id and not current_user.is_admin():
        flash('You do not have permission.', 'error')
        return redirect(url_for('activities.list_tasks'))
    
    try:
        task.mark_completed()
        db.session.commit()
        flash('Task completed!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash('An error occurred.', 'error')
    
    return redirect(request.referrer or url_for('activities.list_tasks'))
