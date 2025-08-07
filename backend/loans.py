# loans.py - Create this new file in your backend folder

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Bill, LoanDetails
from datetime import datetime
from dateutil.relativedelta import relativedelta
import json
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

loans_bp = Blueprint('loans', __name__)

@loans_bp.route('/bills/<bill_id>/loan', methods=['POST'])
@jwt_required()
def create_loan_details(bill_id):
    """Create loan details for a bill"""
    user_id = get_jwt_identity()
    logger.info(f"[CREATE LOAN] Request from user {user_id} for bill {bill_id}")
    
    # Verify bill ownership
    bill = Bill.query.filter_by(id=bill_id, user_id=user_id).first()
    if not bill:
        logger.warning(f"[CREATE LOAN] Bill {bill_id} not found for user {user_id}")
        return jsonify({'message': 'Bill not found'}), 404
    
    # Check if loan details already exist
    existing_loan = LoanDetails.query.filter_by(bill_id=bill_id).first()
    if existing_loan:
        logger.warning(f"[CREATE LOAN] Loan details already exist for bill {bill_id}")
        return jsonify({'message': 'Loan details already exist for this bill'}), 400
    
    data = request.get_json()
    logger.debug(f"[CREATE LOAN] Request data: {data}")
    
    # Validate required fields
    required = ['total_amount', 'monthly_payment', 'total_installments']
    missing = [field for field in required if field not in data or not data[field]]
    if missing:
        logger.warning(f"[CREATE LOAN] Missing required fields: {missing}")
        return jsonify({'message': f'Missing required fields: {", ".join(missing)}'}), 400
    
    try:
        # Parse loan start date
        loan_start_date = datetime.now()
        if 'loan_start_date' in data and data['loan_start_date']:
            loan_start_date = datetime.fromisoformat(data['loan_start_date'].replace('Z', '+00:00'))
        
        # Create loan details
        loan = LoanDetails(
            bill_id=bill_id,
            total_amount=float(data['total_amount']),
            monthly_payment=float(data['monthly_payment']),
            interest_rate=float(data.get('interest_rate', 0)),
            total_installments=int(data['total_installments']),
            installments_paid=int(data.get('installments_paid', 0)),
            total_paid=float(data.get('total_paid', 0)),
            loan_start_date=loan_start_date,
            notes=data.get('notes')
        )
        
        # Calculate derived fields
        loan.calculate_loan_details()
        
        # Update bill amount to monthly payment and set frequency to monthly
        bill.amount = loan.monthly_payment
        bill.frequency = 'monthly'
        
        db.session.add(loan)
        db.session.commit()
        
        logger.info(f"[CREATE LOAN] Successfully created loan details for bill {bill_id}")
        
        return jsonify({
            'id': loan.id,
            'bill_id': loan.bill_id,
            'total_amount': loan.total_amount,
            'monthly_payment': loan.monthly_payment,
            'interest_rate': loan.interest_rate,
            'total_installments': loan.total_installments,
            'installments_paid': loan.installments_paid,
            'total_paid': loan.total_paid,
            'amount_remaining': loan.amount_remaining,
            'loan_start_date': loan.loan_start_date.isoformat(),
            'expected_completion_date': loan.expected_completion_date.isoformat() if loan.expected_completion_date else None,
            'next_payment_date': loan.next_payment_date.isoformat() if loan.next_payment_date else None,
            'is_active': loan.is_active
        }), 201
        
    except Exception as e:
        logger.error(f"[CREATE LOAN ERROR] Failed to create loan details: {str(e)}", exc_info=True)
        db.session.rollback()
        return jsonify({'message': 'Failed to create loan details', 'error': str(e)}), 500

