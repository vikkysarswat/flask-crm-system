"""Lead management routes.

Yeh module lead CRUD operations aur conversion handle karta hai.

"""

from flask import (
    Blueprint, render_template, redirect, url_for,
    flash, request, jsonify, current_app
)
from flask_login import login_required, current_user
from sqlalchemy import or_
from app import db
from app.models.lead import Lead
from app.models.contact import Contact
from app.models.activity import Activity
from datetime import datetime


leads_bp = Blueprint('leads', __name__, url_prefix='/leads')


@leads_bp.route('/')
@login_required
def list_leads():
    """List all leads with filters.
    
    Leads ko list view mein display karta hai.
    Status, score aur temperature ke basis pe filter karta hai.
    
    Returns:
        Response: Leads list page
    """
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config.get('ITEMS_PER_PAGE', 20)
    
    # Filters
    search = request.args.get('search', '').strip()
    status = request.args.get('status', '')
    temperature = request.args.get('temperature', '')
    source = request.args.get('source', '')
    
    # Base query
    query = Lead.query
    
    if not current_user.is_admin():
        query = query.filter_by(owner_id=current_user.id)
    
    if search:
        query = query.filter(
            or_(
                Lead.first_name.ilike(f'%{search}%'),
                Lead.last_name.ilike(f'%{search}%'),
                Lead.email.ilike(f'%{search}%'),
                Lead.company.ilike(f'%{search}%')
            )
        )
    
    if status:
        query = query.filter_by(status=status)
    
    if temperature:
        query = query.filter_by(temperature=temperature)
    
    if source:
        query = query.filter_by(source=source)
    
    # Pagination
    leads = query.order_by(
        Lead.score.desc(),
        Lead.created_at.desc()
    ).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )
    
    return render_template(
        'leads/list.html',
        leads=leads,
        search=search,
        status=status,
        temperature=temperature,
        source=source
    )


@leads_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_lead():
    """Create new lead.
    
    Naya lead create karne ki functionality.
    
    Returns:
        Response: Create form ya redirect to lead detail
    """
    if request.method == 'POST':
        # Get form data
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        company = request.form.get('company', '').strip()
        job_title = request.form.get('job_title', '').strip()
        industry = request.form.get('industry', '').strip()
        source = request.form.get('source', '')
        budget = request.form.get('budget', type=float)
        timeline = request.form.get('timeline', '').strip()
        requirements = request.form.get('requirements', '').strip()
        notes = request.form.get('notes', '').strip()
        
        # Validation
        errors = []
        
        if not all([first_name, last_name, email]):
            errors.append('First name, last name and email are required.')
        
        if Lead.query.filter_by(email=email).first():
            errors.append('Lead with this email already exists.')
        
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('leads/create.html')
        
        # Create lead
        try:
            lead = Lead(
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=phone,
                company=company,
                job_title=job_title,
                industry=industry,
                source=source,
                budget=budget,
                timeline=timeline,
                requirements=requirements,
                notes=notes,
                owner_id=current_user.id,
                status='new',
                score=0,
                temperature='cold'
            )
            
            db.session.add(lead)
            db.session.commit()
            
            # Log activity
            activity = Activity(
                activity_type='note',
                subject='Lead Created',
                description=f'New lead {lead.full_name} was created',
                user_id=current_user.id,
                lead_id=lead.id,
                is_completed=True,
                completed_at=datetime.utcnow()
            )
            db.session.add(activity)
            db.session.commit()
            
            current_app.logger.info(
                f'Lead created: {lead.email} by {current_user.email}'
            )
            flash(f'Lead {lead.full_name} created successfully!', 'success')
            return redirect(url_for('leads.view_lead', lead_id=lead.id))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Error creating lead: {str(e)}')
            flash('An error occurred while creating the lead.', 'error')
    
    return render_template('leads/create.html')


@leads_bp.route('/<int:lead_id>')
@login_required
def view_lead(lead_id):
    """View lead details.
    
    Lead ki complete information display karta hai.
    
    Args:
        lead_id (int): Lead ID
        
    Returns:
        Response: Lead detail page
    """
    lead = Lead.query.get_or_404(lead_id)
    
    # Check permission
    if not current_user.is_admin() and lead.owner_id != current_user.id:
        flash('You do not have permission to view this lead.', 'error')
        return redirect(url_for('leads.list_leads'))
    
    # Get related data
    activities = lead.activities.order_by(
        Activity.created_at.desc()
    ).limit(20).all()
    
    tasks = lead.tasks.filter_by(
        status='pending'
    ).order_by(
        Lead.due_date.asc()
    ).all()
    
    notes = lead.notes_list.order_by(
        Lead.created_at.desc()
    ).limit(10).all()
    
    return render_template(
        'leads/view.html',
        lead=lead,
        activities=activities,
        tasks=tasks,
        notes=notes
    )


