import pytest
import json
import os
from unittest.mock import patch, MagicMock
from flask import Flask
from src.api import init_app
from src.services.gmail_service import GmailService, EmailResponse


@pytest.fixture
def app():
    """Create a test Flask app."""
    app = Flask(__name__)
    init_app(app)
    app.config['TESTING'] = True
    return app


@pytest.fixture
def client(app):
    """Create a test client."""
    return app.test_client()


@pytest.fixture
def mock_gmail_service():
    """Mock Gmail service for testing."""
    with patch('src.api.routes.analysis.GmailService') as mock_service:
        # Create a mock instance
        mock_instance = MagicMock()
        mock_service.return_value = mock_instance
        yield mock_instance


class TestGenerateEmailEndpoint:
    """Test cases for the generate-email endpoint."""
    
    def test_generate_email_success(self, client, mock_gmail_service):
        """Test successful email generation and sending."""
        # Mock successful email response
        mock_gmail_service.send_email.return_value = EmailResponse(
            success=True,
            message_id="test_message_id_123",
            status_code=200,
            timestamp="2024-01-01T12:00:00"
        )
        
        # Test data
        test_data = {
            "email_config": {
                "to": "test@example.com",
                "subject": "Test Hedge Fund Analysis",
                "body": "Your analysis is ready!",
                "html_body": "<h1>Analysis Complete</h1><p>Your hedge fund analysis is ready.</p>"
            }
        }
        
        # Make request
        response = client.post('/api/analysis/generate-email', 
                             data=json.dumps(test_data),
                             content_type='application/json')
        
        # Assertions
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['message'] == 'Analysis email sent successfully'
        assert 'email_response' in data
        assert data['email_response']['success'] is True
        assert data['email_response']['message_id'] == "test_message_id_123"
        
        # Verify Gmail service was called correctly
        mock_gmail_service.send_email.assert_called_once_with(
            to="test@example.com",
            subject="Test Hedge Fund Analysis",
            body="Your analysis is ready!",
            html_body="<h1>Analysis Complete</h1><p>Your hedge fund analysis is ready.</p>",
            attachments=None
        )
    
    def test_generate_email_missing_data(self, client):
        """Test email generation with missing request data."""
        response = client.post('/api/analysis/generate-email',
                             data=json.dumps({}),
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'No data provided' in data['error']
    
    def test_generate_email_missing_email_config(self, client):
        """Test email generation with missing email configuration."""
        test_data = {"some_other_field": "value"}
        
        response = client.post('/api/analysis/generate-email',
                             data=json.dumps(test_data),
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'Email configuration is required' in data['error']
    
    def test_generate_email_missing_required_fields(self, client):
        """Test email generation with missing required email fields."""
        test_data = {
            "email_config": {
                "to": "test@example.com"
                # Missing subject and body
            }
        }
        
        response = client.post('/api/analysis/generate-email',
                             data=json.dumps(test_data),
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'Missing required email field' in data['error']
    
    def test_generate_email_gmail_failure(self, client, mock_gmail_service):
        """Test email generation when Gmail service fails."""
        # Mock failed email response
        mock_gmail_service.send_email.return_value = EmailResponse(
            success=False,
            error="Gmail API error: 403 - Forbidden",
            status_code=403,
            timestamp="2024-01-01T12:00:00"
        )
        
        test_data = {
            "email_config": {
                "to": "test@example.com",
                "subject": "Test Subject",
                "body": "Test body"
            }
        }
        
        response = client.post('/api/analysis/generate-email',
                             data=json.dumps(test_data),
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'Failed to send email' in data['error']
        assert 'email_error' in data
        assert data['email_error']['success'] is False
        assert 'Gmail API error' in data['email_error']['error']
    
    def test_generate_email_invalid_json(self, client):
        """Test email generation with invalid JSON."""
        response = client.post('/api/analysis/generate-email',
                             data="invalid json",
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_generate_email_with_attachments(self, client, mock_gmail_service):
        """Test email generation with attachments."""
        mock_gmail_service.send_email.return_value = EmailResponse(
            success=True,
            message_id="test_message_id_456",
            status_code=200,
            timestamp="2024-01-01T12:00:00"
        )
        
        test_data = {
            "email_config": {
                "to": "test@example.com",
                "subject": "Analysis with Attachments",
                "body": "Please find the analysis attached.",
                "attachments": ["/path/to/analysis.pdf", "/path/to/chart.png"]
            }
        }
        
        response = client.post('/api/analysis/generate-email',
                             data=json.dumps(test_data),
                             content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        
        # Verify Gmail service was called with attachments
        mock_gmail_service.send_email.assert_called_once_with(
            to="test@example.com",
            subject="Analysis with Attachments",
            body="Please find the analysis attached.",
            html_body=None,
            attachments=["/path/to/analysis.pdf", "/path/to/chart.png"]
        )


class TestGmailServiceIntegration:
    """Test cases for Gmail service integration."""
    
    @patch.dict(os.environ, {
        'GOOGLE_CLIENT_ID': 'test-client-id',
        'GOOGLE_CLIENT_SECRET': 'test-client-secret',
        'GOOGLE_API_KEY': 'test-api-key'
    })
    def test_gmail_service_initialization(self):
        """Test Gmail service initialization with environment variables."""
        with patch('src.services.gmail_service.load_dotenv'):
            with patch('src.services.gmail_service.build') as mock_build:
                with patch('src.services.gmail_service.InstalledAppFlow') as mock_flow:
                    mock_service = MagicMock()
                    mock_build.return_value = mock_service
                    
                    # Mock the OAuth flow
                    mock_creds = MagicMock()
                    mock_flow_instance = MagicMock()
                    mock_flow_instance.run_local_server.return_value = mock_creds
                    mock_flow.from_client_secrets_file.return_value = mock_flow_instance
                    
                    # This should not raise an exception
                    service = GmailService()
                    assert service is not None
    
    def test_gmail_service_missing_credentials(self):
        """Test Gmail service with missing environment credentials."""
        with patch.dict(os.environ, {}, clear=True):
            with patch('src.services.gmail_service.load_dotenv'):
                with patch('src.services.gmail_service.build') as mock_build:
                    # Should handle missing credentials gracefully
                    service = GmailService()
                    assert service is not None
                    # Service should be created but not authenticated
                    assert service.service is None


if __name__ == "__main__":
    pytest.main([__file__]) 