from flask import Blueprint, request, jsonify
import os
from datetime import datetime
from src.controllers.analysis_controller import AnalysisController
from src.services.gmail_service import GmailService
from src.models.dto.requests import EmailRequestDTO
from src.models.dto.responses import EmailResponseDTO
import logging
from src.utils.cancellation import cancel_request, get_cancellation_manager
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

@analysis_bp.route('/cancel/<request_id>', methods=['POST'])
def cancel_analysis(request_id: str):
    """Cancel an ongoing analysis request."""
    try:
        success = cancel_request(request_id)
        if success:
            return jsonify({
                'message': f'Request {request_id} cancelled successfully',
                'cancelled': True
            }), 200
        else:
            return jsonify({
                'message': f'Request {request_id} not found or already completed',
                'cancelled': False
            }), 404
    except Exception as e:
        logger.error(f"Error cancelling request {request_id}: {str(e)}")
        return jsonify({
            'error': 'Failed to cancel request',
            'message': str(e)
        }), 500

@analysis_bp.route('/active', methods=['GET'])
def get_active_requests():
    """Get list of active analysis requests."""
    try:
        manager = get_cancellation_manager()
        active_requests = list(manager.get_active_request_ids())
        return jsonify({
            'active_requests': active_requests,
            'count': len(active_requests)
        }), 200
    except Exception as e:
        logger.error(f"Error getting active requests: {str(e)}")
        return jsonify({
            'error': 'Failed to get active requests',
            'message': str(e)
        }), 500

@analysis_bp.route('/cancel-all', methods=['POST'])
def cancel_all_requests():
    """Cancel all ongoing analysis requests."""
    try:
        manager = get_cancellation_manager()
        active_count = manager.get_active_request_count()
        manager.cancel_all_requests()
        return jsonify({
            'message': f'Cancelled {active_count} active requests',
            'cancelled_count': active_count
        }), 200
    except Exception as e:
        logger.error(f"Error cancelling all requests: {str(e)}")
        return jsonify({
            'error': 'Failed to cancel all requests',
            'message': str(e)
        }), 500

# MCP-compliant notification endpoint
mcp_bp = Blueprint('mcp', __name__, url_prefix='/api/mcp')

@mcp_bp.route('/notification', methods=['POST'])
def handle_mcp_notification():
    """Handle MCP notifications according to specification."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        # Validate JSON-RPC format
        if not all(key in data for key in ['jsonrpc', 'method']):
            return jsonify({'error': 'Invalid JSON-RPC format'}), 400
        
        if data['jsonrpc'] != '2.0':
            return jsonify({'error': 'Unsupported JSON-RPC version'}), 400
        
        method = data.get('method')
        params = data.get('params', {})
        
        if method == 'notifications/cancelled':
            # Handle cancellation notification according to MCP spec
            request_id = params.get('requestId')
            reason = params.get('reason', 'Client requested cancellation')
            
            if not request_id:
                return jsonify({'error': 'Missing requestId in cancellation notification'}), 400
            
            logger.info(f"Received MCP cancellation notification for request {request_id}: {reason}")
            
            # Cancel the request
            success = cancel_request(request_id)
            
            if success:
                logger.info(f"Successfully cancelled request {request_id}")
            else:
                logger.warning(f"Request {request_id} not found or already completed")
            
            # According to MCP spec, return 202 Accepted for notifications
            return '', 202
        
        else:
            logger.warning(f"Received unknown MCP notification method: {method}")
            return jsonify({'error': f'Unknown notification method: {method}'}), 400
    
    except Exception as e:
        logger.error(f"Error handling MCP notification: {str(e)}")
        return jsonify({'error': 'Failed to process MCP notification', 'message': str(e)}), 500
