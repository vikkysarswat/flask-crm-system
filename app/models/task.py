"""Task model for task management and reminders.

Yeh model CRM mein tasks aur reminders manage karta hai.

"""

from datetime import datetime
from app import db


class Task(db.Model):
    """Task model for managing to-dos and reminders.
    
    Yeh class CRM ke tasks aur reminders ko manage karti hai.
    Due dates, priorities aur completion tracking provide karti hai.
    
    Attributes:
        id (int): Primary key
        title (str): Task title
        description (str): Task description
        priority (str): Priority level (low/medium/high/urgent)
        status (str): Task status (pending/in_progress/completed/cancelled)
        due_date (datetime): Due date and time
        completed_at (datetime): Completion timestamp
        assigned_to (int): Assigned user ID
        created_by (int): Task creator ID
        contact_id (int): Related contact
        lead_id (int): Related lead
        deal_id (int): Related deal
        reminder_sent (bool): Reminder notification status
        created_at (datetime): Creation timestamp
        updated_at (datetime): Last update timestamp
    """
    
    __tablename__ = 'tasks'
    
    # Primary fields
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    
    # Task properties
    priority = db.Column(
        db.String(20),
        default='medium',
        nullable=False
    )  # low, medium, high, urgent
    status = db.Column(
        db.String(20),
        default='pending',
        nullable=False,
        index=True
    )  # pending, in_progress, completed, cancelled
    
    # Scheduling
    due_date = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    
    # Assignment
    assigned_to = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        nullable=False,
        index=True
    )
    created_by = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        nullable=False
    )
    
    # Relationships
    contact_id = db.Column(db.Integer, db.ForeignKey('contacts.id'), index=True)
    lead_id = db.Column(db.Integer, db.ForeignKey('leads.id'), index=True)
    deal_id = db.Column(db.Integer, db.ForeignKey('deals.id'), index=True)
    
    # Reminder
    reminder_sent = db.Column(db.Boolean, default=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    
    # Relationship with creator
    creator = db.relationship('User', foreign_keys=[created_by])
    
    def __repr__(self):
        """String representation of Task."""
        return f'<Task {self.title}>'
    
    def mark_completed(self):
        """Mark task as completed."""
        self.status = 'completed'
        self.completed_at = datetime.utcnow()
    
    def is_overdue(self):
        """Check if task is overdue.
        
        Returns:
            bool: True if due date has passed and not completed
        """
        if self.status == 'completed' or not self.due_date:
            return False
        return self.due_date < datetime.utcnow()
    
    def get_priority_color(self):
        """Get color code for priority.
        
        Returns:
            str: CSS color class
        """
        colors = {
            'low': 'success',
            'medium': 'info',
            'high': 'warning',
            'urgent': 'danger'
        }
        return colors.get(self.priority, 'secondary')
    
    def to_dict(self):
        """Convert task to dictionary.
        
        Returns:
            dict: Task data
        """
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'priority': self.priority,
            'status': self.status,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'assigned_to': self.assigned_to,
            'created_by': self.created_by,
            'contact_id': self.contact_id,
            'lead_id': self.lead_id,
            'deal_id': self.deal_id,
            'is_overdue': self.is_overdue(),
            'priority_color': self.get_priority_color(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
