# fast-api-image-documentation-classifier

FastAPI service that uploads documentation photos, classifies them into document groups, orders pages, and serves grouped results.

## Run with Docker Compose

1. Copy env file:

```bash
cp .env.example .env
```

2. Start infra and app:

```bash
docker compose up -d --build
```

3. Initialize Garage bucket + credentials:

```bash
./scripts/init-garage.sh
```

4. Put generated Garage access key/secret into `.env`, then restart app:

```bash
docker compose up -d app
```

## API Endpoints

- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `POST /api/v1/jobs` (multipart files, async)
- `GET /api/v1/jobs/{job_id}`
- `GET /api/v1/groups/{group_id}`
- `GET /api/v1/images/{image_id}` (redirect to presigned URL)
