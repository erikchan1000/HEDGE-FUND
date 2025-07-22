from typing import Dict, Any, List, Optional
import logging
import base64
import os
from datetime import datetime
from dataclasses import dataclass
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import json

from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google.api_core import exceptions as google_exceptions
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow

logger = logging.getLogger(__name__)

@dataclass
class EmailMessage:
    """Data class for email message details."""
    to: str
    subject: str
    body: str
    html_body: Optional[str] = None
    attachments: Optional[List[str]] = None
    message_id: Optional[str] = None
    status: Optional[str] = None
    created_at: Optional[str] = None

@dataclass
class EmailResponse:
    """Data class for Gmail API response."""
    success: bool
    message_id: Optional[str] = None
    error: Optional[str] = None
    status_code: Optional[int] = None
    timestamp: Optional[str] = None

class GmailService:
    """Service for handling Google Gmail API interactions."""
    
    # Gmail API scopes
    SCOPES = ['https://www.googleapis.com/auth/gmail.send']
    
    def __init__(self, credentials_path: Optional[str] = None):
        self.credentials_path = credentials_path
        self.service = None
        self._authenticate()
    
    def _authenticate(self) -> None:
        """Authenticate with Gmail API using OAuth2."""
        try:
            creds = None
            
            # First try to load from credentials file
            if self.credentials_path and os.path.exists(self.credentials_path):
                try:
                    with open(self.credentials_path, 'r') as token:
                        creds = Credentials.from_authorized_user_info(
                            json.load(token), self.SCOPES
                        )
                except Exception as e:
                    logger.warning(f"Could not load credentials from file: {e}")
            
            # If no valid credentials available, create them
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    # Create credentials using OAuth2 flow
                    creds = self._create_credentials_with_oauth2()
                
                # Save the credentials for the next run
                if self.credentials_path and creds:
                    try:
                        with open(self.credentials_path, 'w') as token:
                            token.write(creds.to_json())
                    except Exception as e:
                        logger.warning(f"Could not save credentials: {e}")
            
            # Build the Gmail service
            if creds:
                self.service = build('gmail', 'v1', credentials=creds)
                logger.info("Gmail service authenticated successfully")
            else:
                logger.error("No valid credentials available")
            
        except Exception as e:
            logger.error(f"Error authenticating with Gmail API: {str(e)}")
            raise
    
    def _create_credentials_with_oauth2(self):
        """Create credentials using OAuth2 flow."""
        try:
            # Load environment variables
            load_dotenv()
            
            # Get credentials from environment variables
            client_id = os.getenv('GOOGLE_CLIENT_ID')
            client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
            
            if not client_id or not client_secret:
                logger.error("GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET must be set in environment variables")
                return None
            
            # Create client configuration
            client_config = {
                "web": {
                    "client_id": client_id,
                    "project_id": "hedge-fund-466705",
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                    "client_secret": client_secret,
                    "redirect_uris": ["http://localhost:5000"]
                }
            }
            
            # Create a temporary file for the OAuth flow
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                json.dump(client_config, f)
                temp_file_path = f.name
            
            try:
                # Run OAuth2 flow using the temporary file
                flow = InstalledAppFlow.from_client_secrets_file(temp_file_path, self.SCOPES)
                creds = flow.run_local_server(port=0)
                
                logger.info("OAuth2 authentication completed successfully")
                return creds
            finally:
                # Clean up the temporary file
                try:
                    os.unlink(temp_file_path)
                except Exception as e:
                    logger.warning(f"Could not delete temporary file {temp_file_path}: {e}")
            
        except Exception as e:
            logger.error(f"Error creating credentials with OAuth2: {e}")
            return None
    
    def send_email(self, to: str, subject: str, body: str, html_body: Optional[str] = None, 
                   attachments: Optional[List[str]] = None) -> EmailResponse:
        """
        Send an email using Gmail API.
        
        Args:
            to: Recipient email address
            subject: Email subject
            body: Plain text email body
            html_body: HTML email body (optional)
            attachments: List of file paths to attach (optional)
            
        Returns:
            EmailResponse with success status and message details
        """
        try:
            if not self.service:
                raise ValueError("Gmail service not authenticated")
            
            # Validate inputs
            if not to or not subject or not body:
                raise ValueError("to, subject, and body are required")
            
            # Create message
            message = self._create_message(to, subject, body, html_body, attachments)
            
            # Send message
            sent_message = self.service.users().messages().send(
                userId='me', body=message
            ).execute()
            
            return EmailResponse(
                success=True,
                message_id=sent_message['id'],
                status_code=200,
                timestamp=datetime.now().isoformat()
            )
            
        except google_exceptions.HttpError as e:
            error_msg = f"Gmail API error: {e.code} - {e.message}"
            logger.error(error_msg)
            return EmailResponse(
                success=False,
                error=error_msg,
                status_code=e.code,
                timestamp=datetime.now().isoformat()
            )
            
        except Exception as e:
            error_msg = f"Error sending email: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return EmailResponse(
                success=False,
                error=error_msg,
                timestamp=datetime.now().isoformat()
            )
    
    def _create_message(self, to: str, subject: str, body: str, html_body: Optional[str] = None,
                       attachments: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Create a Gmail API message object.
        
        Args:
            to: Recipient email address
            subject: Email subject
            body: Plain text email body
            html_body: HTML email body (optional)
            attachments: List of file paths to attach (optional)
            
        Returns:
            Gmail API message object
        """
        message = MIMEMultipart('alternative')
        message['to'] = to
        message['subject'] = subject
        
        # Add plain text part
        text_part = MIMEText(body, 'plain')
        message.attach(text_part)
        
        # Add HTML part if provided
        if html_body:
            html_part = MIMEText(html_body, 'html')
            message.attach(html_part)
        
        # Add attachments if provided
        if attachments:
            for attachment_path in attachments:
                if os.path.exists(attachment_path):
                    with open(attachment_path, 'rb') as f:
                        part = MIMEBase('application', 'octet-stream')
                        part.set_payload(f.read())
                    
                    encoders.encode_base64(part)
                    part.add_header(
                        'Content-Disposition',
                        f'attachment; filename= {os.path.basename(attachment_path)}'
                    )
                    message.attach(part)
        
        # Encode the message
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        return {'raw': raw_message}
    
    def get_email_status(self, message_id: str) -> EmailResponse:
        """
        Get the status of a sent email.
        
        Args:
            message_id: The message ID returned from send_email
            
        Returns:
            EmailResponse with status information
        """
        try:
            if not self.service:
                raise ValueError("Gmail service not authenticated")
            
            message = self.service.users().messages().get(
                userId='me', id=message_id
            ).execute()
            
            return EmailResponse(
                success=True,
                message_id=message_id,
                status_code=200,
                timestamp=datetime.now().isoformat()
            )
            
        except google_exceptions.HttpError as e:
            error_msg = f"Failed to get email status: {e.code} - {e.message}"
            logger.error(error_msg)
            return EmailResponse(
                success=False,
                error=error_msg,
                status_code=e.code,
                timestamp=datetime.now().isoformat()
            )
            
        except Exception as e:
            error_msg = f"Error getting email status: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return EmailResponse(
                success=False,
                error=error_msg,
                timestamp=datetime.now().isoformat()
            )
    
    def send_bulk_email(self, messages: List[EmailMessage]) -> List[EmailResponse]:
        """
        Send multiple emails in bulk.
        
        Args:
            messages: List of EmailMessage objects to send
            
        Returns:
            List of EmailResponse objects for each message
        """
        responses = []
        
        for message in messages:
            response = self.send_email(
                to=message.to,
                subject=message.subject,
                body=message.body,
                html_body=message.html_body,
                attachments=message.attachments
            )
            responses.append(response)
            
            # Add small delay to avoid rate limiting
            import time
            time.sleep(0.1)
        
        return responses
    
    def _validate_email(self, email: str) -> None:
        """
        Validate email address format.
        
        Args:
            email: Email address to validate
            
        Raises:
            ValueError: If email format is invalid
        """
        import re
        
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if not re.match(pattern, email):
            raise ValueError(f"Invalid email format: {email}")
    
    def configure_credentials(self, credentials_path: str) -> None:
        """
        Configure the Gmail service with credentials file path.
        
        Args:
            credentials_path: Path to the credentials JSON file
        """
        self.credentials_path = credentials_path
        self._authenticate()
        logger.info("Gmail service configured with credentials") 