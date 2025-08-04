from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
from models import db, Bill, User, ReminderSettings
from reminder_service import generate_reminder_message, send_whatsapp_reminder, send_voice_reminder
import pytz

# We will not import 'app' in this file at all to avoid circular imports.

scheduler = BackgroundScheduler()

def start_scheduler(app):
    """
    Initializes and starts the background scheduler.
    The job functions are defined inside so they have access to the 'app' context
    without causing circular import errors.
    """

    def check_and_send_reminders():
        """This job runs every minute to check for upcoming reminders."""
        # This function can now use the 'app' variable from the outer scope
        with app.app_context():
            print("Scheduler: Checking for due bills...")
            users = User.query.filter(User.phone_number.isnot(None)).all()
            
            for user in users:
                settings = ReminderSettings.query.filter_by(user_id=user.id).first()
                if not settings:
                    continue
                
                current_time = datetime.now().strftime('%H:%M')
                if current_time != settings.preferred_time:
                    continue
                
                reminder_date = datetime.now() + timedelta(days=settings.days_before)
                bills_due = Bill.query.filter(
                    Bill.user_id == user.id,
                    Bill.is_paid == False,
                    Bill.due_date <= reminder_date,
                    Bill.due_date >= datetime.now()
                ).all()
                
                for bill in bills_due:
                    bill_data = {
                        'name': bill.name,
                        'amount': bill.amount,
                        'due_date': bill.due_date.strftime('%Y-%m-%d')
                    }
                    message = generate_reminder_message(user.name, bill_data)
                    
                    if settings.whatsapp_enabled and bill.enable_whatsapp:
                        send_whatsapp_reminder(user.phone_number, message)
                    
                    if settings.call_enabled and bill.enable_call:
                        send_voice_reminder(user.phone_number, message)

    def check_overdue_bills():
        """This job runs daily to check for overdue bills."""
        # This function can also use the 'app' variable
        with app.app_context():
            print("Scheduler: Checking for overdue bills...")
            overdue_bills = Bill.query.filter(
                Bill.is_paid == False,
                Bill.due_date < datetime.now()
            ).all()
            
            for bill in overdue_bills:
                user = User.query.get(bill.user_id)
                if not user or not user.phone_number:
                    continue
                
                days_overdue = (datetime.now() - bill.due_date).days
                
                if days_overdue <= 7:
                    message = f"URGENT: Your {bill.name} payment of ₹{bill.amount} is {days_overdue} days overdue. Please pay immediately to avoid late fees."
                    
                    if bill.enable_whatsapp:
                        send_whatsapp_reminder(user.phone_number, message)

    # Add the jobs to the scheduler
    scheduler.add_job(
        func=check_and_send_reminders,
        trigger="cron",
        minute="*",
        id='reminder_checker',
        replace_existing=True
    )
    
    scheduler.add_job(
        func=check_overdue_bills,
        trigger="cron",
        hour=10,
        minute=0,
        id='overdue_checker',
        replace_existing=True
    )
    
    # Start the scheduler if it's not already running
    if not scheduler.running:
        scheduler.start()
