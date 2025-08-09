# chatbot.py - API endpoints for chatbot functionality

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Bill, User, LoanDetails
from chatbot_models import ChatSession, ChatMessage, ChatPreferences
# We need to import the class, but not instantiate it here.
from ai_service import AIService
from datetime import datetime, timedelta
import json
import asyncio
import logging


# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

chatbot_bp = Blueprint('chatbot', __name__)

# In chatbot.py

# ... (other code) ...

@chatbot_bp.route('/chat/session', methods=['POST'])
@jwt_required()
def create_chat_session():
    """Create a new chat session"""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    logger.info(f"[CHATBOT] Creating new session for user {user_id}")
    
    try:
        # Get user preferences
        preferences = ChatPreferences.query.filter_by(user_id=user_id).first()
        ai_provider = data.get('ai_provider', preferences.preferred_ai if preferences else 'gemini')
        
        # Create new session
        session = ChatSession(
            user_id=user_id,
            ai_provider=ai_provider
        )
        
        db.session.add(session)
        db.session.commit()
        
        # Add initial system message with a supported role
        system_msg = ChatMessage(
            session_id=session.id,
            role='model', # <-- THIS IS THE CRITICAL CHANGE
            content='Chat session started. How can I help you with your bills today?'
        )
        
        db.session.add(system_msg)
        db.session.commit()
        
        logger.info(f"[CHATBOT] Session created: {session.id}")
        
        return jsonify({
            'session_id': session.id,
            'ai_provider': ai_provider,
            'message': 'Chat session created successfully'
        }), 201
        
    except Exception as e:
        logger.error(f"[CHATBOT ERROR] Failed to create session: {str(e)}")
        db.session.rollback()
        return jsonify({'message': 'Failed to create chat session', 'error': str(e)}), 500

# ... (rest of the file) ...

# In chatbot.py

@chatbot_bp.route('/chat/message', methods=['POST'])
@jwt_required()
def send_message():
    """Send a message to the chatbot and get response"""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    session_id = data.get('session_id')
    message_content = data.get('message')
    
    if not session_id or not message_content:
        return jsonify({'message': 'Session ID and message are required'}), 400
    
    logger.info(f"[CHATBOT] Processing message for session {session_id}")
    
    try:
        # Verify session belongs to user
        session = ChatSession.query.filter_by(
            id=session_id,
            user_id=user_id,
            is_active=True
        ).first()
        
        if not session:
            return jsonify({'message': 'Invalid or inactive session'}), 404
        
        # Save user message
        user_msg = ChatMessage(
            session_id=session_id,
            role='user',
            content=message_content
        )
        db.session.add(user_msg)
        db.session.commit()
        
        # Get conversation history
        messages = ChatMessage.query.filter_by(session_id=session_id).order_by(ChatMessage.timestamp).all()
        
        message_history = [
            {'role': msg.role, 'content': msg.content}
            for msg in messages
        ]
        
        # Get user context
        user_context = get_user_context(user_id)
        
        # Get AI response
        response_text, function_call = asyncio.run(
            get_ai_response(session.ai_provider, message_history, user_id, user_context)
        )
        
        if function_call:
            func_name = function_call.name
            
            # FIX: Convert func_args to a dictionary
            try:
                func_args = dict(function_call.args)
            except (TypeError, ValueError):
                func_args = {}
            
            # The rest of the function call remains the same
            function_response = execute_function_call({'name': func_name, 'arguments': func_args}, user_id)
            
            # Save function call details
            assistant_msg = ChatMessage(
                session_id=session_id,
                role='assistant',
                content=response_text,
                function_call=json.dumps({'name': func_name, 'args': func_args}),
                function_response=json.dumps(function_response)
            )
            
            # Generate a user-friendly response based on function results
            response_text = format_function_response(func_name, function_response, response_text)
        else:
            # Save assistant response
            assistant_msg = ChatMessage(
                session_id=session_id,
                role='assistant',
                content=response_text
            )
        
        db.session.add(assistant_msg)
        db.session.commit()
        
        logger.info(f"[CHATBOT] Response generated for session {session_id}")
        
        return jsonify({
            'response': response_text,
            'function_executed': function_call is not None,
            'function_data': {'name': func_name, 'args': func_args} if function_call else None
        }), 200
        
    except Exception as e:
        logger.error(f"[CHATBOT ERROR] Failed to process message: {str(e)}")
        db.session.rollback()
        return jsonify({'message': 'Failed to process message', 'error': str(e)}), 500

