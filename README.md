# Items CRUD API

FastAPI CRUD and Anthropic Q&A chat agent for Cloud Run.

## Configuration

| Setting | Value |
|---|---|
| GCP project | `markethub-70f1a` |
| Project number | `146001622616` |
| Cloud Run service | `items-crud` |
| Region | `us-west1` |
| Secret | `anthropic-api-key` → `ANTHROPIC_API_KEY` |
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

## Deploy to the existing Cloud Run service

Set the project:

```powershell
gcloud config set project markethub-70f1a
```

Create the secret (once):

```powershell
gcloud secrets create anthropic-api-key --replication-policy=automatic --project=markethub-70f1a
```

Add the Anthropic API key (paste the key, then Ctrl+Z and Enter):

```powershell
gcloud secrets versions add anthropic-api-key --data-file=- --project=markethub-70f1a
```

Grant the Cloud Run service account access:

```powershell
gcloud secrets add-iam-policy-binding anthropic-api-key `
  --project=markethub-70f1a `
  --member="serviceAccount:146001622616-compute@developer.gserviceaccount.com" `
  --role="roles/secretmanager.secretAccessor"
```

Redeploy this directory onto `items-crud`:

```powershell
gcloud run deploy items-crud `
  --project=markethub-70f1a `
  --region=us-west1 `
  --source . `
  --set-secrets=ANTHROPIC_API_KEY=anthropic-api-key:latest `
  --set-env-vars=CHAT_MODEL=anthropic:claude-sonnet-4-5 `
  --timeout=300
```

After deploy:

- Service: https://items-crud-146001622616.us-west1.run.app
- Chat: https://items-crud-146001622616.us-west1.run.app/chat
- Docs: https://items-crud-146001622616.us-west1.run.app/docs

Cloud Run sets `PORT`; the container listens on `0.0.0.0`.

## Delete a Cloud Run service

Cloud Run does not rename a service. Deploy a new name, then delete the old one when it is no longer needed.

```powershell
gcloud run services delete SERVICE_NAME --project=markethub-70f1a --region=us-west1
```

Skip the confirmation prompt:

```powershell
gcloud run services delete SERVICE_NAME --project=markethub-70f1a --region=us-west1 --quiet
```

Example — remove the unused `items-crud` service (keep `aiagentic`):

```powershell
gcloud run services delete items-crud --project=markethub-70f1a --region=us-west1
```

This only deletes that Cloud Run service. The `anthropic-api-key` secret is not removed.

## Cloud Run instance (optional)

```powershell
gcloud builds submit --tag us-west1-docker.pkg.dev/markethub-70f1a/REPO/items-crud --project=markethub-70f1a

gcloud beta run instances deploy items-crud `
  --project=markethub-70f1a `
  --image us-west1-docker.pkg.dev/markethub-70f1a/REPO/items-crud `
  --region us-west1 `
  --port 8080 `
  --set-secrets=ANTHROPIC_API_KEY=anthropic-api-key:latest `
  --set-env-vars=CHAT_MODEL=anthropic:claude-sonnet-4-5
```
