import pytest

from src.external.clients.sendgrid_email_adapter import SendGridEmailAdapter


def test_sendgrid_adapter_uses_injected_client_without_imports():
    class FakeClient:
        def __init__(self):
            self.sent = []

        def send(self, payload):
            self.sent.append(payload)

    fake = FakeClient()
    adapter = SendGridEmailAdapter(api_key="x", from_address="no-reply@example.com", client=fake)

    adapter.send_email(
        to_address="user@example.com",
        subject="Subject",
        text_body="Hello",
        html_body="<p>Hello</p>",
        headers={"X-Test": "1"}
    )

    assert fake.sent and fake.sent[0]["to"] == "user@example.com"
    assert fake.sent[0]["from"] == "no-reply@example.com"
    assert fake.sent[0]["headers"]["X-Test"] == "1"


def test_sendgrid_adapter_requires_from_address_when_client_injected():
    class Dummy:
        def send(self, p):
            pass

    adapter = SendGridEmailAdapter(api_key="x", client=Dummy())
    with pytest.raises(ValueError):
        adapter.send_email("u@example.com", "s", "t")