# ... (rest of the file) ...

@chatbot_bp.route('/chat/history/<session_id>', methods=['GET'])
@jwt_required()
def get_chat_history(session_id):
    """Get chat history for a session"""
    user_id = get_jwt_identity()
    
    # Verify session belongs to user
    session = ChatSession.query.filter_by(
        id=session_id,
        user_id=user_id
    ).first()
    
    if not session:
        return jsonify({'message': 'Session not found'}), 404
    
    # Get messages
    messages = ChatMessage.query.filter_by(session_id=session_id).order_by(ChatMessage.timestamp).all()
    
    history = []
    for msg in messages:
        msg_data = {
            'id': msg.id,
            'role': msg.role,
            'content': msg.content,
            'timestamp': msg.timestamp.isoformat()
        }
        
        if msg.function_call:
            msg_data['function_call'] = json.loads(msg.function_call)
        if msg.function_response:
            msg_data['function_response'] = json.loads(msg.function_response)
        
        history.append(msg_data)
    
    return jsonify({
        'session_id': session_id,
        'ai_provider': session.ai_provider,
        'messages': history
    }), 200

@chatbot_bp.route('/chat/preferences', methods=['GET', 'PUT'])
@jwt_required()
def manage_preferences():
    """Get or update chatbot preferences"""
    user_id = get_jwt_identity()
    
    if request.method == 'GET':
        preferences = ChatPreferences.query.filter_by(user_id=user_id).first()
        
        if not preferences:
            # Create default preferences
            preferences = ChatPreferences(user_id=user_id)
            db.session.add(preferences)
            db.session.commit()
        
        return jsonify({
            'preferred_ai': preferences.preferred_ai,
            'language': preferences.language,
            'enable_voice': preferences.enable_voice,
            'auto_suggestions': preferences.auto_suggestions,
            'has_gemini_key': bool(preferences.gemini_api_key),
            'has_openai_key': bool(preferences.openai_api_key)
        }), 200
    
    else:  # PUT
        data = request.get_json()
        
        preferences = ChatPreferences.query.filter_by(user_id=user_id).first()
        if not preferences:
            preferences = ChatPreferences(user_id=user_id)
            db.session.add(preferences)
        
        # Update preferences
        if 'preferred_ai' in data:
            preferences.preferred_ai = data['preferred_ai']
        if 'language' in data:
            preferences.language = data['language']
        if 'enable_voice' in data:
            preferences.enable_voice = data['enable_voice']
        if 'auto_suggestions' in data:
            preferences.auto_suggestions = data['auto_suggestions']
        
        # Handle API keys (encrypt before storing)
        if 'gemini_api_key' in data and data['gemini_api_key']:
            # Access the service instance from the app context
            preferences.gemini_api_key = current_app.ai_service.encrypt_api_key(data['gemini_api_key'])
        if 'openai_api_key' in data and data['openai_api_key']:
            # Access the service instance from the app context
            preferences.openai_api_key = current_app.ai_service.encrypt_api_key(data['openai_api_key'])
                
        preferences.updated_at = datetime.utcnow()
        db.session.commit()
        
        logger.info(f"[CHATBOT] Preferences updated for user {user_id}")
        
        return jsonify({'message': 'Preferences updated successfully'}), 200

@chatbot_bp.route('/chat/suggestions', methods=['GET'])
@jwt_required()
def get_suggestions():
    """Get suggested queries based on user's current bills"""
    user_id = get_jwt_identity()
    
    # Get user's bills
    bills = Bill.query.filter_by(user_id=user_id).all()
    
    suggestions = []
    
    # Check for overdue bills
    overdue_bills = [b for b in bills if not b.is_paid and b.due_date < datetime.now()]
    if overdue_bills:
        suggestions.append("Show me my overdue bills")
    
    # Check for upcoming bills
    upcoming_bills = [b for b in bills if not b.is_paid and b.due_date >= datetime.now()]
    if upcoming_bills:
        suggestions.append("What bills are due this week?")
    
    # Check for loans
    loans = db.session.query(Bill, LoanDetails).join(
        LoanDetails, Bill.id == LoanDetails.bill_id
    ).filter(Bill.user_id == user_id).all()
    
    if loans:
        suggestions.append("Show my loan payment progress")
    
    # General suggestions
    suggestions.extend([
        "Add a new bill reminder",
        "Show all my bills",
        "What's my total monthly expense?"
    ])
    
    return jsonify({'suggestions': suggestions[:5]}), 200  # Return top 5 suggestions

