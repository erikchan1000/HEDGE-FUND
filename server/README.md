AI Hedge Fund Server

API endpoints
- POST /api/analysis/generate: Stream analysis results.
- POST /api/analysis/email: Generate an analysis and email the result.

POST /api/analysis/email
- Body example:

```
{
  "email": "you@example.com",
  "tickers": ["AAPL"],
  "start_date": "2024-01-01",
  "end_date": "2024-02-01",
  "show_reasoning": false
}
```

- Response: { "message": "Analysis generated and emailed successfully" }

Email delivery
- The app uses an EmailPort with two adapters:
  - SendGridEmailAdapter (default when SENDGRID_API_KEY and EMAIL_FROM are set)
  - ConsoleEmailAdapter (fallback for local dev; logs the email)

Environment variables
- EMAIL_FROM: The from/sender address (e.g., no-reply@yourdomain.com)
- SENDGRID_API_KEY: SendGrid API key with Mail Send permission
- Other existing provider keys (e.g., POLYGON_API_KEY) as already configured

GCP + SendGrid setup (Cloud Run)
- Enable services: Cloud Run, Cloud Build, Artifact Registry, Secret Manager, Cloud Logging/Monitoring
- Create Secret Manager secret: SENDGRID_API_KEY
- Deploy to Cloud Run and set:
  - EMAIL_FROM env var
  - Mount SENDGRID_API_KEY from Secret Manager (runtime environment variable)
- SendGrid configuration:
  - Create account via Google Cloud Marketplace or directly
  - Verify sender or set up domain authentication (DNS)
  - Use the generated API key in SENDGRID_API_KEY

Local development
- Install dependencies: poetry install
- Run tests: poetry run pytest -q
- Run server: python app.py


