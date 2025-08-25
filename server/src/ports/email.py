from typing import Protocol, Optional, Dict, Any, runtime_checkable


@runtime_checkable
class EmailPort(Protocol):
    """Port for sending email messages with optional HTML content.

    This is an interface (protocol) used for dependency inversion. Concrete implementations
    include adapters like `ConsoleEmailAdapter` (logs to console) and `SendGridEmailAdapter`.
    """

    def send_email(
        self,
        to_address: str,
        subject: str,
        text_body: str,
        html_body: Optional[str] = None,
        headers: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Send an email.

        Implementations should raise an exception on failure so callers can surface errors.
        """
        ...


