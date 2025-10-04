"""Contact management routes.

Yeh module contact CRUD operations handle karta hai.

"""

from flask import (
    Blueprint, render_template, redirect, url_for,
    flash, request, jsonify, current_app
)
from flask_login import login_required, current_user
from sqlalchemy import or_
from app import db
from app.models.contact import Contact
from app.models.activity import Activity
from app.models.deal import Deal
from datetime import datetime


contacts_bp = Blueprint('contacts', __name__, url_prefix='/contacts')


@contacts_bp.route('/')
@login_required
def list_contacts():
    """List all contacts with pagination and filters.
    
    Contacts ko list view mein display karta hai.
    Filtering, sorting aur pagination support karta hai.
    
    Returns:
        Response: Contacts list page
    """
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config.get('ITEMS_PER_PAGE', 20)
    
    # Search query
    search = request.args.get('search', '').strip()
    status = request.args.get('status', '')
    source = request.args.get('source', '')
    
    # Base query
    query = Contact.query
    
    # Apply filters
    if not current_user.is_admin():
        query = query.filter_by(owner_id=current_user.id)
    
    if search:
        query = query.filter(
            or_(
                Contact.first_name.ilike(f'%{search}%'),
                Contact.last_name.ilike(f'%{search}%'),
                Contact.email.ilike(f'%{search}%'),
                Contact.company.ilike(f'%{search}%')
            )
        )
    
    if status:
        query = query.filter_by(status=status)
    
    if source:
        query = query.filter_by(source=source)
    
    # Pagination
    contacts = query.order_by(
        Contact.created_at.desc()
    ).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )
    
    return render_template(
        'contacts/list.html',
        contacts=contacts,
        search=search,
        status=status,
        source=source
    )


@contacts_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_contact():
    """Create new contact.
    
    Naya contact create karne ki functionality.
    
    Returns:
        Response: Create form ya redirect to contact detail
    """
    if request.method == 'POST':
        # Get form data
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        mobile = request.form.get('mobile', '').strip()
        company = request.form.get('company', '').strip()
        job_title = request.form.get('job_title', '').strip()
        source = request.form.get('source', '')
        website = request.form.get('website', '').strip()
        address = request.form.get('address', '').strip()
        city = request.form.get('city', '').strip()
        state = request.form.get('state', '').strip()
        country = request.form.get('country', 'India').strip()
        postal_code = request.form.get('postal_code', '').strip()
        notes = request.form.get('notes', '').strip()
        
        # Validation
        errors = []
        
        if not all([first_name, last_name, email]):
            errors.append('First name, last name and email are required.')
        
        if Contact.query.filter_by(email=email).first():
            errors.append('Contact with this email already exists.')
        
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('contacts/create.html')
        
        # Create contact
        try:
            contact = Contact(
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=phone,
                mobile=mobile,
                company=company,
                job_title=job_title,
                source=source,
                website=website,
                address=address,
                city=city,
                state=state,
                country=country,
                postal_code=postal_code,
                notes=notes,
                owner_id=current_user.id,
                status='active'
            )
            
            db.session.add(contact)
            db.session.commit()
            
            # Log activity
            activity = Activity(
                activity_type='note',
                subject='Contact Created',
                description=f'New contact {contact.full_name} was created',
                user_id=current_user.id,
                contact_id=contact.id,
                is_completed=True,
                completed_at=datetime.utcnow()
            )
            db.session.add(activity)
            db.session.commit()
            
            current_app.logger.info(
                f'Contact created: {contact.email} by {current_user.email}'
            )
            flash(f'Contact {contact.full_name} created successfully!', 'success')
            return redirect(url_for('contacts.view_contact', contact_id=contact.id))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Error creating contact: {str(e)}')
            flash('An error occurred while creating the contact.', 'error')
    
    return render_template('contacts/create.html')


@contacts_bp.route('/<int:contact_id>')
@login_required
def view_contact(contact_id):
    """View contact details.
    
    Contact ki complete details aur associated records display karta hai.
    
    Args:
        contact_id (int): Contact ID
        
    Returns:
        Response: Contact detail page
    """
    contact = Contact.query.get_or_404(contact_id)
    
    # Check permission
    if not current_user.is_admin() and contact.owner_id != current_user.id:
        flash('You do not have permission to view this contact.', 'error')
        return redirect(url_for('contacts.list_contacts'))
    
    # Get related data
    activities = contact.activities.order_by(
        Activity.created_at.desc()
    ).limit(20).all()
    
    deals = contact.deals.order_by(
        Deal.created_at.desc()
    ).all()
    
    notes = contact.notes_list.order_by(
        Contact.created_at.desc()
    ).limit(10).all()
    
    return render_template(
        'contacts/view.html',
        contact=contact,
        activities=activities,
        deals=deals,
        notes=notes
    )


