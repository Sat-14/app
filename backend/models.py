from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    bills = db.relationship('Bill', backref='user', lazy=True, cascade='all, delete-orphan')
    reminder_settings = db.relationship('ReminderSettings', backref='user', uselist=False, cascade='all, delete-orphan')
    
    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        logger.info(f"[USER MODEL] Creating new user with email: {kwargs.get('email')}")
        logger.debug(f"[USER MODEL] User data: name={kwargs.get('name')}, phone={kwargs.get('phone_number')}")
    
    def __repr__(self):
        return f'<User {self.id}: {self.email}>'
    
    @property
    def _details(self):
        """Property for detailed logging"""
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'phone_number': self.phone_number,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Bill(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    due_date = db.Column(db.DateTime, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    frequency = db.Column(db.String(20), nullable=False)
    is_paid = db.Column(db.Boolean, default=False)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Reminder preferences
    enable_whatsapp = db.Column(db.Boolean, default=True)
    enable_call = db.Column(db.Boolean, default=False)
    enable_sms = db.Column(db.Boolean, default=False)
    enable_local_notification = db.Column(db.Boolean, default=True)
    
    payments = db.relationship('Payment', backref='bill', lazy=True, cascade='all, delete-orphan')
    loan_details = db.relationship('LoanDetails', backref='bill', uselist=False, cascade='all, delete-orphan')
    
    def __init__(self, **kwargs):
        super(Bill, self).__init__(**kwargs)
        logger.info(f"[BILL MODEL] Creating new bill: {kwargs.get('name')} for user: {kwargs.get('user_id')}")
        logger.debug(f"[BILL MODEL] Bill details: amount={kwargs.get('amount')}, due_date={kwargs.get('due_date')}, category={kwargs.get('category')}")
        logger.debug(f"[BILL MODEL] Reminder settings: whatsapp={kwargs.get('enable_whatsapp', True)}, call={kwargs.get('enable_call', False)}")
    
    def __repr__(self):
        return f'<Bill {self.id}: {self.name}>'
    
    @property
    def _details(self):
        """Property for detailed logging"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'amount': self.amount,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'category': self.category,
            'frequency': self.frequency,
            'is_paid': self.is_paid,
            'enable_whatsapp': self.enable_whatsapp,
            'enable_call': self.enable_call,
            'notes': self.notes[:50] + '...' if self.notes and len(self.notes) > 50 else self.notes
        }
    
    @property
    def days_until_due(self):
        """Calculate days until due date"""
        if self.due_date:
            days = (self.due_date.date() - datetime.now().date()).days
            logger.debug(f"[BILL MODEL] Bill {self.id} days until due: {days}")
            return days
        return None

class Payment(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    bill_id = db.Column(db.String(36), db.ForeignKey('bill.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_date = db.Column(db.DateTime, default=datetime.utcnow)
    payment_method = db.Column(db.String(50))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, **kwargs):
        super(Payment, self).__init__(**kwargs)
        logger.info(f"[PAYMENT MODEL] Creating new payment for bill: {kwargs.get('bill_id')}")
        logger.debug(f"[PAYMENT MODEL] Payment details: amount={kwargs.get('amount')}, method={kwargs.get('payment_method')}")
    
    def __repr__(self):
        return f'<Payment {self.id}: {self.amount}>'
    
    @property
    def _details(self):
        """Property for detailed logging"""
        return {
            'id': self.id,
            'bill_id': self.bill_id,
            'amount': self.amount,
            'payment_date': self.payment_date.isoformat() if self.payment_date else None,
            'payment_method': self.payment_method,
            'notes': self.notes[:50] + '...' if self.notes and len(self.notes) > 50 else self.notes
        }

class ReminderSettings(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    local_notifications = db.Column(db.Boolean, default=True)
    whatsapp_enabled = db.Column(db.Boolean, default=False)
    call_enabled = db.Column(db.Boolean, default=False)
    sms_enabled = db.Column(db.Boolean, default=False)
    days_before = db.Column(db.Integer, default=3)
    preferred_time = db.Column(db.String(5), default='09:00')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, **kwargs):
        super(ReminderSettings, self).__init__(**kwargs)
        logger.info(f"[REMINDER SETTINGS] Creating settings for user: {kwargs.get('user_id')}")
        logger.debug(f"[REMINDER SETTINGS] Settings: whatsapp={kwargs.get('whatsapp_enabled', False)}, call={kwargs.get('call_enabled', False)}")
        logger.debug(f"[REMINDER SETTINGS] Timing: days_before={kwargs.get('days_before', 3)}, preferred_time={kwargs.get('preferred_time', '09:00')}")
    
    def __repr__(self):
        return f'<ReminderSettings {self.id}: User {self.user_id}>'
    
    @property
    def _details(self):
        """Property for detailed logging"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'local_notifications': self.local_notifications,
            'whatsapp_enabled': self.whatsapp_enabled,
            'call_enabled': self.call_enabled,
            'sms_enabled': self.sms_enabled,
            'days_before': self.days_before,
            'preferred_time': self.preferred_time,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class LoanDetails(db.Model):
    """Track loan/EMI details for bills"""
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    bill_id = db.Column(db.String(36), db.ForeignKey('bill.id'), nullable=False, unique=True)
    
    # Loan basic details
    total_amount = db.Column(db.Float, nullable=False)  # Total loan amount
    monthly_payment = db.Column(db.Float, nullable=False)  # EMI/Monthly payment
    interest_rate = db.Column(db.Float, default=0)  # Annual interest rate (optional)
    total_installments = db.Column(db.Integer, nullable=False)  # Total number of installments
    
    # Payment tracking
    installments_paid = db.Column(db.Integer, default=0)  # Number of installments paid
    total_paid = db.Column(db.Float, default=0)  # Total amount paid so far
    amount_remaining = db.Column(db.Float)  # Remaining amount to pay
    
    # Dates
    loan_start_date = db.Column(db.DateTime, nullable=False)
    expected_completion_date = db.Column(db.DateTime)
    last_payment_date = db.Column(db.DateTime)
    next_payment_date = db.Column(db.DateTime)
    
    # Additional tracking
    payment_history = db.Column(db.Text)  # JSON string of payment history
    is_active = db.Column(db.Boolean, default=True)
    notes = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, **kwargs):
        super(LoanDetails, self).__init__(**kwargs)
        self.calculate_loan_details()
        logger.info(f"[LOAN MODEL] Creating loan details for bill: {kwargs.get('bill_id')}")
    
    def calculate_loan_details(self):
        """Calculate loan details like remaining amount and completion date"""
        if self.total_amount and self.monthly_payment:
            # Calculate remaining amount
            self.amount_remaining = self.total_amount - self.total_paid
            
            # Calculate expected completion date if not set
            if not self.expected_completion_date and self.total_installments:
                from dateutil.relativedelta import relativedelta
                self.expected_completion_date = self.loan_start_date + relativedelta(months=self.total_installments)
            
            # Calculate next payment date
            if self.loan_start_date:
                from dateutil.relativedelta import relativedelta
                self.next_payment_date = self.loan_start_date + relativedelta(months=self.installments_paid + 1)
    
    def make_payment(self, amount=None):
        """Record a payment for the loan"""
        import json
        from datetime import datetime
        
        payment_amount = amount or self.monthly_payment
        
        # Update payment tracking
        self.installments_paid += 1
        self.total_paid += payment_amount
        self.amount_remaining = self.total_amount - self.total_paid
        self.last_payment_date = datetime.utcnow()
        
        # Update payment history
        payment_record = {
            'installment_no': self.installments_paid,
            'amount': payment_amount,
            'date': self.last_payment_date.isoformat(),
            'remaining': self.amount_remaining
        }
        
        if self.payment_history:
            history = json.loads(self.payment_history)
        else:
            history = []
        
        history.append(payment_record)
        self.payment_history = json.dumps(history)
        
        # Calculate next payment date
        from dateutil.relativedelta import relativedelta
        self.next_payment_date = self.loan_start_date + relativedelta(months=self.installments_paid + 1)
        
        # Check if loan is completed
        if self.installments_paid >= self.total_installments or self.amount_remaining <= 0:
            self.is_active = False
            logger.info(f"[LOAN MODEL] Loan completed for bill {self.bill_id}")
        
        self.updated_at = datetime.utcnow()
        
        return {
            'installment_no': self.installments_paid,
            'amount_paid': payment_amount,
            'amount_remaining': self.amount_remaining,
            'is_completed': not self.is_active
        }

# Database event listeners for logging
from sqlalchemy import event

@event.listens_for(User, 'after_insert')
def log_user_insert(mapper, connection, target):
    logger.info(f"[DB EVENT] User created: {target._details}")

@event.listens_for(User, 'after_update')
def log_user_update(mapper, connection, target):
    logger.info(f"[DB EVENT] User updated: {target._details}")

@event.listens_for(User, 'after_delete')
def log_user_delete(mapper, connection, target):
    logger.info(f"[DB EVENT] User deleted: {target.id}")

@event.listens_for(Bill, 'after_insert')
def log_bill_insert(mapper, connection, target):
    logger.info(f"[DB EVENT] Bill created: {target._details}")

@event.listens_for(Bill, 'after_update')
def log_bill_update(mapper, connection, target):
    logger.info(f"[DB EVENT] Bill updated: {target._details}")
    if hasattr(target, '_sa_instance_state'):
        # Log what changed
        history = db.inspect(target).attrs
        changes = {}
        for attr in history:
            hist = attr.history
            if hist.has_changes():
                changes[attr.key] = {
                    'from': hist.deleted[0] if hist.deleted else None,
                    'to': hist.added[0] if hist.added else None
                }
        if changes:
            logger.debug(f"[DB EVENT] Bill {target.id} changes: {changes}")

@event.listens_for(Bill, 'after_delete')
def log_bill_delete(mapper, connection, target):
    logger.info(f"[DB EVENT] Bill deleted: {target.id} - {target.name}")

@event.listens_for(Payment, 'after_insert')
def log_payment_insert(mapper, connection, target):
    logger.info(f"[DB EVENT] Payment created: {target._details}")

@event.listens_for(ReminderSettings, 'after_insert')
def log_settings_insert(mapper, connection, target):
    logger.info(f"[DB EVENT] ReminderSettings created: {target._details}")

@event.listens_for(ReminderSettings, 'after_update')
def log_settings_update(mapper, connection, target):
    logger.info(f"[DB EVENT] ReminderSettings updated: {target._details}")
