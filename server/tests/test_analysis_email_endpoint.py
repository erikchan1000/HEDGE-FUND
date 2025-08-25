import json
from flask import Flask
import pytest

from src.api.routes.analysis import analysis_bp, set_email_port, set_analysis_service


class FakeEmailPort:
    def __init__(self):
        self.sent = []

    def send_email(self, to_address: str, subject: str, text_body: str, html_body=None, headers=None):
        self.sent.append({
            'to': to_address,
            'subject': subject,
            'text': text_body,
            'html': html_body,
        })


class FakeAnalysisService:
    def process_analysis_request(self, request_dto):
        payload = {
            'type': 'result',
            'data': {'summary': 'ok', 'tickers': request_dto.tickers}
        }
        yield json.dumps(payload)


@pytest.fixture
def app():
    app = Flask(__name__)
    app.register_blueprint(analysis_bp)
    yield app


def test_email_endpoint_missing_body_returns_400(app):
    client = app.test_client()
    resp = client.post('/api/analysis/email', data=None, content_type='application/json')
    assert resp.status_code == 400


def test_email_endpoint_happy_path_sends_email(app):
    client = app.test_client()

    fake_email = FakeEmailPort()
    set_email_port(fake_email)

    set_analysis_service(FakeAnalysisService())

    body = {
        'email': 'test@example.com',
        'tickers': ['AAPL'],
        'start_date': '2024-01-01',
        'end_date': '2024-02-01',
        'show_reasoning': False
    }

    resp = client.post('/api/analysis/email', data=json.dumps(body), content_type='application/json')
    assert resp.status_code == 200
    assert fake_email.sent, 'Expected an email to be sent'
    sent = fake_email.sent[0]
    assert sent['to'] == 'test@example.com'
    assert 'AAPL' in sent['subject']
    assert 'summary' in sent['text']

import json
from flask import Flask
import pytest

from src.api.routes.analysis import analysis_bp, set_email_port, set_analysis_service


class FakeEmailPort:
    def __init__(self):
        self.sent = []

    def send_email(self, to_address, subject, text_body, html_body=None, headers=None):
        self.sent.append({
            'to': to_address,
            'subject': subject,
            'text': text_body,
            'html': html_body,
        })


class FakeAnalysisService:
    def process_analysis_request(self, request_dto, cancellation_token=None):
        # Yield some progress, then a result event
        yield json.dumps({'type': 'progress', 'stage': 'init', 'message': 'ok', 'progress': 0})
        yield json.dumps({'type': 'result', 'data': {'summary': 'done', 'tickers': request_dto.tickers}})


@pytest.fixture
def app():
    app = Flask(__name__)
    app.register_blueprint(analysis_bp)
    yield app


def test_generate_and_email_analysis_success(app):
    fake_email = FakeEmailPort()
    set_email_port(fake_email)
    set_analysis_service(FakeAnalysisService())

    client = app.test_client()
    payload = {
        'tickers': ['AAPL'],
        'end_date': '2025-01-01',
        'email': 'test@example.com'
    }
    resp = client.post('/api/analysis/email', json=payload)
    assert resp.status_code == 200
    assert fake_email.sent, 'Email should be sent'
    email = fake_email.sent[0]
    assert email['to'] == 'test@example.com'
    assert 'AAPL' in email['subject']
    assert 'summary' in email['text']


def test_generate_and_email_analysis_missing_email(app):
    client = app.test_client()
    payload = {
        'tickers': ['AAPL'],
        'end_date': '2025-01-01',
    }
    resp = client.post('/api/analysis/email', json=payload)
    assert resp.status_code == 400
    body = resp.get_json()
    assert 'error' in body


