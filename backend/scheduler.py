# scheduler.py

from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
from models import db, Bill, User, ReminderSettings
from reminder_service import generate_reminder_message, send_whatsapp_reminder, send_voice_reminder
import pytz
import logging

# We will not import 'app' in this file at all to avoid circular imports.

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()

def start_scheduler(app):
    """
    Initializes and starts the background scheduler.
    The job functions are defined inside so they have access to the 'app' context
    without causing circular import errors.
    """
    logger.info("=== SCHEDULER START: Initializing scheduler ===")

    def check_and_send_reminders():
        """This job runs every minute to check for upcoming reminders."""
        # This function can now use the 'app' variable from the outer scope
        with app.app_context():
            current_time = datetime.now().strftime('%H:%M')
            logger.info(f"[REMINDER CHECK] Starting reminder check at {current_time}")
            print("Scheduler: Checking for due bills...")
            
            # This loop runs every minute
            
            users = User.query.filter(User.phone_number.isnot(None)).all()
            logger.info(f"[REMINDER CHECK] Found {len(users)} users with phone numbers")
            
            for user in users:
                logger.debug(f"[USER CHECK] Processing user: {user.id} - {user.name}")
                
                settings = ReminderSettings.query.filter_by(user_id=user.id).first()
                if not settings:
                    logger.warning(f"[USER CHECK] No reminder settings found for user {user.id}")
                    continue

                logger.debug(f"[USER CHECK] User {user.id} preferred time: {settings.preferred_time}")
                logger.debug(f"[USER CHECK] WhatsApp enabled: {settings.whatsapp_enabled}, Call enabled: {settings.call_enabled}")

                # The key change is here: The reminder logic is now executed ONLY
                # at the exact minute of the user's preferred time.
                if current_time == settings.preferred_time:
                    logger.info(f"[TIME MATCH] Current time {current_time} matches user {user.id} preferred time")
                    
                    bills_due = Bill.query.filter(
                        Bill.user_id == user.id,
                        Bill.is_paid == False
                    ).all()
                    
                    logger.info(f"[BILLS CHECK] Found {len(bills_due)} unpaid bills for user {user.id}")
                    
                    for bill in bills_due:
                        logger.debug(f"[BILL PROCESS] Processing bill: {bill.id} - {bill.name}")
                        logger.debug(f"[BILL PROCESS] Bill due date: {bill.due_date}, Amount: {bill.amount}")
                        
                        # Calculate days left using only the date portion
                        current_date = datetime.now().date()
                        bill_due_date = bill.due_date.date()
                        days_left = (bill_due_date - current_date).days
                        
                        logger.debug(f"[BILL PROCESS] Days left for bill {bill.id}: {days_left} days")
                        logger.debug(f"[BILL PROCESS] Current date: {current_date}, Bill due date: {bill_due_date}")
                        
                        # Check if the number of days left is in our reminder list
                        # This will trigger a message on the 3rd, 2nd, 1st, and 0th day before the deadline.
                        if days_left in [3, 2, 1, 0]:
                            logger.info(f"[REMINDER TRIGGER] Bill {bill.id} qualifies for reminder (days_left: {days_left})")
                            
                            bill_data = {
                                'name': bill.name,
                                'amount': bill.amount,
                                'due_date': bill.due_date.strftime('%Y-%m-%d')
                            }
                            
                            logger.debug(f"[MESSAGE GEN] Generating message for bill: {bill_data}")
                            message = generate_reminder_message(user.name, bill_data)
                            logger.debug(f"[MESSAGE GEN] Generated message: {message[:50]}...")
                            
                            if settings.whatsapp_enabled and bill.enable_whatsapp:
                                logger.info(f"[WHATSAPP] Sending WhatsApp reminder to {user.phone_number} for bill {bill.id}")
                                try:
                                    send_whatsapp_reminder(user.phone_number, message)
                                    logger.info(f"[WHATSAPP] Successfully sent WhatsApp reminder for bill {bill.id}")
                                except Exception as e:
                                    logger.error(f"[WHATSAPP ERROR] Failed to send WhatsApp reminder for bill {bill.id}: {str(e)}")
                            else:
                                logger.debug(f"[WHATSAPP] Skipped - WhatsApp disabled (settings: {settings.whatsapp_enabled}, bill: {bill.enable_whatsapp})")
                            
                            if settings.call_enabled and bill.enable_call:
                                logger.info(f"[VOICE CALL] Sending voice reminder to {user.phone_number} for bill {bill.id}")
                                try:
                                    send_voice_reminder(user.phone_number, message)
                                    logger.info(f"[VOICE CALL] Successfully sent voice reminder for bill {bill.id}")
                                except Exception as e:
                                    logger.error(f"[VOICE CALL ERROR] Failed to send voice reminder for bill {bill.id}: {str(e)}")
                            else:
                                logger.debug(f"[VOICE CALL] Skipped - Voice call disabled (settings: {settings.call_enabled}, bill: {bill.enable_call})")
                        else:
                            logger.debug(f"[BILL SKIP] Bill {bill.id} not due for reminder (days_left: {days_left})")
                else:
                    logger.debug(f"[TIME SKIP] Current time {current_time} does not match user {user.id} preferred time {settings.preferred_time}")
            
            logger.info(f"[REMINDER CHECK] Completed reminder check at {datetime.now().strftime('%H:%M:%S')}")

    def check_overdue_bills():
        """This job runs daily to check for overdue bills."""
        # This function can also use the 'app' variable
        with app.app_context():
            logger.info("[OVERDUE CHECK] Starting overdue bills check")
            print("Scheduler: Checking for overdue bills...")
            
            current_datetime = datetime.now()
            overdue_bills = Bill.query.filter(
                Bill.is_paid == False,
                Bill.due_date < current_datetime
            ).all()
            
            logger.info(f"[OVERDUE CHECK] Found {len(overdue_bills)} overdue bills")
            
            for bill in overdue_bills:
                logger.debug(f"[OVERDUE PROCESS] Processing overdue bill: {bill.id} - {bill.name}")
                
                user = User.query.get(bill.user_id)
                if not user:
                    logger.warning(f"[OVERDUE PROCESS] User not found for bill {bill.id} (user_id: {bill.user_id})")
                    continue
                
                if not user.phone_number:
                    logger.warning(f"[OVERDUE PROCESS] No phone number for user {user.id}")
                    continue
                
                days_overdue = (current_datetime - bill.due_date).days
                logger.debug(f"[OVERDUE PROCESS] Bill {bill.id} is {days_overdue} days overdue")
                
                if days_overdue <= 7:
                    message = f"URGENT: Your {bill.name} payment of ₹{bill.amount} is {days_overdue} days overdue. Please pay immediately to avoid late fees."
                    logger.info(f"[OVERDUE ALERT] Sending overdue alert for bill {bill.id} ({days_overdue} days overdue)")
                    
                    if bill.enable_whatsapp:
                        logger.info(f"[OVERDUE WHATSAPP] Sending WhatsApp overdue reminder to {user.phone_number}")
                        try:
                            send_whatsapp_reminder(user.phone_number, message)
                            logger.info(f"[OVERDUE WHATSAPP] Successfully sent overdue reminder for bill {bill.id}")
                        except Exception as e:
                            logger.error(f"[OVERDUE WHATSAPP ERROR] Failed to send overdue reminder for bill {bill.id}: {str(e)}")
                    else:
                        logger.debug(f"[OVERDUE WHATSAPP] WhatsApp disabled for bill {bill.id}")
                else:
                    logger.debug(f"[OVERDUE SKIP] Bill {bill.id} is {days_overdue} days overdue (>7 days, skipping)")
            
            logger.info(f"[OVERDUE CHECK] Completed overdue bills check at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Add the jobs to the scheduler
    logger.info("[SCHEDULER CONFIG] Adding reminder_checker job (runs every minute)")
    scheduler.add_job(
        func=check_and_send_reminders,
        trigger="cron",
        minute="*",
        id='reminder_checker',
        replace_existing=True
    )
    
    logger.info("[SCHEDULER CONFIG] Adding overdue_checker job (runs daily at 10:00)")
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
        logger.info("[SCHEDULER START] Starting the scheduler")
        scheduler.start()
        logger.info("[SCHEDULER START] Scheduler started successfully")
    else:
        logger.info("[SCHEDULER START] Scheduler already running")