# Helper functions

async def get_ai_response(ai_provider: str, messages: list, user_id: str, context: dict) -> tuple:
    """Get response from selected AI provider"""
    preferences = ChatPreferences.query.filter_by(user_id=user_id).first()
    
    if not preferences:
        raise Exception("AI preferences not configured")
    
    if ai_provider == 'gemini':
        if not preferences.gemini_api_key:
            raise Exception("Gemini API key not configured")
        
        # Access the service instance from the app context
        api_key = current_app.ai_service.decrypt_api_key(preferences.gemini_api_key)
        return await current_app.ai_service.chat_with_gemini(messages, api_key, context)
    
    elif ai_provider == 'openai':
        if not preferences.openai_api_key:
            raise Exception("OpenAI API key not configured")

        # Access the service instance from the app context
        api_key = current_app.ai_service.decrypt_api_key(preferences.openai_api_key)
        return await current_app.ai_service.chat_with_openai(messages, api_key, context)
    
    else:
        raise Exception(f"Unknown AI provider: {ai_provider}")

def get_user_context(user_id: str) -> dict:
    """Get user's current data context for AI"""
    context = {}
    
    # Get bills
    bills = Bill.query.filter_by(user_id=user_id).all()
    context['total_bills'] = len(bills)
    context['unpaid_bills'] = len([b for b in bills if not b.is_paid])
    
    # Get upcoming payments
    upcoming = Bill.query.filter(
        Bill.user_id == user_id,
        Bill.is_paid == False,
        Bill.due_date <= datetime.now() + timedelta(days=7)
    ).all()
    
    context['upcoming_payments'] = [
        {
            'name': b.name,
            'amount': b.amount,
            'due_date': b.due_date.strftime('%Y-%m-%d')
        }
        for b in upcoming
    ]
    
    # Get loan summary
    loans = db.session.query(Bill, LoanDetails).join(
        LoanDetails, Bill.id == LoanDetails.bill_id
    ).filter(Bill.user_id == user_id, LoanDetails.is_active == True).all()
    
    if loans:
        context['active_loans'] = len(loans)
        context['total_debt'] = sum(loan.amount_remaining for _, loan in loans)
    
    return context

def execute_function_call(function_call: dict, user_id: str) -> dict:
    """Execute the function requested by AI"""
    func_name = function_call['name']
    args = function_call.get('arguments', {})
    
    logger.info(f"[CHATBOT] Executing function: {func_name}")
    
    if func_name == 'get_user_bills':
        bills = Bill.query.filter_by(user_id=user_id).all()
        return {
            'bills': [
                {
                    'id': b.id,
                    'name': b.name,
                    'amount': b.amount,
                    'due_date': b.due_date.strftime('%Y-%m-%d'),
                    'is_paid': b.is_paid,
                    'category': b.category,
                    'frequency': b.frequency
                }
                for b in bills
            ]
        }
    
    elif func_name == 'get_upcoming_payments':
        days = args.get('days', 7)
        upcoming = Bill.query.filter(
            Bill.user_id == user_id,
            Bill.is_paid == False,
            Bill.due_date <= datetime.now() + timedelta(days=days)
        ).all()
        
        return {
            'upcoming': [
                {
                    'name': b.name,
                    'amount': b.amount,
                    'due_date': b.due_date.strftime('%Y-%m-%d'),
                    'days_until_due': (b.due_date.date() - datetime.now().date()).days
                }
                for b in upcoming
            ]
        }
    
    elif func_name == 'get_loan_summary':
        loans = db.session.query(Bill, LoanDetails).join(
            LoanDetails, Bill.id == LoanDetails.bill_id
        ).filter(Bill.user_id == user_id).all()
        
        active_loans = []
        total_debt = 0
        
        for bill, loan in loans:
            if loan.is_active:
                active_loans.append({
                    'bill_name': bill.name,
                    'total_amount': loan.total_amount,
                    'amount_remaining': loan.amount_remaining,
                    'installments_paid': loan.installments_paid,
                    'total_installments': loan.total_installments,
                    'progress_percentage': round((loan.installments_paid / loan.total_installments) * 100, 2)
                })
                total_debt += loan.amount_remaining
        
        return {
            'active_loans': active_loans,
            'total_debt': total_debt,
            'total_loans': len(active_loans)
        }
    
    elif func_name == 'create_bill':
        # This would need more validation in production
        if not args:
            return {'error': 'Bill details required'}
        
        try:
            bill = Bill(
                user_id=user_id,
                name=args['name'],
                amount=args['amount'],
                due_date=datetime.strptime(args['due_date'], '%Y-%m-%d'),
                category=args['category'],
                frequency=args['frequency'],
                notes='Created via chatbot'
            )
            db.session.add(bill)
            db.session.commit()
            
            return {
                'success': True,
                'bill_id': bill.id,
                'message': f"Bill '{args['name']}' created successfully"
            }
        except Exception as e:
            return {'error': str(e)}
    
    elif func_name == 'get_bill_details':
        bill_id = args.get('bill_id')
        if not bill_id:
            return {'error': 'Bill ID required'}
        
        bill = Bill.query.filter_by(id=bill_id, user_id=user_id).first()
        if not bill:
            return {'error': 'Bill not found'}
        
        # Check for loan details
        loan = LoanDetails.query.filter_by(bill_id=bill_id).first()
        
        result = {
            'id': bill.id,
            'name': bill.name,
            'amount': bill.amount,
            'due_date': bill.due_date.strftime('%Y-%m-%d'),
            'category': bill.category,
            'frequency': bill.frequency,
            'is_paid': bill.is_paid,
            'notes': bill.notes
        }
        
        if loan:
            result['loan_details'] = {
                'total_amount': loan.total_amount,
                'monthly_payment': loan.monthly_payment,
                'installments_paid': loan.installments_paid,
                'total_installments': loan.total_installments,
                'amount_remaining': loan.amount_remaining
            }
        
        return result
    
    else:
        return {'error': f'Unknown function: {func_name}'}