@leads_bp.route('/<int:lead_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_lead(lead_id):
    """Edit lead details.
    
    Lead ki information update karne ki functionality.
    
    Args:
        lead_id (int): Lead ID
        
    Returns:
        Response: Edit form ya redirect to lead detail
    """
    lead = Lead.query.get_or_404(lead_id)
    
    # Check permission
    if not current_user.can_edit(lead):
        flash('You do not have permission to edit this lead.', 'error')
        return redirect(url_for('leads.view_lead', lead_id=lead_id))
    
    if request.method == 'POST':
        # Update fields
        lead.first_name = request.form.get('first_name', '').strip()
        lead.last_name = request.form.get('last_name', '').strip()
        lead.phone = request.form.get('phone', '').strip()
        lead.company = request.form.get('company', '').strip()
        lead.job_title = request.form.get('job_title', '').strip()
        lead.industry = request.form.get('industry', '').strip()
        lead.status = request.form.get('status', 'new')
        lead.source = request.form.get('source', '')
        lead.budget = request.form.get('budget', type=float)
        lead.timeline = request.form.get('timeline', '').strip()
        lead.requirements = request.form.get('requirements', '').strip()
        lead.notes = request.form.get('notes', '').strip()
        
        try:
            db.session.commit()
            flash('Lead updated successfully!', 'success')
            return redirect(url_for('leads.view_lead', lead_id=lead.id))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Error updating lead: {str(e)}')
            flash('An error occurred while updating the lead.', 'error')
    
    return render_template('leads/edit.html', lead=lead)


@leads_bp.route('/<int:lead_id>/convert', methods=['POST'])
@login_required
def convert_lead(lead_id):
    """Convert lead to contact.
    
    Lead ko contact mein convert karta hai.
    
    Args:
        lead_id (int): Lead ID
        
    Returns:
        Response: Redirect to new contact
    """
    lead = Lead.query.get_or_404(lead_id)
    
    # Check permission
    if not current_user.can_edit(lead):
        flash('You do not have permission to convert this lead.', 'error')
        return redirect(url_for('leads.view_lead', lead_id=lead_id))
    
    if lead.status == 'converted':
        flash('This lead has already been converted.', 'warning')
        return redirect(url_for('leads.view_lead', lead_id=lead_id))
    
    try:
        # Create contact from lead
        contact = Contact(
            first_name=lead.first_name,
            last_name=lead.last_name,
            email=lead.email,
            phone=lead.phone,
            company=lead.company,
            job_title=lead.job_title,
            source=lead.source,
            notes=lead.notes,
            owner_id=lead.owner_id,
            status='active'
        )
        
        db.session.add(contact)
        db.session.flush()  # Get contact ID
        
        # Mark lead as converted
        lead.convert_to_contact(contact.id)
        
        # Log activity
        activity = Activity(
            activity_type='note',
            subject='Lead Converted',
            description=f'Lead {lead.full_name} was converted to contact',
            user_id=current_user.id,
            lead_id=lead.id,
            contact_id=contact.id,
            is_completed=True,
            completed_at=datetime.utcnow()
        )
        db.session.add(activity)
        
        db.session.commit()
        
        current_app.logger.info(
            f'Lead converted: {lead.email} to contact by {current_user.email}'
        )
        flash(
            f'Lead {lead.full_name} converted to contact successfully!',
            'success'
        )
        return redirect(url_for('contacts.view_contact', contact_id=contact.id))
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Error converting lead: {str(e)}')
        flash('An error occurred while converting the lead.', 'error')
        return redirect(url_for('leads.view_lead', lead_id=lead_id))


@leads_bp.route('/<int:lead_id>/update-score', methods=['POST'])
@login_required
def update_lead_score(lead_id):
    """Update lead score.
    
    Lead score ko manually adjust karta hai.
    
    Args:
        lead_id (int): Lead ID
        
    Returns:
        JSON: Updated score
    """
    lead = Lead.query.get_or_404(lead_id)
    
    if not current_user.can_edit(lead):
        return jsonify({'error': 'Permission denied'}), 403
    
    points = request.json.get('points', 0)
    
    try:
        lead.update_score(points)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'score': lead.score,
            'temperature': lead.temperature
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
