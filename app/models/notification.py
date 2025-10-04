"""Notification model for in-app notifications.

Yeh model system notifications aur alerts manage karta hai.

"""

from datetime import datetime
from app import db


class Notification(db.Model):
    """Notification model for in-app notifications and alerts.
    
    Yeh class user notifications aur alerts ko manage karti hai.
    Real-time updates aur reminders provide karti hai.
    
    Attributes:
        id (int): Primary key
        user_id (int): Target user
        notification_type (str): Type (info/success/warning/error/reminder)
        title (str): Notification title
        message (str): Notification message
        action_url (str): Optional action URL
        is_read (bool): Read status
        read_at (datetime): Read timestamp
        priority (str): Priority level (low/normal/high)
        metadata (str): Additional data (JSON)
        created_at (datetime): Creation timestamp
    """
    
    __tablename__ = 'notifications'
    
    # Primary fields
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        nullable=False,
        index=True
    )
    
    # Notification content
    notification_type = db.Column(
        db.String(20),
        nullable=False
    )  # info, success, warning, error, reminder
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    action_url = db.Column(db.String(500))  # URL to navigate on click
    
    # Status
    is_read = db.Column(db.Boolean, default=False, nullable=False, index=True)
    read_at = db.Column(db.DateTime)
    
    # Priority
    priority = db.Column(
        db.String(10),
        default='normal'
    )  # low, normal, high
    
    # Metadata (JSON string)
    metadata = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationship
    user = db.relationship('User', backref='notifications')
    
    def __repr__(self):
        """String representation of Notification."""
        return f'<Notification {self.title}>'
    
    def mark_as_read(self):
        """Mark notification as read."""
        self.is_read = True
        self.read_at = datetime.utcnow()
    
    def get_icon(self):
        """Get icon for notification type.
        
        Returns:
            str: Font Awesome icon class
        """
        icons = {
            'info': 'fa-info-circle',
            'success': 'fa-check-circle',
            'warning': 'fa-exclamation-triangle',
            'error': 'fa-times-circle',
            'reminder': 'fa-bell'
        }
        return icons.get(self.notification_type, 'fa-info-circle')
    
    def get_color_class(self):
        """Get color class for notification type.
        
        Returns:
            str: CSS color class
        """
        colors = {
            'info': 'info',
            'success': 'success',
            'warning': 'warning',
            'error': 'danger',
            'reminder': 'primary'
        }
        return colors.get(self.notification_type, 'info')
    
    def to_dict(self):
        """Convert notification to dictionary.
        
        Returns:
            dict: Notification data
        """
        return {
            'id': self.id,
            'user_id': self.user_id,
            'notification_type': self.notification_type,
            'title': self.title,
            'message': self.message,
            'action_url': self.action_url,
            'is_read': self.is_read,
            'read_at': self.read_at.isoformat() if self.read_at else None,
            'priority': self.priority,
            'icon': self.get_icon(),
            'color_class': self.get_color_class(),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
