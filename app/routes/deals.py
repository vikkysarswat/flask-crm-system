"""Deal management routes.

Yeh module deal pipeline aur opportunity management handle karta hai.

"""

from flask import (
    Blueprint, render_template, redirect, url_for,
    flash, request, jsonify, current_app
)
from flask_login import login_required, current_user
from sqlalchemy import or_, func
from app import db
from app.models.deal import Deal
from app.models.contact import Contact
from app.models.activity import Activity
from datetime import datetime, date


deals_bp = Blueprint('deals', __name__, url_prefix='/deals')


@deals_bp.route('/')
@login_required
def list_deals():
    """List all deals with pipeline view.
    
    Returns:
        Response: Deals list page
    """
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config.get('ITEMS_PER_PAGE', 20)
    
    # Filters
    search = request.args.get('search', '').strip()
    stage = request.args.get('stage', '')
    status = request.args.get('status', '')
    
    # Base query
    query = Deal.query
    
    if not current_user.is_admin():
        query = query.filter_by(owner_id=current_user.id)
    
    if search:
        query = query.join(Contact).filter(
            or_(
                Deal.title.ilike(f'%{search}%'),
                Contact.company.ilike(f'%{search}%')
            )
        )
    
    if stage:
        query = query.filter_by(stage=stage)
    
    if status:
        query = query.filter_by(status=status)
    
    # Pagination
    deals = query.order_by(
        Deal.expected_close_date.asc()
    ).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )
    
    # Calculate pipeline stats
    pipeline_stats = db.session.query(
        Deal.stage,
        func.count(Deal.id).label('count'),
        func.sum(Deal.value).label('total_value')
    ).filter(
        Deal.status == 'open'
    )
    
    if not current_user.is_admin():
        pipeline_stats = pipeline_stats.filter_by(owner_id=current_user.id)
    
    pipeline_stats = pipeline_stats.group_by(Deal.stage).all()
    
    return render_template(
        'deals/list.html',
        deals=deals,
        pipeline_stats=pipeline_stats,
        search=search,
        stage=stage,
        status=status
    )


@deals_bp.route('/pipeline')
@login_required
def pipeline_view():
    """Visual pipeline view with drag-and-drop.
    
    Kanban style pipeline view provide karta hai.
    
    Returns:
        Response: Pipeline view page
    """
    # Get all open deals
    query = Deal.query.filter_by(status='open')
    
    if not current_user.is_admin():
        query = query.filter_by(owner_id=current_user.id)
    
    deals = query.order_by(Deal.probability.desc()).all()
    
    # Group deals by stage
    stages = {
        'prospecting': [],
        'qualified': [],
        'proposal': [],
        'negotiation': [],
        'closed_won': [],
        'closed_lost': []
    }
    
    for deal in deals:
        if deal.stage in stages:
            stages[deal.stage].append(deal)
    
    return render_template(
        'deals/pipeline.html',
        stages=stages
    )


