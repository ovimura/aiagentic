# Items CRUD API

FastAPI CRUD service ready to deploy on Cloud Run.

## Local

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8080
```

Open http://localhost:8080/docs

## Cloud Run service

```bash
gcloud run deploy items-crud \
  --source . \
  --region REGION \
  --allow-unauthenticated
```

## Cloud Run instance

```bash
gcloud builds submit --tag REGION-docker.pkg.dev/PROJECT_ID/REPO/items-crud

gcloud beta run instances deploy items-crud \
  --image REGION-docker.pkg.dev/PROJECT_ID/REPO/items-crud \
  --region REGION \
  --port 8080
```

Cloud Run sets `PORT`; the container listens on `0.0.0.0`.
