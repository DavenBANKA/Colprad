from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
import secrets

db = SQLAlchemy()

class Order(db.Model):
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(20), unique=True, nullable=False)
    ticket_type = db.Column(db.String(20), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    unit_price = db.Column(db.Float, nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    promo_code = db.Column(db.String(50))
    discount_amount = db.Column(db.Float, default=0)
    
    # Customer info
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    organization = db.Column(db.String(200))
    
    # Payment info
    payment_method = db.Column(db.String(50))
    payment_reference = db.Column(db.String(100))
    payment_status = db.Column(db.String(20), default='pending')
    
    # Status
    status = db.Column(db.String(20), default='pending')
    checked_in = db.Column(db.Boolean, default=False)
    check_in_time = db.Column(db.DateTime)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, **kwargs):
        super(Order, self).__init__(**kwargs)
        if not self.order_number:
            self.order_number = self.generate_order_number()
    
    @staticmethod
    def generate_order_number():
        return f"COLPRAD{datetime.now().strftime('%Y%m%d')}{secrets.token_hex(3).upper()}"
    
    def to_dict(self):
        return {
            'id': self.id,
            'order_number': self.order_number,
            'ticket_type': self.ticket_type,
            'quantity': self.quantity,
            'total_amount': self.total_amount,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'phone': self.phone,
            'payment_status': self.payment_status,
            'status': self.status,
            'checked_in': self.checked_in,
            'created_at': self.created_at.isoformat()
        }


class PromoCode(db.Model):
    __tablename__ = 'promo_codes'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False)
    discount_type = db.Column(db.String(20), nullable=False)  # percentage or fixed
    discount_value = db.Column(db.Float, nullable=False)
    max_uses = db.Column(db.Integer)
    uses_count = db.Column(db.Integer, default=0)
    valid_from = db.Column(db.DateTime)
    valid_until = db.Column(db.DateTime)
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Speaker(db.Model):
    __tablename__ = 'speakers'
    
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(100))
    bio_fr = db.Column(db.Text)
    bio_en = db.Column(db.Text)
    photo_url = db.Column(db.String(255))
    session_time = db.Column(db.String(50))
    email = db.Column(db.String(120))
    order_index = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class ContactMessage(db.Model):
    __tablename__ = 'contact_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    subject = db.Column(db.String(200))
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='new')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Newsletter(db.Model):
    __tablename__ = 'newsletter'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    subscribed = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Alert(db.Model):
    __tablename__ = 'alerts'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    alert_type = db.Column(db.String(20), nullable=False)  # info, warning, danger, success
    active = db.Column(db.Boolean, default=True)
    priority = db.Column(db.Integer, default=0)  # 0=normal, 1=high, 2=urgent
    created_by = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)
    
    def is_active(self):
        if not self.active:
            return False
        if self.expires_at and self.expires_at < datetime.utcnow():
            return False
        return True


class IncidentReport(db.Model):
    __tablename__ = 'incident_reports'
    
    id = db.Column(db.Integer, primary_key=True)
    incident_type = db.Column(db.String(50), nullable=False)  # technical, medical, security, queue
    severity = db.Column(db.String(20), nullable=False)  # low, medium, high, critical
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(200))
    actions_taken = db.Column(db.Text)
    status = db.Column(db.String(20), default='open')  # open, in_progress, resolved, closed
    reported_by = db.Column(db.String(100))
    resolved_by = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    resolved_at = db.Column(db.DateTime)
    impact_assessment = db.Column(db.Text)
    communication_sent = db.Column(db.Boolean, default=False)