@deals_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_deal():
    """Create new deal.
    
    Returns:
        Response: Create form ya redirect to deal detail
    """
    if request.method == 'POST':
        # Get form data
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        value = request.form.get('value', type=float)
        currency = request.form.get('currency', 'INR')
        stage = request.form.get('stage', 'prospecting')
        contact_id = request.form.get('contact_id', type=int)
        expected_close_date = request.form.get('expected_close_date')
        source = request.form.get('source', '').strip()
        products = request.form.get('products', '').strip()
        notes = request.form.get('notes', '').strip()
        
        # Validation
        errors = []
        
        if not all([title, value, contact_id]):
            errors.append('Title, value and contact are required.')
        
        if value and value < 0:
            errors.append('Deal value must be positive.')
        
        if errors:
            for error in errors:
                flash(error, 'error')
            # Get contacts for dropdown
            contacts = Contact.query.filter_by(
                owner_id=current_user.id
            ).order_by(Contact.company).all()
            return render_template('deals/create.html', contacts=contacts)
        
        # Parse expected close date
        exp_close_date = None
        if expected_close_date:
            try:
                exp_close_date = datetime.strptime(
                    expected_close_date, '%Y-%m-%d'
                ).date()
            except ValueError:
                flash('Invalid date format.', 'error')
        
        # Create deal
        try:
            deal = Deal(
                title=title,
                description=description,
                value=value,
                currency=currency,
                stage=stage,
                contact_id=contact_id,
                owner_id=current_user.id,
                expected_close_date=exp_close_date,
                source=source,
                products=products,
                notes=notes,
                status='open'
            )
            
            # Set probability based on stage
            deal.move_to_stage(stage)
            
            db.session.add(deal)
            db.session.commit()
            
            # Log activity
            activity = Activity(
                activity_type='note',
                subject='Deal Created',
                description=f'New deal "{deal.title}" was created',
                user_id=current_user.id,
                deal_id=deal.id,
                contact_id=contact_id,
                is_completed=True,
                completed_at=datetime.utcnow()
            )
            db.session.add(activity)
            db.session.commit()
            
            current_app.logger.info(
                f'Deal created: {deal.title} by {current_user.email}'
            )
            flash(f'Deal "{deal.title}" created successfully!', 'success')
            return redirect(url_for('deals.view_deal', deal_id=deal.id))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Error creating deal: {str(e)}')
            flash('An error occurred while creating the deal.', 'error')
    
    # GET request - show form
    contacts = Contact.query.filter_by(
        owner_id=current_user.id
    ).order_by(Contact.company).all()
    
    return render_template('deals/create.html', contacts=contacts)


@deals_bp.route('/<int:deal_id>')
@login_required
def view_deal(deal_id):
    """View deal details.
    
    Args:
        deal_id (int): Deal ID
        
    Returns:
        Response: Deal detail page
    """
    deal = Deal.query.get_or_404(deal_id)
    
    # Check permission
    if not current_user.is_admin() and deal.owner_id != current_user.id:
        flash('You do not have permission to view this deal.', 'error')
        return redirect(url_for('deals.list_deals'))
    
    # Get related data
    activities = deal.activities.order_by(
        Activity.created_at.desc()
    ).limit(20).all()
    
    tasks = deal.tasks.filter_by(
        status='pending'
    ).order_by(
        Deal.due_date.asc()
    ).all()
    
    notes = deal.notes_list.order_by(
        Deal.created_at.desc()
    ).limit(10).all()
    
    return render_template(
        'deals/view.html',
        deal=deal,
        activities=activities,
        tasks=tasks,
        notes=notes
    )


