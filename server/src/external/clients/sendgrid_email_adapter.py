import os
from typing import Optional, Dict, Any

from src.ports.email import EmailPort


class SendGridEmailAdapter(EmailPort):
    """SendGrid implementation of EmailPort.

    This adapter supports injecting a custom client for testing to avoid importing
    the sendgrid library in test environments.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        from_address: Optional[str] = None,
        client: Optional[object] = None,
    ) -> None:
        self._api_key = api_key or os.getenv("SENDGRID_API_KEY")
        self._from_address = from_address or os.getenv("EMAIL_FROM")
        self._client = client  # If provided, used directly and no sendgrid import occurs

    def send_email(
        self,
        to_address: str,
        subject: str,
        text_body: str,
        html_body: Optional[str] = None,
        headers: Optional[Dict[str, Any]] = None,
    ) -> None:
        if not self._from_address:
            raise ValueError("EMAIL_FROM must be provided via constructor or EMAIL_FROM env var")

        if self._client is not None:
            # Testing path: delegate to injected client
            payload = {
                "from": self._from_address,
                "to": to_address,
                "subject": subject,
                "text": text_body,
                "html": html_body,
                "headers": headers or {},
            }
            self._client.send(payload)
            return

        # Runtime path: import sendgrid lazily to avoid test dependency
        if not self._api_key:
            raise ValueError("SENDGRID_API_KEY must be provided via constructor or environment")

        from sendgrid import SendGridAPIClient
        from sendgrid.helpers.mail import Mail

        message = Mail(
            from_email=self._from_address,
            to_emails=to_address,
            subject=subject,
            plain_text_content=text_body,
            html_content=html_body,
        )

        if headers:
            # sendgrid Mail supports custom headers via .headers dict
            message.headers = headers

        client = SendGridAPIClient(self._api_key)
        client.send(message)