def format_function_response(func_name: str, response: dict, ai_text: str) -> str:
    """Format function response for user-friendly display"""
    
    if 'error' in response:
        return f"I encountered an error: {response['error']}"
    
    if func_name == 'get_user_bills':
        bills = response.get('bills', [])
        if not bills:
            return "You don't have any bills set up yet. Would you like to add one?"
        
        unpaid = [b for b in bills if not b['is_paid']]
        paid = [b for b in bills if b['is_paid']]
        
        result = f"You have {len(bills)} bills in total.\n\n"
        
        if unpaid:
            result += f"📋 *Unpaid Bills ({len(unpaid)}):*\n"
            for bill in unpaid:
                result += f"• {bill['name']}: ₹{bill['amount']} due on {bill['due_date']}\n"
        
        if paid:
            result += f"\n✅ *Paid Bills ({len(paid)}):*\n"
            for bill in paid[:3]:  # Show only first 3
                result += f"• {bill['name']}: ₹{bill['amount']}\n"
        
        return result
    
    elif func_name == 'get_upcoming_payments':
        upcoming = response.get('upcoming', [])
        if not upcoming:
            return "Great! You don't have any payments due in the specified period."
        
        result = f"You have {len(upcoming)} upcoming payments:\n\n"
        total = 0
        
        for bill in upcoming:
            days = bill['days_until_due']
            if days == 0:
                when = "*TODAY*"
            elif days == 1:
                when = "tomorrow"
            else:
                when = f"in {days} days"
            
            result += f"• {bill['name']}: ₹{bill['amount']} due {when}\n"
            total += bill['amount']
        
        result += f"\n💰 Total amount due: ₹{total}"
        return result
    
    elif func_name == 'get_loan_summary':
        loans = response.get('active_loans', [])
        if not loans:
            return "You don't have any active loans or EMIs."
        
        result = f"📊 *Loan/EMI Summary:*\n\n"
        
        for loan in loans:
            result += f"{loan['bill_name']}\n"
            result += f"• Progress: {loan['installments_paid']}/{loan['total_installments']} installments ({loan['progress_percentage']}%)\n"
            result += f"• Remaining: ₹{loan['amount_remaining']}\n\n"
        
        result += f"💳 *Total Outstanding Debt:* ₹{response['total_debt']}"
        return result
    
    elif func_name == 'create_bill':
        if response.get('success'):
            return response['message'] + "\n\nThe bill has been added to your reminders. You'll receive notifications based on your reminder settings."
        return "Failed to create the bill. Please try again."
    
    else:
        # Default formatting
        return ai_text if ai_text else json.dumps(response, indent=2)