@loans_bp.route('/bills/<bill_id>/loan', methods=['GET'])
@jwt_required()
def get_loan_details(bill_id):
    """Get loan details for a bill"""
    user_id = get_jwt_identity()
    logger.info(f"[GET LOAN] Request from user {user_id} for bill {bill_id}")
    
    # Verify bill ownership
    bill = Bill.query.filter_by(id=bill_id, user_id=user_id).first()
    if not bill:
        logger.warning(f"[GET LOAN] Bill {bill_id} not found for user {user_id}")
        return jsonify({'message': 'Bill not found'}), 404
    
    loan = LoanDetails.query.filter_by(bill_id=bill_id).first()
    if not loan:
        logger.info(f"[GET LOAN] No loan details found for bill {bill_id}")
        return jsonify({'message': 'No loan details found for this bill'}), 404
    
    # Parse payment history
    payment_history = []
    if loan.payment_history:
        try:
            payment_history = json.loads(loan.payment_history)
        except:
            pass
    
    return jsonify({
        'id': loan.id,
        'bill_id': loan.bill_id,
        'total_amount': loan.total_amount,
        'monthly_payment': loan.monthly_payment,
        'interest_rate': loan.interest_rate,
        'total_installments': loan.total_installments,
        'installments_paid': loan.installments_paid,
        'installments_remaining': loan.total_installments - loan.installments_paid,
        'total_paid': loan.total_paid,
        'amount_remaining': loan.amount_remaining,
        'loan_start_date': loan.loan_start_date.isoformat() if loan.loan_start_date else None,
        'expected_completion_date': loan.expected_completion_date.isoformat() if loan.expected_completion_date else None,
        'next_payment_date': loan.next_payment_date.isoformat() if loan.next_payment_date else None,
        'last_payment_date': loan.last_payment_date.isoformat() if loan.last_payment_date else None,
        'payment_history': payment_history,
        'is_active': loan.is_active,
        'progress_percentage': round((loan.installments_paid / loan.total_installments) * 100, 2) if loan.total_installments > 0 else 0
    }), 200

@loans_bp.route('/bills/<bill_id>/loan/payment', methods=['POST'])
@jwt_required()
def record_loan_payment(bill_id):
    """Record a payment for a loan"""
    user_id = get_jwt_identity()
    logger.info(f"[LOAN PAYMENT] Request from user {user_id} for bill {bill_id}")
    
    # Verify bill ownership
    bill = Bill.query.filter_by(id=bill_id, user_id=user_id).first()
    if not bill:
        logger.warning(f"[LOAN PAYMENT] Bill {bill_id} not found for user {user_id}")
        return jsonify({'message': 'Bill not found'}), 404
    
    loan = LoanDetails.query.filter_by(bill_id=bill_id).first()
    if not loan:
        logger.warning(f"[LOAN PAYMENT] No loan details found for bill {bill_id}")
        return jsonify({'message': 'No loan details found for this bill'}), 404
    
    if not loan.is_active:
        logger.info(f"[LOAN PAYMENT] Loan for bill {bill_id} is already completed")
        return jsonify({'message': 'This loan is already completed'}), 400
    
    data = request.get_json()
    payment_amount = data.get('amount') if data else None
    
    try:
        # Record the payment
        result = loan.make_payment(payment_amount)
        
        # Mark the bill as paid for this period
        bill.is_paid = True
        
        # If loan is not completed, create next month's bill
        if loan.is_active and bill.frequency == 'monthly':
            next_due_date = bill.due_date + relativedelta(months=1)
            
            # Check if next bill already exists
            next_bill = Bill.query.filter_by(
                user_id=user_id,
                name=bill.name,
                due_date=next_due_date
            ).first()
            
            if not next_bill:
                # Create next month's bill
                next_bill = Bill(
                    user_id=user_id,
                    name=bill.name,
                    amount=loan.monthly_payment,
                    due_date=next_due_date,
                    category=bill.category,
                    frequency=bill.frequency,
                    notes=f"EMI #{loan.installments_paid + 1} of {loan.total_installments}",
                    enable_whatsapp=bill.enable_whatsapp,
                    enable_call=bill.enable_call,
                    enable_sms=bill.enable_sms,
                    enable_local_notification=bill.enable_local_notification
                )
                db.session.add(next_bill)
                logger.info(f"[LOAN PAYMENT] Created next month's bill for loan {loan.id}")
        
        db.session.commit()
        
        logger.info(f"[LOAN PAYMENT] Successfully recorded payment for loan {loan.id}")
        
        return jsonify({
            'message': 'Payment recorded successfully',
            'payment_details': result,
            'loan_status': {
                'installments_paid': loan.installments_paid,
                'installments_remaining': loan.total_installments - loan.installments_paid,
                'amount_remaining': loan.amount_remaining,
                'is_completed': not loan.is_active,
                'next_payment_date': loan.next_payment_date.isoformat() if loan.next_payment_date else None
            }
        }), 200
        
    except Exception as e:
        logger.error(f"[LOAN PAYMENT ERROR] Failed to record payment: {str(e)}", exc_info=True)
        db.session.rollback()
        return jsonify({'message': 'Failed to record payment', 'error': str(e)}), 500

