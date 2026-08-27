# AI Agentic

FastAPI CRUD and Anthropic Q&A chat agent for Cloud Run.

## Configuration

Replace the placeholders with your own values. Do not commit real project IDs, service names, or live URLs.

| Setting | Placeholder |
|---|---|
| GCP project | `PROJECT_ID` |
| Project number | `PROJECT_NUMBER` |
| Cloud Run service | `SERVICE_NAME` |
| Region | `REGION` |
| Secret | `SECRET_NAME` → `ANTHROPIC_API_KEY` |
| Model | `CHAT_MODEL=anthropic:claude-sonnet-4-5` |
| Timeout | `300` seconds |

Chat memory is in-process. It is lost if the Cloud Run instance is replaced.

## Local

```powershell
pip install -r requirements.txt
$env:ANTHROPIC_API_KEY = "your-key"
python -m uvicorn app.main:app --reload --port 8080
```

- API docs: http://localhost:8080/docs
- Chat UI: http://localhost:8080/chat

Send the same `session_id` on `POST /chat` to continue a conversation.

## Deploy to Cloud Run

Set the project:

```powershell
gcloud config set project PROJECT_ID
```

Create the secret (once):

```powershell
gcloud secrets create SECRET_NAME --replication-policy=automatic --project=PROJECT_ID
```

Add the Anthropic API key (paste the key, then Ctrl+Z and Enter):

```powershell
gcloud secrets versions add SECRET_NAME --data-file=- --project=PROJECT_ID
```

Grant the Cloud Run service account access:

```powershell
gcloud secrets add-iam-policy-binding SECRET_NAME `
  --project=PROJECT_ID `
  --member="serviceAccount:PROJECT_NUMBER-compute@developer.gserviceaccount.com" `
  --role="roles/secretmanager.secretAccessor"
```

Deploy this directory:

```powershell
gcloud run deploy SERVICE_NAME `
  --project=PROJECT_ID `
  --region=REGION `
  --source . `
  --set-secrets=ANTHROPIC_API_KEY=SECRET_NAME:latest `
  --set-env-vars=CHAT_MODEL=anthropic:claude-sonnet-4-5 `
  --timeout=300
```

After deploy:

- Service: `https://SERVICE_NAME-PROJECT_NUMBER.REGION.run.app`
- Chat: `https://SERVICE_NAME-PROJECT_NUMBER.REGION.run.app/chat`
- Docs: `https://SERVICE_NAME-PROJECT_NUMBER.REGION.run.app/docs`

Cloud Run sets `PORT`; the container listens on `0.0.0.0`.

## Delete a Cloud Run service

Cloud Run does not rename a service. Deploy a new name, then delete the old one when it is no longer needed.

```powershell
gcloud run services delete SERVICE_NAME --project=PROJECT_ID --region=REGION
```

Skip the confirmation prompt:

```powershell
gcloud run services delete SERVICE_NAME --project=PROJECT_ID --region=REGION --quiet
```

This only deletes that Cloud Run service. The secret is not removed.

## Cloud Run instance (optional)

```powershell
gcloud builds submit --tag REGION-docker.pkg.dev/PROJECT_ID/REPO/SERVICE_NAME --project=PROJECT_ID

gcloud beta run instances deploy SERVICE_NAME `
  --project=PROJECT_ID `
  --image REGION-docker.pkg.dev/PROJECT_ID/REPO/SERVICE_NAME `
  --region REGION `
  --port 8080 `
  --set-secrets=ANTHROPIC_API_KEY=SECRET_NAME:latest `
  --set-env-vars=CHAT_MODEL=anthropic:claude-sonnet-4-5
```
