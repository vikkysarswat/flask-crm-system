"""User model for authentication and authorization.

Yeh model CRM system ke users ko represent karta hai.
Authentication, authorization aur user management handle karta hai.

"""

from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db


class User(UserMixin, db.Model):
    """User model for CRM system users.
    
    Yeh class system ke users ko represent karti hai.
    Admin, manager, aur regular users ke roles support karta hai.
    
    Attributes:
        id (int): Primary key
        email (str): User email (unique)
        password_hash (str): Hashed password
        first_name (str): User first name
        last_name (str): User last name
        role (str): User role (admin/manager/user)
        is_active (bool): Account active status
        phone (str): Contact phone number
        avatar (str): Profile picture URL
        created_at (datetime): Account creation timestamp
        last_login (datetime): Last login timestamp
    """
    
    __tablename__ = 'users'
    
    # Primary fields
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # Personal information
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(20))
    avatar = db.Column(db.String(255))
    
    # Role and permissions
    role = db.Column(
        db.String(20),
        nullable=False,
        default='user',
        index=True
    )  # admin, manager, user
    
    # Account status
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    last_login = db.Column(db.DateTime)
    
    # Relationships
    # User ke saath associated leads, contacts, deals, etc.
    owned_leads = db.relationship(
        'Lead',
        backref='owner',
        lazy='dynamic',
        foreign_keys='Lead.owner_id'
    )
    owned_contacts = db.relationship(
        'Contact',
        backref='owner',
        lazy='dynamic',
        foreign_keys='Contact.owner_id'
    )
    owned_deals = db.relationship(
        'Deal',
        backref='owner',
        lazy='dynamic',
        foreign_keys='Deal.owner_id'
    )
    activities = db.relationship(
        'Activity',
        backref='user',
        lazy='dynamic',
        foreign_keys='Activity.user_id'
    )
    tasks = db.relationship(
        'Task',
        backref='assigned_to_user',
        lazy='dynamic',
        foreign_keys='Task.assigned_to'
    )
    
    def __repr__(self):
        """String representation of User."""
        return f'<User {self.email}>'
    
    def set_password(self, password):
        """Hash and set user password.
        
        Password ko securely hash karke store karta hai.
        
        Args:
            password (str): Plain text password
            
        Example:
            >>> user.set_password('mysecretpassword')
        """
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verify user password.
        
        Password ko hash ke saath compare karta hai.
        
        Args:
            password (str): Plain text password to verify
            
        Returns:
            bool: True if password matches, False otherwise
            
        Example:
            >>> if user.check_password('enteredpassword'):
            ...     print('Login successful')
        """
        return check_password_hash(self.password_hash, password)
    
    @property
    def full_name(self):
        """Get user's full name.
        
        Returns:
            str: Full name (first + last)
        """
        return f"{self.first_name} {self.last_name}"
    
    def is_admin(self):
        """Check if user has admin role.
        
        Returns:
            bool: True if user is admin
        """
        return self.role == 'admin'
    
    def is_manager(self):
        """Check if user has manager role.
        
        Returns:
            bool: True if user is manager or admin
        """
        return self.role in ['admin', 'manager']
    
    def can_edit(self, resource):
        """Check if user can edit a resource.
        
        Resource ko edit karne ki permission check karta hai.
        
        Args:
            resource: Database model instance with owner_id
            
        Returns:
            bool: True if user can edit the resource
            
        Example:
            >>> if current_user.can_edit(lead):
            ...     # Allow editing
        """
        if self.is_admin():
            return True
        
        if hasattr(resource, 'owner_id'):
            return resource.owner_id == self.id
        
        return False
    
    def to_dict(self):
        """Convert user object to dictionary.
        
        API responses ke liye user data ko dict format mein convert karta hai.
        
        Returns:
            dict: User data dictionary
        """
        return {
            'id': self.id,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.full_name,
            'phone': self.phone,
            'role': self.role,
            'is_active': self.is_active,
            'avatar': self.avatar,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }
