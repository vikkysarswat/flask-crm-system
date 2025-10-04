"""Lead model for CRM system.

Yeh model potential customers (leads) ko represent karta hai.
Lead tracking, scoring aur conversion handle karta hai.

"""

from datetime import datetime
from app import db


class Lead(db.Model):
    """Lead model for prospect management.
    
    Yeh class CRM ke leads ko represent karti hai.
    Lead qualification, scoring aur conversion tracking karti hai.
    
    Attributes:
        id (int): Primary key
        first_name (str): Lead first name
        last_name (str): Lead last name
        email (str): Lead email
        phone (str): Contact phone
        company (str): Company name
        job_title (str): Designation
        status (str): Lead status (new/contacted/qualified/lost/converted)
        source (str): Lead source
        score (int): Lead score (0-100)
        temperature (str): Lead temperature (hot/warm/cold)
        owner_id (int): Assigned sales rep
        industry (str): Industry type
        budget (float): Estimated budget
        timeline (str): Purchase timeline
        requirements (str): Lead requirements
        notes (str): Internal notes
        converted_to_contact_id (int): Contact ID after conversion
        converted_at (datetime): Conversion timestamp
        created_at (datetime): Creation timestamp
        updated_at (datetime): Last update timestamp
    """
    
    __tablename__ = 'leads'
    
    # Primary fields
    id = db.Column(db.Integer, primary_key=True)
    
    # Personal information
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(20))
    
    # Professional information
    company = db.Column(db.String(100), index=True)
    job_title = db.Column(db.String(100))
    industry = db.Column(db.String(50))
    
    # Lead qualification
    status = db.Column(
        db.String(20),
        default='new',
        nullable=False,
        index=True
    )  # new, contacted, qualified, lost, converted
    source = db.Column(db.String(50), index=True)
    score = db.Column(db.Integer, default=0)  # 0-100 scoring
    temperature = db.Column(
        db.String(10),
        default='cold'
    )  # hot, warm, cold
    
    # Assignment
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Sales information
    budget = db.Column(db.Float)  # Estimated budget
    timeline = db.Column(db.String(50))  # immediate, 1-3months, 3-6months, etc.
    requirements = db.Column(db.Text)
    notes = db.Column(db.Text)
    
    # Conversion tracking
    converted_to_contact_id = db.Column(db.Integer, db.ForeignKey('contacts.id'))
    converted_at = db.Column(db.DateTime)
    
    # Address information
    city = db.Column(db.String(50))
    state = db.Column(db.String(50))
    country = db.Column(db.String(50), default='India')
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    last_contacted = db.Column(db.DateTime)
    next_followup = db.Column(db.DateTime)
    
    # Relationships
    activities = db.relationship(
        'Activity',
        backref='lead',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )
    notes_list = db.relationship(
        'Note',
        backref='lead',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )
    tasks = db.relationship(
        'Task',
        backref='lead',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )
    
    def __repr__(self):
        """String representation of Lead."""
        return f'<Lead {self.full_name}>'
    
    @property
    def full_name(self):
        """Get lead's full name.
        
        Returns:
            str: Full name
        """
        return f"{self.first_name} {self.last_name}"
    
    def update_score(self, points):
        """Update lead score.
        
        Lead score ko update karta hai aur temperature adjust karta hai.
        
        Args:
            points (int): Points to add (can be negative)
        """
        self.score = max(0, min(100, self.score + points))
        
        # Update temperature based on score
        if self.score >= 70:
            self.temperature = 'hot'
        elif self.score >= 40:
            self.temperature = 'warm'
        else:
            self.temperature = 'cold'
    
    def convert_to_contact(self, contact_id):
        """Mark lead as converted.
        
        Lead ko contact mein convert karta hai.
        
        Args:
            contact_id (int): Created contact ID
        """
        self.status = 'converted'
        self.converted_to_contact_id = contact_id
        self.converted_at = datetime.utcnow()
    
    def is_qualified(self):
        """Check if lead is qualified.
        
        Returns:
            bool: True if lead score is >= 50
        """
        return self.score >= 50
    
    def to_dict(self):
        """Convert lead to dictionary.
        
        Returns:
            dict: Lead data
        """
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.full_name,
            'email': self.email,
            'phone': self.phone,
            'company': self.company,
            'job_title': self.job_title,
            'industry': self.industry,
            'status': self.status,
            'source': self.source,
            'score': self.score,
            'temperature': self.temperature,
            'owner_id': self.owner_id,
            'budget': self.budget,
            'timeline': self.timeline,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'next_followup': self.next_followup.isoformat() if self.next_followup else None
        }
