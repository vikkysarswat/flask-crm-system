"""Note model for rich text notes and attachments.

Yeh model contacts, leads aur deals ke notes store karta hai.

"""

from datetime import datetime
from app import db


class Note(db.Model):
    """Note model for storing rich text notes.
    
    Yeh class CRM entities ke saath notes associate karti hai.
    Rich text content aur attachments support karti hai.
    
    Attributes:
        id (int): Primary key
        title (str): Note title
        content (str): Note content (can be rich text/HTML)
        is_pinned (bool): Pin status
        user_id (int): Note creator
        contact_id (int): Associated contact
        lead_id (int): Associated lead
        deal_id (int): Associated deal
        attachments (str): File attachment paths (JSON)
        created_at (datetime): Creation timestamp
        updated_at (datetime): Last update timestamp
    """
    
    __tablename__ = 'notes'
    
    # Primary fields
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    content = db.Column(db.Text, nullable=False)
    is_pinned = db.Column(db.Boolean, default=False)
    
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
    
    # Attachments (stored as JSON string)
    attachments = db.Column(db.Text)  # JSON array of file paths
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    
    # Relationship with user
    author = db.relationship('User', foreign_keys=[user_id])
    
    def __repr__(self):
        """String representation of Note."""
        return f'<Note {self.title or self.id}>'
    
    def to_dict(self):
        """Convert note to dictionary.
        
        Returns:
            dict: Note data
        """
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'is_pinned': self.is_pinned,
            'user_id': self.user_id,
            'contact_id': self.contact_id,
            'lead_id': self.lead_id,
            'deal_id': self.deal_id,
            'attachments': self.attachments,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
