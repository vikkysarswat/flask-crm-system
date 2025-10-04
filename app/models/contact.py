"""Contact model for CRM system.

Yeh model customers aur contacts ko represent karta hai.
Contact management aur relationship tracking handle karta hai.

"""

from datetime import datetime
from app import db


class Contact(db.Model):
    """Contact model for customer and prospect information.
    
    Yeh class CRM system ke contacts ko represent karti hai.
    Customer information, communication history aur relationships store karti hai.
    
    Attributes:
        id (int): Primary key
        first_name (str): Contact first name
        last_name (str): Contact last name
        email (str): Contact email
        phone (str): Primary phone number
        mobile (str): Mobile phone number
        company (str): Company name
        job_title (str): Job designation
        status (str): Contact status (active/inactive/archived)
        source (str): Lead source (website/referral/campaign)
        owner_id (int): Assigned user ID
        address (str): Street address
        city (str): City
        state (str): State
        country (str): Country
        postal_code (str): PIN/ZIP code
        website (str): Company website
        linkedin (str): LinkedIn profile URL
        twitter (str): Twitter handle
        tags (str): Comma-separated tags
        notes (str): Additional notes
        created_at (datetime): Record creation timestamp
        updated_at (datetime): Last update timestamp
    """
    
    __tablename__ = 'contacts'
    
    # Primary fields
    id = db.Column(db.Integer, primary_key=True)
    
    # Personal information
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(20))
    mobile = db.Column(db.String(20))
    
    # Professional information
    company = db.Column(db.String(100), index=True)
    job_title = db.Column(db.String(100))
    
    # Status and assignment
    status = db.Column(
        db.String(20),
        default='active',
        nullable=False,
        index=True
    )  # active, inactive, archived
    source = db.Column(db.String(50))  # website, referral, campaign, etc.
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Address information
    address = db.Column(db.String(200))
    city = db.Column(db.String(50))
    state = db.Column(db.String(50))
    country = db.Column(db.String(50), default='India')
    postal_code = db.Column(db.String(20))
    
    # Social and web presence
    website = db.Column(db.String(200))
    linkedin = db.Column(db.String(200))
    twitter = db.Column(db.String(100))
    
    # Additional metadata
    tags = db.Column(db.Text)  # Comma-separated tags
    notes = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    last_contacted = db.Column(db.DateTime)
    
    # Relationships
    deals = db.relationship(
        'Deal',
        backref='contact',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )
    activities = db.relationship(
        'Activity',
        backref='contact',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )
    notes_list = db.relationship(
        'Note',
        backref='contact',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )
    communications = db.relationship(
        'Communication',
        backref='contact',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )
    
    def __repr__(self):
        """String representation of Contact."""
        return f'<Contact {self.full_name}>'
    
    @property
    def full_name(self):
        """Get contact's full name.
        
        Returns:
            str: Full name
        """
        return f"{self.first_name} {self.last_name}"
    
    @property
    def full_address(self):
        """Get formatted complete address.
        
        Returns:
            str: Formatted address or empty string
        """
        parts = [self.address, self.city, self.state, 
                 self.country, self.postal_code]
        return ', '.join([p for p in parts if p])
    
    def get_tags_list(self):
        """Get tags as a list.
        
        Returns:
            list: List of tag strings
        """
        if not self.tags:
            return []
        return [tag.strip() for tag in self.tags.split(',')]
    
    def set_tags_list(self, tags_list):
        """Set tags from a list.
        
        Args:
            tags_list (list): List of tag strings
        """
        if isinstance(tags_list, list):
            self.tags = ', '.join(tags_list)
        else:
            self.tags = str(tags_list)
    
    def to_dict(self):
        """Convert contact to dictionary.
        
        Returns:
            dict: Contact data
        """
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.full_name,
            'email': self.email,
            'phone': self.phone,
            'mobile': self.mobile,
            'company': self.company,
            'job_title': self.job_title,
            'status': self.status,
            'source': self.source,
            'owner_id': self.owner_id,
            'address': self.full_address,
            'website': self.website,
            'linkedin': self.linkedin,
            'twitter': self.twitter,
            'tags': self.get_tags_list(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_contacted': self.last_contacted.isoformat() if self.last_contacted else None
        }