@deals_bp.route('/<int:deal_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_deal(deal_id):
    """Edit deal details.
    
    Args:
        deal_id (int): Deal ID
        
    Returns:
        Response: Edit form ya redirect to deal detail
    """
    deal = Deal.query.get_or_404(deal_id)
    
    # Check permission
    if not current_user.can_edit(deal):
        flash('You do not have permission to edit this deal.', 'error')
        return redirect(url_for('deals.view_deal', deal_id=deal_id))
    
    if request.method == 'POST':
        # Update fields
        deal.title = request.form.get('title', '').strip()
        deal.description = request.form.get('description', '').strip()
        deal.value = request.form.get('value', type=float)
        deal.currency = request.form.get('currency', 'INR')
        deal.stage = request.form.get('stage', 'prospecting')
        deal.source = request.form.get('source', '').strip()
        deal.products = request.form.get('products', '').strip()
        deal.notes = request.form.get('notes', '').strip()
        
        # Parse expected close date
        expected_close_date = request.form.get('expected_close_date')
        if expected_close_date:
            try:
                deal.expected_close_date = datetime.strptime(
                    expected_close_date, '%Y-%m-%d'
                ).date()
            except ValueError:
                flash('Invalid date format.', 'error')
        
        try:
            # Update probability if stage changed
            deal.move_to_stage(deal.stage)
            
            db.session.commit()
            flash('Deal updated successfully!', 'success')
            return redirect(url_for('deals.view_deal', deal_id=deal.id))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Error updating deal: {str(e)}')
            flash('An error occurred while updating the deal.', 'error')
    
    contacts = Contact.query.filter_by(
        owner_id=current_user.id
    ).order_by(Contact.company).all()
    
    return render_template('deals/edit.html', deal=deal, contacts=contacts)


@deals_bp.route('/<int:deal_id>/move-stage', methods=['POST'])
@login_required
def move_deal_stage(deal_id):
    """Move deal to different stage.
    
    Args:
        deal_id (int): Deal ID
        
    Returns:
        JSON: Success status
    """
    deal = Deal.query.get_or_404(deal_id)
    
    if not current_user.can_edit(deal):
        return jsonify({'error': 'Permission denied'}), 403
    
    new_stage = request.json.get('stage')
    
    if not new_stage:
        return jsonify({'error': 'Stage is required'}), 400
    
    try:
        old_stage = deal.stage
        deal.move_to_stage(new_stage)
        
        # Log activity
        activity = Activity(
            activity_type='note',
            subject='Deal Stage Updated',
            description=f'Deal moved from {old_stage} to {new_stage}',
            user_id=current_user.id,
            deal_id=deal.id,
            is_completed=True,
            completed_at=datetime.utcnow()
        )
        db.session.add(activity)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'stage': deal.stage,
            'probability': deal.probability,
            'status': deal.status
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@deals_bp.route('/<int:deal_id>/mark-won', methods=['POST'])
@login_required
def mark_deal_won(deal_id):
    """Mark deal as won.
    
    Args:
        deal_id (int): Deal ID
        
    Returns:
        Response: Redirect to deal detail
    """
    deal = Deal.query.get_or_404(deal_id)
    
    if not current_user.can_edit(deal):
        flash('You do not have permission to edit this deal.', 'error')
        return redirect(url_for('deals.view_deal', deal_id=deal_id))
    
    try:
        deal.mark_as_won()
        
        # Log activity
        activity = Activity(
            activity_type='note',
            subject='Deal Won!',
            description=f'Deal "{deal.title}" was marked as won',
            user_id=current_user.id,
            deal_id=deal.id,
            contact_id=deal.contact_id,
            is_completed=True,
            completed_at=datetime.utcnow()
        )
        db.session.add(activity)
        db.session.commit()
        
        flash(f'Congratulations! Deal "{deal.title}" marked as won!', 'success')
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Error marking deal as won: {str(e)}')
        flash('An error occurred.', 'error')
    
    return redirect(url_for('deals.view_deal', deal_id=deal_id))


@deals_bp.route('/<int:deal_id>/mark-lost', methods=['POST'])
@login_required
def mark_deal_lost(deal_id):
    """Mark deal as lost.
    
    Args:
        deal_id (int): Deal ID
        
    Returns:
        Response: Redirect to deal detail
    """
    deal = Deal.query.get_or_404(deal_id)
    
    if not current_user.can_edit(deal):
        flash('You do not have permission to edit this deal.', 'error')
        return redirect(url_for('deals.view_deal', deal_id=deal_id))
    
    reason = request.form.get('lost_reason', '').strip()
    
    try:
        deal.mark_as_lost(reason=reason)
        
        # Log activity
        activity = Activity(
            activity_type='note',
            subject='Deal Lost',
            description=f'Deal "{deal.title}" was marked as lost. Reason: {reason}',
            user_id=current_user.id,
            deal_id=deal.id,
            contact_id=deal.contact_id,
            is_completed=True,
            completed_at=datetime.utcnow()
        )
        db.session.add(activity)
        db.session.commit()
        
        flash(f'Deal "{deal.title}" marked as lost.', 'info')
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Error marking deal as lost: {str(e)}')
        flash('An error occurred.', 'error')
    
    return redirect(url_for('deals.view_deal', deal_id=deal_id))
