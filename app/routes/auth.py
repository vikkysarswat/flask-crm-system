"""Authentication routes for login, logout and registration.

Yeh module user authentication handle karta hai.

"""

from flask import (
    Blueprint, render_template, redirect, url_for, 
    flash, request, current_app
)
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime
from app import db
from app.models.user import User
from werkzeug.urls import url_parse


auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login endpoint.
    
    User ko login karne ki functionality provide karta hai.
    Credentials verify karke session create karta hai.
    
    Returns:
        Response: Login page ya redirect to dashboard
    """
    # Agar user already logged in hai toh dashboard pe redirect karo
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        remember = request.form.get('remember', False)
        
        # Validate input
        if not email or not password:
            flash('Email and password are required.', 'error')
            return render_template('auth/login.html')
        
        # Find user
        user = User.query.filter_by(email=email).first()
        
        # Verify credentials
        if user is None or not user.check_password(password):
            flash('Invalid email or password.', 'error')
            current_app.logger.warning(f'Failed login attempt for {email}')
            return render_template('auth/login.html')
        
        # Check if account is active
        if not user.is_active:
            flash('Your account has been deactivated. Please contact administrator.', 'error')
            return render_template('auth/login.html')
        
        # Login successful
        login_user(user, remember=remember)
        
        # Update last login timestamp
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        current_app.logger.info(f'User logged in: {user.email}')
        flash(f'Welcome back, {user.first_name}!', 'success')
        
        # Redirect to next page ya dashboard
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.dashboard')
        
        return redirect(next_page)
    
    return render_template('auth/login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    """User logout endpoint.
    
    User ko logout karke session destroy karta hai.
    
    Returns:
        Response: Redirect to login page
    """
    user_email = current_user.email
    logout_user()
    current_app.logger.info(f'User logged out: {user_email}')
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration endpoint.
    
    Naye users ko register karne ki functionality.
    Note: Production mein yeh route disable kar sakte hain.
    
    Returns:
        Response: Registration page ya redirect to login
    """
    # Agar user already logged in hai
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        password_confirm = request.form.get('password_confirm', '')
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        
        # Validate input
        errors = []
        
        if not all([email, password, first_name, last_name]):
            errors.append('All fields are required.')
        
        if password != password_confirm:
            errors.append('Passwords do not match.')
        
        if len(password) < 6:
            errors.append('Password must be at least 6 characters long.')
        
        if User.query.filter_by(email=email).first():
            errors.append('Email already registered.')
        
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('auth/register.html')
        
        # Create new user
        try:
            user = User(
                email=email,
                first_name=first_name,
                last_name=last_name,
                role='user',  # Default role
                is_active=True
            )
            user.set_password(password)
            
            db.session.add(user)
            db.session.commit()
            
            current_app.logger.info(f'New user registered: {email}')
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('auth.login'))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Registration error: {str(e)}')
            flash('An error occurred during registration. Please try again.', 'error')
    
    return render_template('auth/register.html')


@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Forgot password endpoint.
    
    Password reset request handle karta hai.
    
    Returns:
        Response: Forgot password page
    """
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        
        # TODO: Implement password reset email functionality
        flash('Password reset instructions have been sent to your email.', 'info')
        current_app.logger.info(f'Password reset requested for: {email}')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/forgot_password.html')
