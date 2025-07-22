from flask import Blueprint, Response, stream_with_context, request, jsonify
import json
import sys
import os
from datetime import datetime
import time
from src.controllers.analysis_controller import AnalysisController
from src.services.gmail_service import GmailService
from src.models.dto.requests import EmailRequestDTO
from src.models.dto.responses import EmailResponseDTO
import logging

logger = logging.getLogger(__name__)

analysis_bp = Blueprint('analysis', __name__, url_prefix='/api/analysis')

analysis_controller = AnalysisController()

@analysis_bp.route('/generate', methods=['POST'])
def generate_analysis():
    """Generate hedge fund analysis based on provided parameters."""
    return analysis_controller.generate_analysis()

@analysis_bp.route('/generate-email', methods=['POST'])
def generate_analysis_email():
    """Generate hedge fund analysis and send results via email."""
    try:
        # Handle JSON parsing errors
        try:
            data = request.get_json()
        except Exception as e:
            return jsonify({'error': 'Invalid JSON format'}), 400
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Extract email configuration from request
        email_config = data.get('email_config', {})
        if not email_config:
            return jsonify({'error': 'Email configuration is required'}), 400
        
        # Validate email configuration
        required_email_fields = ['to', 'subject', 'body']
        for field in required_email_fields:
            if field not in email_config or not email_config[field]:
                return jsonify({'error': f'Missing required email field: {field}'}), 400
        
        # Initialize Gmail service
        credentials_path = os.getenv('GOOGLE_CREDENTIALS_PATH')
        gmail_service = GmailService(credentials_path=credentials_path)
        
        # Create email request DTO
        try:
            email_request_dto = EmailRequestDTO.from_dict(email_config)
        except Exception as e:
            return jsonify({'error': f'Invalid email configuration format: {str(e)}'}), 400
        
        # Send email with attachments
        email_response = gmail_service.send_email(
            to=email_request_dto.to,
            subject=email_request_dto.subject,
            body=email_request_dto.body,
            html_body=email_request_dto.html_body,
            attachments=email_request_dto.attachments
        )
        
        # Create email response DTO
        email_response_dto = EmailResponseDTO(
            success=email_response.success,
            message_id=email_response.message_id,
            error=email_response.error,
            status_code=email_response.status_code
        )
        
        if not email_response.success:
            return jsonify({
                'error': 'Failed to send email',
                'email_error': email_response_dto.to_dict()
            }), 400
        
        # Return success response
        return jsonify({
            'success': True,
            'message': 'Analysis email sent successfully',
            'email_response': email_response_dto.to_dict(),
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Error in generate_analysis_email: {str(e)}", exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500
