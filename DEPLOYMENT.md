# GenPos Deployment Guide


## Architecture Overview

```
User Browser  ──>  Vercel (Next.js)  ──>  Railway (FastAPI)  ──>  Railway PostgreSQL
                                      ──>  Railway Redis
                                      ──>  Cloudflare R2 (Assets)
```

| Component        | Platform        | Purpose                          |
|------------------|-----------------|----------------------------------|
| Frontend         | Vercel          | Next.js SSR + static pages       |
| Backend API      | Railway         | FastAPI, agent pipeline, auth    |
| Database         | Railway Postgres| All application data             |
| Cache            | Railway Redis   | Session cache, rate limiting     |
| Object Storage   | Cloudflare R2   | Product images, generated assets |
| CI/CD            | GitHub Actions  | Lint, type-check, build, deploy  |

---

## 1. Frontend — Vercel

### Setup

1. Go to [vercel.com/new](https://vercel.com/new) and import the `Gimmick12-DYY/GenPos` repository.
2. Set the **Root Directory** to `apps/web`.
3. Vercel auto-detects Next.js — accept the defaults.
4. Add this environment variable in the Vercel dashboard:

   | Variable              | Value                                 |
   |-----------------------|---------------------------------------|
   | `NEXT_PUBLIC_API_URL` | `https://<your-railway-app>.railway.app/api/v1` |

5. Deploy. Vercel will auto-deploy on every push to `main` and create preview deploys for PRs.

### Custom Domain (optional)

In Vercel project settings > Domains, add your custom domain and update DNS records as instructed.

---

## 2. Backend — Railway

### Setup

1. Go to [railway.app](https://railway.app) and create a new project.
2. Click **"Deploy from GitHub Repo"** and select `Gimmick12-DYY/GenPos`.
3. Railway settings:
   - **Root Directory**: `apps/api`
   - **Builder**: Dockerfile
   - **Dockerfile Path**: `Dockerfile` (relative to root directory)
4. Add services:
   - Click **"+ New"** > **"Database"** > **PostgreSQL** — this auto-provisions and sets `DATABASE_URL`.
   - Click **"+ New"** > **"Database"** > **Redis** — this auto-provisions and sets `REDIS_URL`.

### Environment Variables

Set these in the Railway service's **Variables** tab:

| Variable         | Value                                           | Notes                          |
|------------------|-------------------------------------------------|--------------------------------|
| `DATABASE_URL`   | *(auto-set by Railway Postgres)*                | Railway sets this for you      |
| `REDIS_URL`      | *(auto-set by Railway Redis)*                   | Railway sets this for you      |
| `S3_ENDPOINT`    | `https://<account-id>.r2.cloudflarestorage.com` | From Cloudflare R2 dashboard   |
| `S3_ACCESS_KEY`  | *(R2 API token access key)*                     | From R2 API token              |
| `S3_SECRET_KEY`  | *(R2 API token secret key)*                     | From R2 API token              |
| `S3_BUCKET`      | `genpos-assets`                                 | The R2 bucket name             |
| `JWT_SECRET`     | *(random 64-char string)*                       | Generate with `openssl rand -hex 32` |
| `OPENAI_API_KEY` | `sk-...`                                        | Your OpenAI API key            |
| `CORS_ORIGINS`   | `https://your-app.vercel.app` or `["https://..."]` | Your Vercel frontend URL(s)   |
| `PORT`           | `8000`                                          | Railway injects PORT           |

### How Deploys Work

Railway auto-deploys on push to `main`. The deploy process:

1. Builds the Docker image from `apps/api/Dockerfile`
2. Runs `start.sh` which:
   - Executes `alembic upgrade head` (database migrations)
   - Starts `uvicorn` on the configured PORT

### Checking Logs

Use the Railway dashboard or CLI: `railway logs`

---

## 3. Object Storage — Cloudflare R2

### Setup

1. Log in to [Cloudflare Dashboard](https://dash.cloudflare.com) > R2.
2. Create a bucket named `genpos-assets`.
3. Go to **R2** > **Manage R2 API Tokens** > **Create API Token**.
4. Permissions: **Object Read & Write** on the `genpos-assets` bucket.
5. Copy the **Access Key ID** and **Secret Access Key** into Railway env vars.
6. Your S3 endpoint is: `https://<account-id>.r2.cloudflarestorage.com`

### CORS (if needed for direct browser uploads later)

In the R2 bucket settings, add a CORS rule allowing your Vercel domain.

---

## 4. CI/CD — GitHub Actions

The workflow at `.github/workflows/ci.yml` runs on every push and PR:

| Job              | Trigger           | What it does                              |
|------------------|-------------------|-------------------------------------------|
| frontend-check   | Push + PR         | TypeScript type-check, Next.js build      |
| backend-check    | Push + PR         | Ruff lint + format check                  |
| docker-build     | Push to main only | Builds the API Docker image               |

Both Vercel and Railway have their own GitHub integrations that auto-deploy on push to `main`, so the CI workflow focuses on quality gates (lint, types, build) rather than deployment.

---

## 5. Local Development

For local development, use Docker Compose for backing services:

```bash
# Start PostgreSQL, Redis, MinIO, Temporal
docker compose -f infra/docker/docker-compose.yml up -d

# Backend
cd apps/api
pip install -e ".[dev]"
alembic upgrade head
uvicorn src.main:app --reload

# Frontend
cd apps/web
npm install
npm run dev
```

---

## 6. Environment Variable Reference

### Backend (`apps/api`)

| Variable            | Required | Default                           | Description                    |
|---------------------|----------|-----------------------------------|--------------------------------|
| `DATABASE_URL`      | Yes      | `postgresql+asyncpg://...`        | PostgreSQL connection string   |
| `REDIS_URL`         | Yes      | `redis://localhost:6379`          | Redis connection string        |
| `S3_ENDPOINT`       | Yes      | `http://localhost:9000`           | S3-compatible endpoint         |
| `S3_ACCESS_KEY`     | Yes      | `minioadmin`                      | S3 access key                  |
| `S3_SECRET_KEY`     | Yes      | `minioadmin`                      | S3 secret key                  |
| `S3_BUCKET`         | Yes      | `genpos-assets`                   | S3 bucket name                 |
| `JWT_SECRET`        | Yes      | `change-me-in-production`         | JWT signing secret             |
| `JWT_ALGORITHM`     | No       | `HS256`                           | JWT algorithm                  |
| `JWT_EXPIRE_MINUTES`| No       | `1440`                            | Token expiry (24h)             |
| `OPENAI_API_KEY`    | Yes      | *(empty)*                         | OpenAI API key                 |
| `TEMPORAL_HOST`     | No       | `localhost:7233`                  | Temporal server address        |
| `CORS_ORIGINS`      | Yes      | `["http://localhost:3000"]`       | Allowed CORS origins (URL or JSON array) |
| `DEBUG`             | No       | `false`                           | Enable debug logging           |
| `PORT`              | No       | `8000`                            | Server port (Railway sets this)|

### Frontend (`apps/web`)

| Variable              | Required | Default                          | Description                    |
|-----------------------|----------|----------------------------------|--------------------------------|
| `NEXT_PUBLIC_API_URL` | Yes      | `http://localhost:8000/api/v1`   | Backend API base URL           |

---

## 7. Troubleshooting: "无法连接后端" / "Failed to get dev token"

If the frontend shows this error when opening the app:

1. **Vercel env**  
   In Vercel → Project → Settings → Environment Variables, set:
   - `NEXT_PUBLIC_API_URL` = your Railway API base **including** `/api/v1`, e.g. `https://your-app.up.railway.app/api/v1` (no trailing slash after `api/v1`).  
   The frontend calls `NEXT_PUBLIC_API_URL/auth/dev-token` and `NEXT_PUBLIC_API_URL/auth/bootstrap`. If you use a custom domain for the API, use that same base. Redeploy the frontend after changing env vars.

2. **CORS**  
   In Railway → API service → Variables, set:
   - `CORS_ORIGINS` = your Vercel frontend URL, e.g. `https://gen-pos-xxx.vercel.app` (a single URL is fine; you can also use a JSON array like `["https://your-app.vercel.app"]` or comma-separated URLs). Without this, the browser blocks the response and the app reports a connection error.

3. **First-time setup: create a merchant**  
   If the API is reachable but returns "No merchant in database", call once:
   ```bash
   curl -X POST "https://YOUR-RAILWAY-API-URL/api/v1/auth/bootstrap" \
     -H "Content-Type: application/json" -d '{}'
   ```
   Then reload the site; the frontend will get a dev token and work.

4. **Railway API health**  
   Open `https://YOUR-RAILWAY-API-URL/health` in a browser. You should see `{"status":"ok","service":"genpos-api"}`. If not, check Railway logs and that `DATABASE_URL` is set (private URL is fine).

5. **Chat shows "Failed to fetch" or "无法连接后端" when sending a message**  
   The first load may succeed (dev-token works) but POST /chat/message can still fail if: the API crashes during generation (check Railway logs for tracebacks), `OPENAI_API_KEY` is missing or invalid, or the request times out (e.g. Railway/proxy limit). Fix the cause and retry; the app now returns a clearer error when the API responds with an error body.

6. **Reading Railway logs — common errors**  
   When tracing `logs.*.log` or Railway dashboard logs:
   - **`429` / `insufficient_quota` (OpenAI)** — Your OpenAI API key has exceeded quota or billing is not set up. Fix at [platform.openai.com](https://platform.openai.com) (billing / usage).
   - **`Session is already flushing`** / **`cannot use Connection.transaction() in a manually started transaction`** — These came from running writer and designer in parallel on the same DB session; the pipeline now runs them sequentially. If you still see this on an older deploy, redeploy the latest API.
   - **`OPTIONS ... 400 Bad Request`** — Some clients send a preflight that returns 400; if POST immediately after succeeds (e.g. dev-token 200), you can ignore.

---

## 8. Migrating to Another Platform

This setup is fully portable:

- **Frontend**: `next build` produces a standalone Node.js server — runs anywhere
- **Backend**: Standard Docker image — runs on any container platform (AWS ECS, GCP Cloud Run, Aliyun ECS, etc.)
- **Database**: Standard PostgreSQL — migrate with `pg_dump`/`pg_restore`
- **Storage**: R2 is S3-compatible — switch to AWS S3, Aliyun OSS, or MinIO with just env var changes
