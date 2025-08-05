from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from local_storage_service import (
    upload_receipt_to_local, 
    get_receipt_path, 
    get_receipt_url,
    delete_receipt_from_local
)
from models import db, Bill
import json
import os

receipts_bp = Blueprint('receipts', __name__)

@receipts_bp.route('/scan-receipt', methods=['POST'])
@jwt_required()
def scan_receipt():
    """Upload and process receipt using local storage"""
    user_id = get_jwt_identity()
    
    if 'receipt' not in request.files:
        return jsonify({'message': 'No receipt file provided'}), 400
    
    file = request.files['receipt']
    if file.filename == '':
        return jsonify({'message': 'No file selected'}), 400
    
    # Upload to local storage
    result = upload_receipt_to_local(file, user_id)
    
    if not result['success']:
        return jsonify({'message': 'Failed to upload receipt', 'error': result.get('error')}), 500
    
    # Mock OCR processing (in real app, you'd use Tesseract OCR or similar)
    # For now, return a sample bill structure
    mock_bill_data = {
        'id': None,
        'name': 'Scanned Bill',
        'amount': 0.0,
        'due_date': None,
        'category': 'other',
        'frequency': 'once',
        'is_paid': False,
        'notes': f"Receipt uploaded: {result['filename']}",
        'receipt_url': result['url']
    }
    
    return jsonify(mock_bill_data), 200

@receipts_bp.route('/<bill_id>/receipt', methods=['POST'])
@jwt_required()
def upload_bill_receipt(bill_id):
    """Upload receipt for existing bill"""
    user_id = get_jwt_identity()
    
    # Verify bill ownership
    bill = Bill.query.filter_by(id=bill_id, user_id=user_id).first()
    if not bill:
        return jsonify({'message': 'Bill not found'}), 404
    
    if 'receipt' not in request.files:
        return jsonify({'message': 'No receipt file provided'}), 400
    
    file = request.files['receipt']
    if file.filename == '':
        return jsonify({'message': 'No file selected'}), 400
    
    # Upload to local storage
    result = upload_receipt_to_local(file, user_id)
    
    if not result['success']:
        return jsonify({'message': 'Failed to upload receipt'}), 500
    
    # Update bill notes with receipt info
    notes_data = {}
    if bill.notes:
        try:
            notes_data = json.loads(bill.notes)
        except:
            notes_data = {'original_notes': bill.notes}
    
    # Delete old receipt if exists
    old_receipt = notes_data.get('receipt_filename')
    if old_receipt:
        delete_receipt_from_local(old_receipt)
    
    notes_data['receipt_filename'] = result['filename']
    bill.notes = json.dumps(notes_data)
    
    db.session.commit()
    
    return jsonify({
        'message': 'Receipt uploaded successfully',
        'receipt_url': result['url']
    }), 200

@receipts_bp.route('/<bill_id>/receipt', methods=['GET'])
@jwt_required()
def get_bill_receipt(bill_id):
    """Get receipt URL for a bill"""
    user_id = get_jwt_identity()
    
    # Verify bill ownership
    bill = Bill.query.filter_by(id=bill_id, user_id=user_id).first()
    if not bill:
        return jsonify({'message': 'Bill not found'}), 404
    
    # Get receipt filename from notes
    try:
        notes_data = json.loads(bill.notes or '{}')
        receipt_filename = notes_data.get('receipt_filename')
        
        if not receipt_filename:
            return jsonify({'message': 'No receipt found for this bill'}), 404
        
        # Get URL
        result = get_receipt_url(receipt_filename)
        
        if result['success']:
            return jsonify({'receipt_url': result['url']}), 200
        else:
            return jsonify({'message': 'Failed to get receipt URL'}), 500
            
    except:
        return jsonify({'message': 'No receipt found for this bill'}), 404

@receipts_bp.route('/<bill_id>/receipt', methods=['DELETE'])
@jwt_required()
def delete_bill_receipt(bill_id):
    """Delete receipt for a bill"""
    user_id = get_jwt_identity()
    
    # Verify bill ownership
    bill = Bill.query.filter_by(id=bill_id, user_id=user_id).first()
    if not bill:
        return jsonify({'message': 'Bill not found'}), 404
    
    # Get receipt filename from notes
    try:
        notes_data = json.loads(bill.notes or '{}')
        receipt_filename = notes_data.get('receipt_filename')
        
        if not receipt_filename:
            return jsonify({'message': 'No receipt found for this bill'}), 404
        
        # Delete file
        result = delete_receipt_from_local(receipt_filename)
        
        if result['success']:
            # Update bill notes
            del notes_data['receipt_filename']
            bill.notes = json.dumps(notes_data) if notes_data else None
            db.session.commit()
            
            return jsonify({'message': 'Receipt deleted successfully'}), 200
        else:
            return jsonify({'message': 'Failed to delete receipt'}), 500
            
    except:
        return jsonify({'message': 'Error processing request'}), 500

@receipts_bp.route('/view/<user_id>/<filename>', methods=['GET'])
@jwt_required()
def view_receipt(user_id, filename):
    """Serve receipt file"""
    current_user_id = get_jwt_identity()
    
    # Security check - users can only view their own receipts
    if current_user_id != user_id:
        return jsonify({'message': 'Unauthorized'}), 403
    
    # Get file path
    result = get_receipt_path(f"{user_id}/{filename}")
    
    if result['success']:
        file_path = result['path']
        # Determine file type
        file_extension = filename.rsplit('.', 1)[1].lower()
        
        if file_extension in ['jpg', 'jpeg']:
            mimetype = 'image/jpeg'
        elif file_extension == 'png':
            mimetype = 'image/png'
        elif file_extension == 'pdf':
            mimetype = 'application/pdf'
        else:
            mimetype = 'application/octet-stream'
        
        return send_file(file_path, mimetype=mimetype)
    else:
        return jsonify({'message': 'File not found'}), 404