@loans_bp.route('/bills/<bill_id>/loan', methods=['PUT'])
@jwt_required()
def update_loan_details(bill_id):
    """Update loan details"""
    user_id = get_jwt_identity()
    logger.info(f"[UPDATE LOAN] Request from user {user_id} for bill {bill_id}")
    
    # Verify bill ownership
    bill = Bill.query.filter_by(id=bill_id, user_id=user_id).first()
    if not bill:
        return jsonify({'message': 'Bill not found'}), 404
    
    loan = LoanDetails.query.filter_by(bill_id=bill_id).first()
    if not loan:
        return jsonify({'message': 'No loan details found for this bill'}), 404
    
    data = request.get_json()
    logger.debug(f"[UPDATE LOAN] Update data: {data}")
    
    try:
        # Update fields if provided
        if 'monthly_payment' in data:
            loan.monthly_payment = float(data['monthly_payment'])
            bill.amount = loan.monthly_payment  # Update bill amount
        
        if 'interest_rate' in data:
            loan.interest_rate = float(data['interest_rate'])
        
        if 'notes' in data:
            loan.notes = data['notes']
        
        # Recalculate loan details
        loan.calculate_loan_details()
        loan.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        logger.info(f"[UPDATE LOAN] Successfully updated loan details for bill {bill_id}")
        
        return jsonify({'message': 'Loan details updated successfully'}), 200
        
    except Exception as e:
        logger.error(f"[UPDATE LOAN ERROR] Failed to update loan details: {str(e)}", exc_info=True)
        db.session.rollback()
        return jsonify({'message': 'Failed to update loan details', 'error': str(e)}), 500

@loans_bp.route('/loans/summary', methods=['GET'])
@jwt_required()
def get_loans_summary():
    """Get summary of all loans for the user"""
    user_id = get_jwt_identity()
    logger.info(f"[LOANS SUMMARY] Request from user {user_id}")
    
    # Get all bills with loan details for the user
    bills_with_loans = db.session.query(Bill, LoanDetails).join(
        LoanDetails, Bill.id == LoanDetails.bill_id
    ).filter(Bill.user_id == user_id).all()
    
    active_loans = []
    completed_loans = []
    total_debt = 0
    total_monthly_payment = 0
    
    for bill, loan in bills_with_loans:
        loan_data = {
            'bill_name': bill.name,
            'bill_id': bill.id,
            'loan_id': loan.id,
            'total_amount': loan.total_amount,
            'monthly_payment': loan.monthly_payment,
            'installments_paid': loan.installments_paid,
            'total_installments': loan.total_installments,
            'amount_remaining': loan.amount_remaining,
            'progress_percentage': round((loan.installments_paid / loan.total_installments) * 100, 2) if loan.total_installments > 0 else 0,
            'next_payment_date': loan.next_payment_date.isoformat() if loan.next_payment_date else None
        }
        
        if loan.is_active:
            active_loans.append(loan_data)
            total_debt += loan.amount_remaining
            total_monthly_payment += loan.monthly_payment
        else:
            completed_loans.append(loan_data)
    
    return jsonify({
        'active_loans': active_loans,
        'completed_loans': completed_loans,
        'summary': {
            'total_active_loans': len(active_loans),
            'total_completed_loans': len(completed_loans),
            'total_debt': total_debt,
            'total_monthly_payment': total_monthly_payment
        
