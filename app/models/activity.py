"""Activity model for tracking user actions and events.

Yeh model CRM system mein saare activities ko track karta hai.
Calls, emails, meetings aur other interactions log karta hai.

"""

from datetime import datetime
from app import db


class Activity(db.Model):
    """Activity model for tracking interactions and events.
    
    Yeh class CRM mein hone wale saare activities ko track karti hai.
    Timeline view aur activity history provide karti hai.
    
    Attributes:
        id (int): Primary key
        activity_type (str): Activity type (call/email/meeting/task/note)
        subject (str): Activity subject/title
        description (str): Detailed description
        outcome (str): Activity outcome
        duration (int): Duration in minutes
        user_id (int): User who performed activity
        contact_id (int): Related contact
        lead_id (int): Related lead
        deal_id (int): Related deal
        scheduled_at (datetime): Scheduled time
        completed_at (datetime): Completion time
        is_completed (bool): Completion status
        created_at (datetime): Creation timestamp
    """
    
    __tablename__ = 'activities'
    
    # Primary fields
    id = db.Column(db.Integer, primary_key=True)
    activity_type = db.Column(
        db.String(50),
        nullable=False,
        index=True
    )  # call, email, meeting, task, note, sms
    subject = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    
    # Activity details
    outcome = db.Column(db.String(100))  # successful, no_answer, follow_up_needed, etc.
    duration = db.Column(db.Integer)  # Duration in minutes
    
    # Relationships
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        nullable=False,
        index=True
    )
    contact_id = db.Column(db.Integer, db.ForeignKey('contacts.id'), index=True)
    lead_id = db.Column(db.Integer, db.ForeignKey('leads.id'), index=True)
    deal_id = db.Column(db.Integer, db.ForeignKey('deals.id'), index=True)
    
    # Scheduling
    scheduled_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    is_completed = db.Column(db.Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    
    def __repr__(self):
        """String representation of Activity."""
        return f'<Activity {self.activity_type}: {self.subject}>'
    
    def mark_completed(self, outcome=None):
        """Mark activity as completed.
        
        Args:
            outcome (str): Activity outcome
        """
        self.is_completed = True
        self.completed_at = datetime.utcnow()
        if outcome:
            self.outcome = outcome
    
    def is_overdue(self):
        """Check if activity is overdue.
        
        Returns:
            bool: True if scheduled time has passed and not completed
        """
        if self.is_completed or not self.scheduled_at:
            return False
        return self.scheduled_at < datetime.utcnow()
    
    def to_dict(self):
        """Convert activity to dictionary.
        
        Returns:
            dict: Activity data
        """
        return {
            'id': self.id,
            'activity_type': self.activity_type,
            'subject': self.subject,
            'description': self.description,
            'outcome': self.outcome,
            'duration': self.duration,
            'user_id': self.user_id,
            'contact_id': self.contact_id,
            'lead_id': self.lead_id,
            'deal_id': self.deal_id,
            'scheduled_at': self.scheduled_at.isoformat() if self.scheduled_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'is_completed': self.is_completed,
            'is_overdue': self.is_overdue(),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
