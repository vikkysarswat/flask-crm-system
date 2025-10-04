"""Deal model for CRM system.

Yeh model sales opportunities aur deals ko represent karta hai.
Deal pipeline, forecasting aur revenue tracking handle karta hai.

"""

from datetime import datetime
from app import db


class Deal(db.Model):
    """Deal model for sales opportunity tracking.
    
    Yeh class sales deals aur opportunities ko represent karti hai.
    Deal stages, value tracking aur closure probability manage karti hai.
    
    Attributes:
        id (int): Primary key
        title (str): Deal name/title
        description (str): Deal description
        value (float): Deal monetary value
        currency (str): Currency code (INR/USD)
        stage (str): Deal stage (prospecting/qualified/proposal/negotiation/closed_won/closed_lost)
        probability (int): Win probability (0-100%)
        contact_id (int): Associated contact
        owner_id (int): Deal owner (sales rep)
        expected_close_date (date): Expected closing date
        actual_close_date (date): Actual closing date
        status (str): Deal status (open/won/lost)
        source (str): Deal source
        lost_reason (str): Reason for loss (if applicable)
        products (str): Products/services involved
        competitors (str): Competing vendors
        notes (str): Internal notes
        created_at (datetime): Creation timestamp
        updated_at (datetime): Last update timestamp
    """
    
    __tablename__ = 'deals'
    
    # Primary fields
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    
    # Financial information
    value = db.Column(db.Float, nullable=False, default=0.0)
    currency = db.Column(db.String(3), default='INR')  # INR, USD, EUR, etc.
    
    # Deal stage and status
    stage = db.Column(
        db.String(50),
        default='prospecting',
        nullable=False,
        index=True
    )  # prospecting, qualified, proposal, negotiation, closed_won, closed_lost
    probability = db.Column(db.Integer, default=10)  # 0-100 win probability
    status = db.Column(
        db.String(20),
        default='open',
        nullable=False,
        index=True
    )  # open, won, lost
    
    # Relationships
    contact_id = db.Column(
        db.Integer,
        db.ForeignKey('contacts.id'),
        nullable=False,
        index=True
    )
    owner_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        nullable=False,
        index=True
    )
    
    # Timeline
    expected_close_date = db.Column(db.Date)
    actual_close_date = db.Column(db.Date)
    
    # Additional information
    source = db.Column(db.String(50))  # inbound, outbound, referral, etc.
    lost_reason = db.Column(db.String(200))  # price, competitor, timing, etc.
    products = db.Column(db.Text)  # Products/services in this deal
    competitors = db.Column(db.Text)  # Competing vendors
    notes = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    
    # Relationships
    activities = db.relationship(
        'Activity',
        backref='deal',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )
    notes_list = db.relationship(
        'Note',
        backref='deal',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )
    tasks = db.relationship(
        'Task',
        backref='deal',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )
    
    def __repr__(self):
        """String representation of Deal."""
        return f'<Deal {self.title}>'
    
    def move_to_stage(self, new_stage):
        """Move deal to a new stage.
        
        Deal ko naye stage mein move karta hai aur probability update karta hai.
        
        Args:
            new_stage (str): New stage name
        """
        stage_probabilities = {
            'prospecting': 10,
            'qualified': 25,
            'proposal': 50,
            'negotiation': 75,
            'closed_won': 100,
            'closed_lost': 0
        }
        
        self.stage = new_stage
        self.probability = stage_probabilities.get(new_stage, self.probability)
        
        # Update status based on stage
        if new_stage == 'closed_won':
            self.status = 'won'
            self.actual_close_date = datetime.utcnow().date()
        elif new_stage == 'closed_lost':
            self.status = 'lost'
            self.actual_close_date = datetime.utcnow().date()
    
    def mark_as_won(self, close_date=None):
        """Mark deal as won.
        
        Args:
            close_date (date): Closing date (defaults to today)
        """
        self.status = 'won'
        self.stage = 'closed_won'
        self.probability = 100
        self.actual_close_date = close_date or datetime.utcnow().date()
    
    def mark_as_lost(self, reason=None, close_date=None):
        """Mark deal as lost.
        
        Args:
            reason (str): Reason for loss
            close_date (date): Closing date (defaults to today)
        """
        self.status = 'lost'
        self.stage = 'closed_lost'
        self.probability = 0
        self.lost_reason = reason
        self.actual_close_date = close_date or datetime.utcnow().date()
    
    def get_weighted_value(self):
        """Calculate weighted deal value.
        
        Probability ke basis pe weighted value calculate karta hai.
        
        Returns:
            float: Weighted value (value * probability / 100)
        """
        return (self.value * self.probability) / 100
    
    def is_overdue(self):
        """Check if deal is overdue.
        
        Returns:
            bool: True if expected close date has passed
        """
        if not self.expected_close_date or self.status != 'open':
            return False
        return self.expected_close_date < datetime.utcnow().date()
    
    def to_dict(self):
        """Convert deal to dictionary.
        
        Returns:
            dict: Deal data
        """
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'value': self.value,
            'currency': self.currency,
            'stage': self.stage,
            'probability': self.probability,
            'status': self.status,
            'contact_id': self.contact_id,
            'owner_id': self.owner_id,
            'expected_close_date': self.expected_close_date.isoformat() if self.expected_close_date else None,
            'actual_close_date': self.actual_close_date.isoformat() if self.actual_close_date else None,
            'source': self.source,
            'lost_reason': self.lost_reason,
            'weighted_value': self.get_weighted_value(),
            'is_overdue': self.is_overdue(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
