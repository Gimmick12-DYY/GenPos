# GenPos - XiaoHongShu AI Ads Workspace (小红书AI广告工作台)

An entrepreneur-facing creative operating system for XiaoHongShu marketing content generation.

## Overview

GenPos is a production-grade, multi-tenant SaaS platform that automates the creation, review, and export of XiaoHongShu (小红书) advertising content. It uses AI agent teams to generate native-feeling note packages — including copy, titles, cover images, and hashtags — tailored to each merchant's brand, products, and target personas.

Key capabilities:

- **Daily Auto-Generation** — Automatically produces fresh note packages every day
- **AI Agent Teams** — Configurable teams of specialized AI personas (writer, photographer, strategist, etc.)
- **Multi-Surface Export** — Export to 笔记 (organic notes), 聚光 (search ads), and 蒲公英 (influencer marketplace)
- **Compliance & Review** — Built-in China advertising compliance checks and human review queue
- **Performance Analytics** — Track and optimize content performance with feedback loops

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 15, React 19, Tailwind CSS 4, Zustand, React Query |
| Backend | FastAPI, SQLAlchemy 2 (async), Pydantic v2 |
| Database | PostgreSQL 16 |
| Cache/Queue | Redis 7 |
| Object Storage | MinIO (S3-compatible) |
| Workflow Engine | Temporal |
| AI | OpenAI API |
| Infrastructure | Docker, Docker Compose |

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 20+
- Docker & Docker Compose

### Quick Start

```bash
# 1. Start infrastructure services
cd infra/docker
docker compose up -d

# 2. Start the API server
cd apps/api
pip install -e ".[dev]"
uvicorn src.main:app --reload

# 3. Start the frontend
cd apps/web
npm install
npm run dev
```

The API will be available at `http://localhost:8000` and the frontend at `http://localhost:3000`.

## Project Structure

```
apps/
  web/                  # Next.js frontend
  api/                  # FastAPI backend
  worker/               # Temporal background workers
packages/
  types/                # Shared type definitions
  config/               # Shared configuration
  prompts/              # AI prompt templates
  compliance-rules/     # China ad compliance rule sets
services/
  asset-service/        # Asset management microservice
  generation-service/   # AI content generation
  compliance-service/   # Compliance checking
  ranking-service/      # Content ranking & optimization
  workflow-service/     # Workflow orchestration
  export-service/       # Multi-surface export
  persona-service/      # AI persona management
  team-composition-service/  # Agent team composition
infra/
  docker/               # Docker & Docker Compose configs
  scripts/              # Dev & deployment scripts
docs/
  api/                  # OpenAPI specification
  architecture/         # Architecture docs
  prd/                  # Product requirements
  prompts/              # Prompt contracts
```