@contacts_bp.route('/<int:contact_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_contact(contact_id):
    """Edit contact details.
    
    Contact ki information update karne ki functionality.
    
    Args:
        contact_id (int): Contact ID
        
    Returns:
        Response: Edit form ya redirect to contact detail
    """
    contact = Contact.query.get_or_404(contact_id)
    
    # Check permission
    if not current_user.can_edit(contact):
        flash('You do not have permission to edit this contact.', 'error')
        return redirect(url_for('contacts.view_contact', contact_id=contact_id))
    
    if request.method == 'POST':
        # Update fields
        contact.first_name = request.form.get('first_name', '').strip()
        contact.last_name = request.form.get('last_name', '').strip()
        contact.phone = request.form.get('phone', '').strip()
        contact.mobile = request.form.get('mobile', '').strip()
        contact.company = request.form.get('company', '').strip()
        contact.job_title = request.form.get('job_title', '').strip()
        contact.status = request.form.get('status', 'active')
        contact.source = request.form.get('source', '')
        contact.website = request.form.get('website', '').strip()
        contact.address = request.form.get('address', '').strip()
        contact.city = request.form.get('city', '').strip()
        contact.state = request.form.get('state', '').strip()
        contact.country = request.form.get('country', 'India').strip()
        contact.postal_code = request.form.get('postal_code', '').strip()
        contact.notes = request.form.get('notes', '').strip()
        
        try:
            db.session.commit()
            
            # Log activity
            activity = Activity(
                activity_type='note',
                subject='Contact Updated',
                description=f'Contact {contact.full_name} was updated',
                user_id=current_user.id,
                contact_id=contact.id,
                is_completed=True,
                completed_at=datetime.utcnow()
            )
            db.session.add(activity)
            db.session.commit()
            
            flash('Contact updated successfully!', 'success')
            return redirect(url_for('contacts.view_contact', contact_id=contact.id))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Error updating contact: {str(e)}')
            flash('An error occurred while updating the contact.', 'error')
    
    return render_template('contacts/edit.html', contact=contact)


@contacts_bp.route('/<int:contact_id>/delete', methods=['POST'])
@login_required
def delete_contact(contact_id):
    """Delete contact.
    
    Contact ko database se delete karta hai.
    
    Args:
        contact_id (int): Contact ID
        
    Returns:
        Response: Redirect to contacts list
    """
    contact = Contact.query.get_or_404(contact_id)
    
    # Check permission
    if not current_user.can_edit(contact):
        flash('You do not have permission to delete this contact.', 'error')
        return redirect(url_for('contacts.view_contact', contact_id=contact_id))
    
    try:
        contact_name = contact.full_name
        db.session.delete(contact)
        db.session.commit()
        
        current_app.logger.info(
            f'Contact deleted: {contact_name} by {current_user.email}'
        )
        flash(f'Contact {contact_name} deleted successfully!', 'success')
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Error deleting contact: {str(e)}')
        flash('An error occurred while deleting the contact.', 'error')
    
    return redirect(url_for('contacts.list_contacts'))


@contacts_bp.route('/api/search')
@login_required
def api_search_contacts():
    """API endpoint for contact search (for autocomplete).
    
    Contact search ke liye JSON API endpoint.
    
    Returns:
        JSON: List of matching contacts
    """
    query = request.args.get('q', '').strip()
    limit = request.args.get('limit', 10, type=int)
    
    if not query:
        return jsonify({'contacts': []})
    
    # Search contacts
    contacts = Contact.query.filter(
        or_(
            Contact.first_name.ilike(f'%{query}%'),
            Contact.last_name.ilike(f'%{query}%'),
            Contact.email.ilike(f'%{query}%'),
            Contact.company.ilike(f'%{query}%')
        )
    )
    
    if not current_user.is_admin():
        contacts = contacts.filter_by(owner_id=current_user.id)
    
    contacts = contacts.limit(limit).all()
    
    return jsonify({
        'contacts': [
            {
                'id': c.id,
                'name': c.full_name,
                'email': c.email,
                'company': c.company
            }
            for c in contacts
        ]
    })
