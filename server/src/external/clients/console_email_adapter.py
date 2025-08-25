import logging
from typing import Optional, Dict, Any

from src.ports.email import EmailPort


logger = logging.getLogger(__name__)


class ConsoleEmailAdapter(EmailPort):
    """Simple adapter that logs email contents for development/testing."""

    def send_email(
        self,
        to_address: str,
        subject: str,
        text_body: str,
        html_body: Optional[str] = None,
        headers: Optional[Dict[str, Any]] = None,
    ) -> None:
        logger.info(
            "Sending email",
            extra={
                "to": to_address,
                "subject": subject,
                "text_body": text_body[:5000],
                "has_html": html_body is not None,
            },
        )


