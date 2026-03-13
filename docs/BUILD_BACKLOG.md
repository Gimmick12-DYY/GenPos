# GenPos — Build Backlog

> **Version:** 0.1.0-draft
> **Last updated:** 2026-03-12
> **Status:** Living document — items are refined and re-prioritized as work progresses
> **Source documents:** [PRD](prd/PRD.md) · [Architecture](architecture/ARCHITECTURE.md) · [ERD](architecture/ERD.sql) · [Agent Team Spec](architecture/AGENT_TEAM_SPEC.md) · [Production Plan](../production_plan.md)

---

## How to Read This Document

Each backlog item follows a consistent ticket format:

| Field | Meaning |
|---|---|
| **ID** | Unique identifier. `BL-0XX` = Phase 0, `BL-1XX` = Phase 1, etc. |
| **Title** | Short imperative title. |
| **Description** | 2–3 sentences describing what to build and why. |
| **Acceptance Criteria** | Bulleted list of testable conditions that must be true for the item to be considered done. |
| **Priority** | `P0` = must-have for phase gate, `P1` = important but not blocking, `P2` = nice-to-have. |
| **Complexity** | `S` = ≤ 2 days, `M` = 3–5 days, `L` = 1–2 weeks, `XL` = 2+ weeks. |
| **Dependencies** | IDs of prerequisite items that must be completed first. |

---

## Phase 0 — Foundation

> **Goal:** Establish the monorepo, database, authentication, and core CRUD APIs so that all subsequent phases have a stable foundation to build on.

---

### BL-001: Create Monorepo Scaffold

**Description:**
Initialize the repository with the canonical directory structure defined in the architecture doc: `apps/` (web, api, worker, admin), `packages/` (ui, config, db, types, prompts, agent-sdk, xhs-domain, compliance-rules, analytics), `services/`, `infra/`, and `docs/`. Configure Turborepo for the Node workspace and a Python workspace root (`pyproject.toml`) for backend packages.

**Acceptance Criteria:**
- `apps/web`, `apps/api`, `apps/worker`, `apps/admin` directories exist with placeholder entry points
- `packages/` contains all 9 declared sub-packages, each with its own `package.json` or `pyproject.toml`
- `services/` contains stub directories for all 9 services from the architecture doc
- `infra/terraform/`, `infra/docker/`, `infra/k8s/`, `infra/scripts/` directories exist
- `turbo.json` is configured with `build`, `lint`, `test`, and `dev` pipeline targets
- Root `package.json` declares the Node workspace (`apps/*`, `packages/*`)
- Root `pyproject.toml` declares the Python workspace
- `README.md` documents the project structure and setup instructions
- `pnpm install` (or `npm install`) completes without errors
- `turbo run lint` succeeds on the empty scaffold

**Priority:** P0
**Complexity:** M
**Dependencies:** None

---

### BL-002: Set Up Next.js Frontend App

**Description:**
Initialize `apps/web` as a Next.js 14+ application with TypeScript, Tailwind CSS, and the App Router. Configure shared UI package consumption, path aliases, and a basic layout shell with the 10-tab navigation rail defined in the PRD (今日推荐, 一键生成, AI对话, 我的产品库, 内容工厂, 待审核, 投放中心, 达人合作, 成效分析, 品牌规则).

**Acceptance Criteria:**
- `apps/web` runs via `pnpm dev` and renders the shell layout
- Tailwind CSS is configured and functional
- TypeScript strict mode is enabled
- Left-hand navigation rail displays all 10 tabs as defined in PRD § 6.1
- Each tab routes to a placeholder page
- `packages/ui` is consumed as a workspace dependency
- `packages/types` is consumed for shared TypeScript types
- Environment variable loading is configured (`.env.local` for `NEXT_PUBLIC_API_URL`)
- ESLint and Prettier are configured and pass on the scaffold
- The app builds successfully with `next build`

**Priority:** P0
**Complexity:** M
**Dependencies:** BL-001

---

### BL-003: Set Up FastAPI Backend App

**Description:**
Initialize `apps/api` as a FastAPI application (Python 3.12+) with Pydantic v2, CORS middleware, health endpoints (`/healthz`, `/readyz`), and OpenAPI auto-generation. Configure the application to load shared packages (`packages/db`, `packages/config`) and set up the project structure with routers, dependencies, and middleware directories.

**Acceptance Criteria:**
- `apps/api` starts via `uvicorn` and responds to `GET /healthz` with `200 OK`
- `GET /readyz` returns `200` when the database connection is healthy
- OpenAPI docs are accessible at `/docs` (Swagger UI) and `/redoc`
- CORS is configured to allow the frontend origin
- Pydantic v2 is used for all request/response models
- `packages/db` and `packages/config` are importable from the API app
- Router directory structure is created: `routers/merchants.py`, `routers/products.py`, etc.
- Middleware directory contains `tenant_context.py` (stub) and `auth.py` (stub)
- `pytest` runs successfully with at least one passing health-check test
- `ruff` linter passes with zero errors

**Priority:** P0
**Complexity:** M
**Dependencies:** BL-001

---

### BL-004: Set Up Background Worker App

**Description:**
Initialize `apps/worker` as a Temporal worker application in Python. Configure it to connect to a Temporal server, register activity and workflow definitions, and run a basic heartbeat workflow. This worker will execute generation pipeline activities, scheduled jobs, and async processing tasks in later phases.

**Acceptance Criteria:**
- `apps/worker` starts and connects to a Temporal server (local Docker instance)
- A `HealthCheckWorkflow` can be triggered and completes successfully
- Activity registration pattern is established with a sample `ping_activity`
- Worker gracefully shuts down on SIGTERM
- Shared packages (`packages/db`, `packages/config`, `packages/agent-sdk`) are importable
- Worker configuration (task queue name, concurrency limits) is loaded from environment variables
- Logging is configured with structured JSON output
- A basic integration test verifies the health-check workflow

**Priority:** P0
**Complexity:** M
**Dependencies:** BL-001, BL-013

---

### BL-005: Set Up PostgreSQL with Migrations

**Description:**
Configure `packages/db` with SQLAlchemy 2.0 async models and Alembic for database migrations. Create the initial migration that sets up extensions (`pgcrypto`), enum types, and the `set_updated_at()` trigger function. Establish the migration workflow and ensure it runs cleanly against a fresh PostgreSQL 16+ instance.

**Acceptance Criteria:**
- `packages/db` contains SQLAlchemy 2.0 model base with async session factory
- Alembic is configured with `alembic.ini` and a `versions/` directory
- Initial migration creates all enum types from the ERD (17 enum types)
- `pgcrypto` extension is created for `gen_random_uuid()`
- `set_updated_at()` trigger function is created
- `alembic upgrade head` runs cleanly against a fresh PostgreSQL 16+ database
- `alembic downgrade base` cleanly reverses all migrations
- Database URL is loaded from environment variable `DATABASE_URL`
- Async connection pooling is configured with sensible defaults
- A test confirms migration round-trip (upgrade + downgrade) succeeds

**Priority:** P0
**Complexity:** M
**Dependencies:** BL-001

---

### BL-006: Create Database Schema (All 22 Tables)

**Description:**
Implement Alembic migrations for all 22 tables defined in the ERD: `merchants`, `merchant_rules`, `products`, `asset_packs`, `assets`, `generation_jobs`, `generation_tasks`, `note_packages`, `text_assets`, `image_assets`, `briefs`, `performance_metrics`, `review_events`, `prompt_versions`, `policy_rules`, `personas`, `persona_constraints`, `agent_roles`, `agent_teams`, `agent_team_members`, `agent_collaboration_edges`, and `persona_experiments`. Include all indexes, constraints, deferred foreign keys, and `updated_at` triggers.

**Acceptance Criteria:**
- All 22 tables are created with exact column types, defaults, and constraints from the ERD
- All deferred foreign keys are applied (`generation_jobs.team_id` → `agent_teams`, `generation_tasks.persona_id` → `personas`)
- All indexes from ERD § 9 are created (approximately 40 indexes)
- `updated_at` triggers are applied to: `merchants`, `merchant_rules`, `products`, `asset_packs`, `note_packages`, `personas`, `agent_teams`
- Unique constraints match the ERD: `prompt_versions(prompt_family, version)`, `agent_team_members(team_id, role_id)`, `agent_collaboration_edges(team_id, from_role_id, to_role_id, edge_type)`, `performance_metrics(note_package_id, date)`
- Check constraints are applied: `asset_packs_date_range`, `no_self_edge`
- SQLAlchemy ORM models exist for every table with correct relationship definitions
- `alembic upgrade head` creates all tables; `alembic downgrade base` drops them cleanly
- A test suite validates each table exists and has the expected columns

**Priority:** P0
**Complexity:** L
**Dependencies:** BL-005

---

### BL-007: Set Up JWT Authentication

**Description:**
Implement JWT-based authentication in the API gateway with RS256-signed short-lived access tokens (15 min) and longer-lived refresh tokens (7 days). The access token must embed `tenant_id`, `user_id`, and `roles` claims. Implement login, token refresh, and token validation middleware that injects tenant context into every request.

**Acceptance Criteria:**
- `POST /auth/login` accepts credentials and returns `{access_token, refresh_token, expires_in}`
- `POST /auth/refresh` accepts a refresh token and returns a new token pair
- Access tokens are RS256-signed with 15-minute expiry
- Refresh tokens are stored hashed in the database and rotated on use
- JWT middleware validates signature and expiry on every protected route
- `tenant_id`, `user_id`, and `roles` are extracted from the JWT and injected into request state
- Unauthenticated requests to protected routes return `401 Unauthorized`
- Expired tokens return `401` with a `token_expired` error code
- Invalid tokens return `401` with a `token_invalid` error code
- RBAC roles (`owner`, `admin`, `editor`, `viewer`) are defined and enforceable via dependency injection
- Unit tests cover: valid login, invalid credentials, token refresh, expired token rejection, RBAC enforcement

**Priority:** P0
**Complexity:** L
**Dependencies:** BL-003, BL-006

---

### BL-008: Implement Merchant CRUD API

**Description:**
Build the merchant management API endpoints. This includes creating merchants (tenant provisioning), reading merchant profiles, updating merchant settings, and managing per-merchant brand rules (tone presets, banned words, required/banned claims, compliance level, review mode). All operations must be tenant-scoped.

**Acceptance Criteria:**
- `POST /merchants` creates a new merchant and its default `merchant_rules` record
- `GET /merchants/{id}` returns the merchant profile (tenant-scoped — users can only read their own)
- `PATCH /merchants/{id}` updates merchant fields (name, industry, xhs_account_type, uses_juguang, uses_pugongying)
- `GET /merchants/{id}/rules` returns the merchant's brand rules
- `PATCH /merchants/{id}/rules` updates tone_preset, banned_words, required_claims, banned_claims, compliance_level, review_mode
- All endpoints enforce JWT authentication and tenant isolation
- Request/response bodies are Pydantic v2 models with validation
- Invalid merchant IDs return `404 Not Found`
- Cross-tenant access attempts return `403 Forbidden`
- Pagination is supported on list endpoints via `limit` and `offset` query parameters
- Unit tests cover CRUD operations and tenant isolation

**Priority:** P0
**Complexity:** M
**Dependencies:** BL-006, BL-007

---

### BL-009: Implement Product CRUD API

**Description:**
Build the product catalog API. Merchants manage their product catalog through these endpoints. Products are tenant-scoped and support status transitions (`active`, `paused`, `archived`). Each product can be linked to assets and generation jobs.

**Acceptance Criteria:**
- `POST /products` creates a product scoped to the authenticated merchant
- `GET /products` lists products for the current merchant with filtering by `status` and `category`
- `GET /products/{id}` returns product details including linked asset packs
- `PATCH /products/{id}` updates product fields (name, category, status, primary_objective, description)
- `DELETE /products/{id}` soft-deletes by transitioning status to `archived`
- Products can only be accessed by their owning merchant (tenant isolation enforced)
- Status transitions are validated: only valid transitions are allowed
- Pagination via `limit`/`offset` with `total_count` in response
- Filtering by `status` and `category` via query parameters
- Request/response models use Pydantic v2 with proper validation
- Unit tests cover CRUD, filtering, pagination, status transitions, and tenant isolation

**Priority:** P0
**Complexity:** M
**Dependencies:** BL-006, BL-007

---

### BL-010: Implement Asset Upload and S3 Storage

**Description:**
Build the asset upload pipeline: multipart file upload endpoint, S3-compatible storage integration (MinIO for local dev, Alibaba Cloud OSS for production), image metadata extraction (dimensions, format, checksum), and asset records in the database. Assets are organized into asset packs and linked to products.

**Acceptance Criteria:**
- `POST /asset-packs` creates a new asset pack (draft status) for the current merchant
- `POST /asset-packs/{id}/assets` accepts multipart file upload (images: jpg, png, webp)
- Uploaded files are stored in S3 with tenant-prefixed paths: `{tenant_id}/assets/{asset_pack_id}/{filename}`
- Image metadata is extracted on upload: width, height, format, SHA-256 checksum
- `GET /asset-packs/{id}/assets` lists assets in a pack with metadata
- `PATCH /assets/{id}` updates asset type, approval_status, and metadata_json
- Asset approval status transitions are validated: `pending` → `approved` / `rejected`
- S3 client is abstracted behind an interface (supports MinIO locally, OSS in prod)
- File size limit is enforced (configurable, default 10 MB per file)
- File type validation rejects non-image uploads
- Storage URL in the database points to the CDN/S3 path
- Unit tests cover upload, metadata extraction, and approval workflow
- Integration test confirms end-to-end upload to MinIO

**Priority:** P0
**Complexity:** L
**Dependencies:** BL-006, BL-007, BL-013

---

### BL-011: Set Up Persona and Agent Team Schemas

**Description:**
Implement the Pydantic models, SQLAlchemy ORM mappings, and API endpoints for the persona and agent team domain. This covers the `personas`, `persona_constraints`, `agent_roles`, `agent_teams`, `agent_team_members`, `agent_collaboration_edges`, and `persona_experiments` tables with full CRUD and validation logic per the Agent Team Spec.

**Acceptance Criteria:**
- Pydantic models exist for `PersonaDefinition`, `AgentTeamDefinition`, `AgentTeamMember`, `CollaborationEdge`
- `POST /personas` creates a persona with validation of required fields (name, communication_style, decision_style, tone_rules)
- `GET /personas` lists personas with filtering by `active` status and `tags`
- `PATCH /personas/{id}` updates persona fields; creates a new version if the persona is referenced by any generation run
- `POST /agent-teams` creates a team with member bindings and collaboration graph
- `GET /agent-teams/{id}` returns the full team definition including members and graph
- `PATCH /agent-teams/{id}` updates team configuration
- Team validation rules are enforced per Agent Team Spec § 9.1: all required roles present, persona compatible with role, no duplicate roles, collaboration graph is a DAG, compliance reviewer cannot be disabled
- `persona_constraints` are stored and retrievable per persona
- Collaboration graph edges are validated for no self-edges and DAG property
- Unit tests cover CRUD, validation rules, and version immutability

**Priority:** P0
**Complexity:** L
**Dependencies:** BL-006, BL-007

---

### BL-012: Seed Agent Roles Data

**Description:**
Create a database seed script that inserts the 8 canonical agent roles defined in the ERD: `founder_copilot`, `strategy_planner`, `xhs_note_writer`, `cartoon_visual_designer`, `compliance_reviewer`, `ranking_analyst`, `ops_exporter`, and `learning_analyst`. Each role includes its display name, description, required output JSON schema, and `is_required_default` flag.

**Acceptance Criteria:**
- Seed script is idempotent — running it multiple times does not create duplicate records
- All 8 agent roles from ERD § 10 are inserted with correct `role_key`, `display_name`, `description`, `required_output_schema`, and `is_required_default`
- `required_output_schema` contains valid JSON Schema definitions matching the agent output contracts in the Agent Team Spec
- Seed script can be invoked via `python -m scripts.seed_agent_roles` or equivalent
- Seed script is integrated into the Docker Compose startup sequence
- A test verifies all 8 roles exist after seeding
- Seed data matches the `INSERT INTO agent_roles` block in the ERD exactly

**Priority:** P1
**Complexity:** S
**Dependencies:** BL-006

---

### BL-013: Docker Compose for Local Development

**Description:**
Create a Docker Compose configuration that spins up the complete local development environment: PostgreSQL 16, Redis, MinIO (S3-compatible storage), Temporal server + UI, and the application services (API, worker, web). Include health checks, volume mounts for data persistence, and a `.env.example` file.

**Acceptance Criteria:**
- `docker compose up` starts all services: PostgreSQL, Redis, MinIO, Temporal, API, worker, web
- PostgreSQL is accessible on port 5432 with a default `genpos` database
- Redis is accessible on port 6379
- MinIO is accessible on port 9000 (API) and 9001 (console) with a default `genpos-assets` bucket
- Temporal server is accessible on port 7233; Temporal UI on port 8233
- Health checks are defined for all infrastructure services
- Application database migrations run automatically on API startup
- Seed data (agent roles) is loaded on first startup
- `.env.example` documents all required environment variables
- `docker compose down -v` cleanly removes all containers and volumes
- Hot-reload is configured for API (uvicorn --reload) and web (next dev) via volume mounts
- A `Makefile` or `scripts/dev-setup.sh` automates the full local setup sequence
- Documentation in `README.md` explains the local development workflow

**Priority:** P0
**Complexity:** L
**Dependencies:** BL-001

---

## Phase 1 — Manual On-Demand MVP

> **Goal:** Deliver a working on-demand generation pipeline where a merchant can request content through a chat interface or structured form and receive complete note packages. This is the first user-facing milestone.

---

### BL-101: Chat Workspace UI

**Description:**
Build the AI Chat (AI对话) tab as a conversational interface where merchants interact with the Founder Copilot agent. The chat supports multi-turn conversation, displays streaming responses, and renders generated note packages inline when the pipeline completes. Messages are persisted per merchant session.

**Acceptance Criteria:**
- AI对话 tab renders a chat interface with message input, send button, and message history
- Messages stream in real-time using WebSocket or SSE connection to the API
- User messages and AI responses are displayed in a threaded conversation view
- When a generation pipeline completes, note package cards render inline in the chat
- Chat sessions are persisted in the database and resumable
- Typing indicator shows while the AI is processing
- Error states are handled gracefully (network errors, generation failures)
- Chat input supports Chinese IME without issues
- Mobile-responsive layout (the chat is usable on tablet-width screens)
- Message history is paginated (load older messages on scroll up)
- Unit tests cover message rendering and state management

**Priority:** P0
**Complexity:** L
**Dependencies:** BL-002, BL-003, BL-007

---

### BL-102: Structured Generation Form UI

**Description:**
Build the Quick Generate (一键生成) tab and the Guided Campaign Mode wizard as defined in PRD § 4.3. The form collects all generation parameters (product, industry, target audience, scenario, objective, 聚光/蒲公英 flags, style, tone, banned words, required selling points, price toggle, CTA type) and submits them as a `StructuredJobRequest` to the generation endpoint.

**Acceptance Criteria:**
- 一键生成 tab displays the structured generation form
- Product selector loads from the merchant's product library
- All fields from PRD § 4.3 are present with correct types (selects, multi-selects, toggles, text inputs)
- Form validation enforces required fields before submission
- Submission sends a `POST /generate/request` with a valid `StructuredJobRequest` payload
- Loading state shows a progress indicator during generation
- Generated note packages display as visual cards upon completion
- Quick template presets (节日促销, 新品上架, 用户好评) pre-fill the form
- Form state is preserved if the user navigates away and returns
- Chinese labels are used for all fields matching the PRD spec
- Unit tests cover form validation and submission flow

**Priority:** P0
**Complexity:** M
**Dependencies:** BL-002, BL-009

---

### BL-103: Founder Copilot Agent Implementation

**Description:**
Implement the `founder_copilot` agent role as defined in Agent Team Spec § 3.1. This agent parses free-text merchant input, disambiguates product/audience/objective/constraints, asks clarifying questions when intent is ambiguous, and produces a valid `StructuredJobRequest` artifact. It uses the Knowledge Base for product facts and merchant context.

**Acceptance Criteria:**
- Agent accepts free-text input and merchant context as input
- Agent produces a schema-valid `StructuredJobRequest` as output (validated against the JSON schema in Agent Team Spec § 12.1)
- Clarifying questions are returned when the input is ambiguous (e.g., product not specified, objective unclear)
- Agent loads persona overlay from the team composition (warm consultant by default)
- Persona influences tone and question style but not the output schema
- Agent retrieves product catalog and merchant rules for context
- Structured output validation with up to 3 retries on malformed responses
- Conversation history is maintained across turns within a session
- Agent respects the role's tool access: Knowledge Base, Merchant Config
- Unit tests cover: clear request → valid output, ambiguous request → clarification, multi-turn resolution

**Priority:** P0
**Complexity:** L
**Dependencies:** BL-003, BL-008, BL-009, BL-011, BL-012

---

### BL-104: Strategy Planner Agent Implementation

**Description:**
Implement the `strategy_planner` agent role as defined in Agent Team Spec § 3.2. This agent receives a `StructuredJobRequest` and produces a `StrategyPlan` that defines the creative direction: objective, audience segments, message angles, hook types, style family, CTA strategy, safety rules, and a variant matrix.

**Acceptance Criteria:**
- Agent accepts a `StructuredJobRequest` + product truth + performance history as input
- Agent produces a schema-valid `StrategyPlan` as output (validated against Agent Team Spec § 12.2)
- Strategy plan includes at least 1 message angle with hook type annotation
- Variant matrix contains at least `variant_count` entries from the job request
- Style family is selected from the 6 defined families (watercolor, flat_vector, pixel_art, collage, minimal_line, pop_art)
- Required selling points from the job request are propagated to the strategy plan
- Safety rules include merchant-specific banned words and compliance guardrails
- Product truth snapshot is frozen in the plan for downstream consumption
- Persona overlay influences strategic framing and risk appetite
- Structured output validation with up to 3 retries
- Unit tests cover: standard request, merchant with custom constraints, multiple product handling

**Priority:** P0
**Complexity:** L
**Dependencies:** BL-003, BL-011, BL-012

---

### BL-105: XiaoHongShu Note Agent Implementation

**Description:**
Implement the `xhs_note_writer` agent role as defined in Agent Team Spec § 3.3. This agent receives a `StrategyPlan` and produces a `NoteContentSet` containing title variants, body variants, first comments, hashtags, and optional cover text overlays — all in XiaoHongShu-native style and within platform character limits.

**Acceptance Criteria:**
- Agent accepts a `StrategyPlan` + product truth + brand rules as input
- Agent produces a schema-valid `NoteContentSet` as output (validated against Agent Team Spec § 12.3)
- Each variant includes ≥ 2 title options (≤ 20 characters each) with hook-type annotation
- Each variant includes ≥ 1 body option (≤ 1000 characters) with tone and selling-point metadata
- First-comment text is generated for engagement seeding
- ≥ 3 hashtags are generated per variant, ordered by relevance
- All required selling points from the strategy plan are covered in at least one body variant
- Content follows XiaoHongShu platform-native style (not generic ad copy)
- Persona overlay controls tone, vocabulary, emoji density, and sentence structure
- Character count validation is enforced at the agent level before output
- Structured output validation with up to 3 retries
- Unit tests cover: content generation, character limit enforcement, selling point coverage

**Priority:** P0
**Complexity:** L
**Dependencies:** BL-003, BL-011, BL-012

---

### BL-106: Cartoon Visual Agent Implementation

**Description:**
Implement the `cartoon_visual_designer` agent role as defined in Agent Team Spec § 3.4. This agent receives a `StrategyPlan` and approved product assets, then produces a `VisualAssetSet` containing cover compositions and carousel image variants. The agent generates cartoon/illustration scene briefs and image generation prompts while preserving real product photography fidelity.

**Acceptance Criteria:**
- Agent accepts a `StrategyPlan` + approved product assets + brand visual guidelines as input
- Agent produces a schema-valid `VisualAssetSet` as output (validated against Agent Team Spec § 12.4)
- Cover images are specified in both 1:1 and 3:4 aspect ratios
- Scene briefs describe the cartoon/illustration context in natural language
- Image generation prompts include product-fidelity constraints
- `product_fidelity_preserved` flag is set to `true` for all compositions using real packshots
- Style family selection matches the strategy plan directive
- Source product asset IDs are tracked for every generated image
- Persona overlay influences aesthetic preferences and composition style
- Structured output validation with up to 3 retries
- Integration with image generation service (or mock) for actual image creation
- Unit tests cover: scene brief generation, prompt construction, fidelity constraint inclusion

**Priority:** P0
**Complexity:** XL
**Dependencies:** BL-003, BL-010, BL-011, BL-012, BL-112

---

### BL-107: Compliance Agent Implementation

**Description:**
Implement the `compliance_reviewer` agent role as defined in Agent Team Spec § 3.5. This agent receives a combined `NoteContentSet` + `VisualAssetSet` and produces a `ComplianceReport` with per-check scores across all compliance dimensions: banned words, unsupported claims, style/IP risks, category rules, product fidelity, and hard-sell risk.

**Acceptance Criteria:**
- Agent accepts `NoteContentSet` + `VisualAssetSet` + compliance rules + merchant rules as input
- Agent produces a schema-valid `ComplianceReport` as output (validated against Agent Team Spec § 12.5)
- Banned-word check runs against the 《广告法》 Article 9 superlatives list and merchant-specific banned words
- Each compliance check produces a score (0–100) and a list of findings
- Each finding includes finding_id, severity, description, location, suggestion, and rule_id
- Aggregate compliance score is computed per variant
- Variants are classified as `pass`, `review`, or `fail` based on configurable thresholds
- Passing variant IDs are collected in the `passing_variant_ids` array
- Overall pass rate is calculated
- Persona influence is limited to explanation style only — never affects pass/fail decisions
- Unit tests cover: clean content passes, banned word detected, claim violation, product fidelity failure

**Priority:** P0
**Complexity:** L
**Dependencies:** BL-003, BL-011, BL-012

---

### BL-108: Agent Orchestration Pipeline

**Description:**
Implement the Orchestrator that drives the agent pipeline as a Temporal workflow. The orchestrator resolves the active team composition, executes agents in the correct sequence per the collaboration graph (Copilot → Planner → [Note Writer ∥ Visual Designer] → Compliance → Ranking → Export), manages artifact passing between agents, and handles retries and failure recovery.

**Acceptance Criteria:**
- Orchestrator is implemented as a Temporal workflow with deterministic replay
- Team composition is resolved at pipeline start (active team with role-persona mappings)
- Agents execute in the sequence defined by the collaboration graph
- Note Writer and Cartoon Visual Designer execute in parallel
- Compliance Reviewer blocks until both parallel agents complete
- Typed artifacts are passed between agents via the orchestrator's artifact store
- Every artifact is persisted with lineage metadata (artifact_id, type, producer, input_artifacts, generation_id)
- Failed agent steps retry up to 3 times with exponential backoff
- Pipeline produces a `PipelineExecutionReport` with timing, token usage, and step status
- On-demand pipeline supports WebSocket progress updates to the frontend
- Daily-auto mode skips the Founder Copilot step
- Orchestrator handles partial failures gracefully (e.g., visual agent fails but text continues)
- Integration tests cover: full pipeline execution, parallel agent execution, retry on failure

**Priority:** P0
**Complexity:** XL
**Dependencies:** BL-004, BL-103, BL-104, BL-105, BL-106, BL-107

---

### BL-109: Review Page UI

**Description:**
Build the Review Queue (待审核) tab as a Kanban-style board with columns: Pending → Approved → Scheduled → Published. Each note package is displayed as a visual card with cover image preview, title, compliance status, ranking score, and action buttons. Support inline editing of titles, body text, and hashtags, and side-by-side variant comparison.

**Acceptance Criteria:**
- 待审核 tab renders a Kanban board with 4 columns
- Note package cards display: cover image thumbnail, selected title, compliance badge, ranking score
- One-tap approve and reject buttons on each card
- Rejection flow prompts for an optional reason (free text or predefined tags)
- Inline editing of title, body, hashtags, and first comment directly on the card
- Side-by-side comparison view for title and body variants within a package
- Drag-and-drop to move cards between columns (for scheduling)
- Filtering by product, source mode, compliance status, and date range
- Pagination or virtual scrolling for large review queues
- Approve/reject actions call `POST /note-packages/{id}/approve` and `POST /note-packages/{id}/reject`
- Review events are logged in the `review_events` table
- Unit tests cover card rendering, actions, and filtering

**Priority:** P0
**Complexity:** L
**Dependencies:** BL-002, BL-110

---

### BL-110: Note Package Persistence and CRUD API

**Description:**
Implement the full CRUD API for note packages and their child entities (text assets, image assets, briefs). Note packages are created by the generation pipeline and managed through review workflows. This is the central data API that the review UI, export service, and analytics depend on.

**Acceptance Criteria:**
- `POST /note-packages` creates a note package with all child entities (text_assets, image_assets)
- `GET /note-packages` lists packages for the current merchant with filtering by product_id, source_mode, compliance_status, review_status, and date range
- `GET /note-packages/{id}` returns the full package including text_assets, image_assets, and briefs
- `PATCH /note-packages/{id}` updates editable fields (review_status, ranking_score)
- `POST /note-packages/{id}/approve` transitions review_status to `approved` and logs a review_event
- `POST /note-packages/{id}/reject` transitions review_status to `rejected` with reason, logs a review_event
- `GET /note-packages/{id}/text-assets` returns text assets for a package
- `PATCH /text-assets/{id}` allows inline editing of text content
- Pagination with `limit`/`offset` and `total_count`
- All endpoints enforce tenant isolation via JWT tenant_id
- Optimistic locking via `updated_at` prevents concurrent edit conflicts
- Unit tests cover CRUD, review transitions, and tenant isolation

**Priority:** P0
**Complexity:** M
**Dependencies:** BL-006, BL-007

---

### BL-111: On-Demand Generation Endpoint

**Description:**
Implement the `POST /generate/request` endpoint that accepts a `StructuredJobRequest` (or free-text input for chat mode) and triggers the agent orchestration pipeline. The endpoint creates a `generation_job` record, dispatches the Temporal workflow, and returns results via WebSocket progress updates or polling.

**Acceptance Criteria:**
- `POST /generate/request` accepts a `StructuredJobRequest` payload and returns a `job_id`
- A `generation_job` record is created with `source_mode=on_demand`, `trigger_type=user_request`
- The agent orchestration pipeline (BL-108) is triggered as a Temporal workflow
- WebSocket endpoint `/ws/generation/{job_id}` streams progress updates (step completions, partial results)
- `GET /generation-jobs/{id}` returns job status (pending, running, completed, failed)
- `GET /generation-jobs/{id}/result` returns the generated note packages when complete
- Timeout handling: jobs that exceed 60 seconds are marked as failed with a timeout error
- Error responses include descriptive error codes and messages
- Rate limiting: max 10 concurrent generation jobs per merchant
- Generation tasks are logged in the `generation_tasks` table with input/output JSON
- Unit tests cover: job creation, status polling, successful completion, timeout, rate limiting

**Priority:** P0
**Complexity:** L
**Dependencies:** BL-003, BL-007, BL-108, BL-110

---

### BL-112: Text and Image Asset Management

**Description:**
Build the asset management layer that the generation pipeline uses: text generation via LLM APIs (Qwen, GPT-4o) with structured output parsing, image generation/compositing via diffusion model APIs, and storage of generated assets. This is the `services/generation-service` thin wrapper that handles prompt construction, model routing, retry logic, and token budgeting.

**Acceptance Criteria:**
- Text generation function accepts a prompt + model config and returns structured text output
- Image generation function accepts a prompt + product assets and returns image URLs
- Prompt construction assembles templates + product truth + persona instructions
- Model routing supports at least 2 LLM providers (configurable via environment)
- Structured output validation: LLM responses are parsed against Pydantic schemas
- Failed validation triggers retry with escalating prompt specificity (up to 3 retries)
- Token budget tracking: input/output tokens counted per call
- Generated images are uploaded to S3 and URLs are persisted
- Image compositing: product cutout + generated cartoon background → final cover image
- Generation lineage record is created for every call: (prompt_version, model_version, input_hash, output_hash, timestamp)
- API key management for LLM and image model providers via environment variables
- Unit tests cover: prompt construction, structured output parsing, retry logic, token counting

**Priority:** P0
**Complexity:** XL
**Dependencies:** BL-003, BL-010

---

## Phase 2 — Daily Generation Engine

> **Goal:** Automate daily creative generation, implement performance-driven ranking, and deliver the 今日推荐 dashboard for merchants to review auto-generated content each morning.

---

### BL-201: Daily Scheduler (Temporal Workflow)

**Description:**
Implement the daily auto-generation Temporal workflow that fires at a configurable time (default 06:00 CST) for each active tenant. The scheduler iterates over active products, resolves the active team composition, and triggers the agent pipeline for each product. It respects generation quotas (configurable packages per product per day) and handles tenant-level scheduling preferences.

**Acceptance Criteria:**
- Daily workflow is triggered by Temporal cron schedule (`0 6 * * *` CST, configurable per tenant)
- Workflow iterates over all active tenants and their active products
- For each product, the workflow triggers the agent pipeline (BL-108) with `source_mode=daily_auto`
- `StructuredJobRequest` is auto-generated from product truth + merchant rules (no Copilot step)
- Configurable packages per product per day (default: 3) via merchant settings
- Failed individual product runs do not block other products or tenants
- Workflow produces a daily summary: products processed, packages generated, failures
- Execution timing is logged (total duration, per-tenant, per-product)
- Workflow is idempotent: re-running for the same date does not create duplicates
- Monitoring: workflow status is queryable via Temporal visibility API
- Integration test: trigger daily run for a test tenant, verify note packages are created

**Priority:** P0
**Complexity:** L
**Dependencies:** BL-004, BL-108

---

### BL-202: Performance Signal Ingestion

**Description:**
Build the analytics ingestion pipeline that pulls XiaoHongShu performance data (impressions, clicks, saves, comments, conversions, costs, revenue) into the `performance_metrics` table. Support both API-based ingestion (when XHS partner API is available) and CSV manual upload as fallback.

**Acceptance Criteria:**
- `POST /metrics/ingest` accepts a batch of performance metric records for multiple note packages
- CSV upload endpoint `POST /metrics/upload` accepts a CSV file and parses metrics into the database
- Performance metrics are stored per note package per date (unique constraint enforced)
- Derived metrics are computed on write: CTR (clicks/impressions), save rate (saves/impressions), cost-per-conversion
- `GET /products/{id}/performance` returns aggregated performance metrics for a product over a date range
- `GET /note-packages/{id}/performance` returns daily metrics for a specific package
- Data validation: negative values rejected, date must not be in the future
- Duplicate ingestion for the same (note_package_id, date) updates existing records (upsert)
- Tenant isolation enforced on all endpoints
- Unit tests cover: batch ingestion, CSV parsing, derived metric computation, upsert behavior

**Priority:** P0
**Complexity:** M
**Dependencies:** BL-006, BL-007, BL-110

---

### BL-203: Fatigue Detection System

**Description:**
Implement the creative fatigue detection module within `packages/analytics`. The system analyzes engagement trends per product across hooks, styles, tones, and audience angles to detect declining performance patterns. Fatigue scores feed into the ranking engine to suppress stale creative directions.

**Acceptance Criteria:**
- Fatigue score is computed per product per dimension: hook_type, style_family, tone, audience_angle, visual_composition
- Fatigue detection compares recent engagement (last 7 days) against a 30-day baseline
- A fatigue score above a configurable threshold (default 0.7) triggers a warning
- Fatigue warnings include: product_id, fatigued dimension, fatigued value, engagement decline %, recommendation
- `GET /products/{id}/fatigue` returns current fatigue scores across all dimensions
- Fatigue signals are consumable by the ranking service and the strategy planner
- The system tracks repeated pattern usage (e.g., same hook used 5 times in 7 days)
- Declining engagement is measured by comparing CTR and save-rate trends
- Fatigue scores are recalculated on a daily schedule (after metric ingestion)
- Unit tests cover: normal engagement (no fatigue), declining engagement (fatigue detected), threshold tuning

**Priority:** P1
**Complexity:** L
**Dependencies:** BL-202

---

### BL-204: Daily Strategy Planning

**Description:**
Enhance the Strategy Planner agent to leverage performance history and fatigue signals when operating in daily-auto mode. The planner should diversify creative directions away from fatigued patterns, prioritize proven angles, and implement the exploration/exploitation sampling strategy (30% exploration, 70% exploitation) as defined in PRD § 7.3.

**Acceptance Criteria:**
- Strategy planner retrieves performance history for the product (last 30 days)
- Fatigued dimensions are deprioritized in angle/style selection
- Exploration/exploitation balance is configurable (default 30/70)
- Exploration samples from under-represented combinations across all 4 axes (style × hook × composition × tone)
- Exploitation weights toward historically high-performing combinations
- The planner generates 24 candidate combinations per product (as specified in PRD) and selects the top N
- Strategy plan includes diversity metadata: how different this plan is from the last 7 days
- A/B test between exploration and exploitation ratios is supportable
- Unit tests cover: strategy with no history (pure exploration), strategy with rich history (exploitation-heavy), fatigue avoidance

**Priority:** P1
**Complexity:** M
**Dependencies:** BL-104, BL-202, BL-203

---

### BL-205: Batch Generation Pipeline

**Description:**
Optimize the agent orchestration pipeline for batch generation: process multiple products in parallel within a single daily run, manage resource limits (concurrent LLM calls, image generation slots), and implement priority queuing. The batch pipeline should handle 100+ products per tenant within a 30-minute window.

**Acceptance Criteria:**
- Batch pipeline processes multiple products in parallel via Temporal child workflows
- Configurable concurrency limit per tenant (default: 5 concurrent product pipelines)
- Global concurrency limit across all tenants (to prevent LLM API throttling)
- Priority queuing: on-demand requests take priority over daily batch items
- Token budget management: track total tokens per batch and enforce per-tenant limits
- Partial failure handling: failed products are retried once, then logged as failed without blocking others
- Batch produces a summary report: success count, failure count, total packages, total tokens, total duration
- Resource usage is logged per product for cost attribution
- Monitoring alerts if a batch exceeds the 30-minute SLA
- Integration test: batch of 10 products completes within resource limits

**Priority:** P1
**Complexity:** L
**Dependencies:** BL-108, BL-201

---

### BL-206: Ranking and Scoring Engine

**Description:**
Implement the `ranking_analyst` agent role and the ranking service. The ranker scores creative variants across 5 dimensions: predicted engagement, style diversity, brand alignment, objective fit, and compliance confidence. It computes a composite weighted score, ranks variants, and recommends the top-N candidates.

**Acceptance Criteria:**
- Agent accepts compliant variants + performance history + fatigue signals as input
- Agent produces a schema-valid `RankingResult` as output (per Agent Team Spec § 12.6)
- Predicted engagement is based on historical performance signals (CTR, save rate for similar content)
- Style diversity score penalizes variants too similar to recently published content
- Brand alignment score measures fit with merchant's tone preset and brand rules
- Objective fit score measures alignment with the stated marketing goal
- Compliance confidence is derived from the compliance report aggregate score
- Composite score is a weighted sum (weights configurable per tenant)
- Variants are sorted by composite score descending
- Top-N recommended variant IDs are included in the output
- Fatigue warnings are flagged on variants using overused patterns
- Ranking rationale is provided in natural language per variant
- Unit tests cover: scoring with rich history, scoring with no history (fallback to defaults), fatigue warning

**Priority:** P0
**Complexity:** L
**Dependencies:** BL-107, BL-202, BL-203

---

### BL-207: Auto-Generated Recommendation Queue

**Description:**
Build the backend logic that processes daily generation results: top-ranked packages are placed in the merchant's 今日推荐 queue, remaining candidates are available in 内容工厂 for manual browsing. The queue is populated after the daily batch completes and respects merchant review mode settings.

**Acceptance Criteria:**
- After daily generation, top-N packages per product are tagged with `review_status=pending` for 今日推荐
- Remaining generated packages are tagged as available in 内容工厂 (searchable but not surfaced in the daily queue)
- N is configurable per merchant (default 3 per product)
- Packages are ordered by composite ranking score within the daily queue
- Merchant review mode is respected: `all` = all packages require review, `sampling` = random subset, `auto` = auto-approve above threshold
- Auto-approve threshold is configurable (default: composite score ≥ 0.85 AND compliance score ≥ 95)
- Auto-approved packages are logged with `review_events.reviewer_id = 'system'`
- Queue is cleared and regenerated daily (previous day's unreviewed items are archived)
- `GET /review/queue/today` returns the current day's recommendation queue
- Unit tests cover: queue population, review mode enforcement, auto-approve logic

**Priority:** P1
**Complexity:** M
**Dependencies:** BL-110, BL-201, BL-206

---

### BL-208: 今日推荐 Dashboard UI

**Description:**
Build the Today's Picks (今日推荐) tab as the merchant's daily content dashboard. Display auto-generated note packages for the current day as visual cards ranked by predicted performance. Support one-tap approve/reject, quick preview of cover images and title variants, and navigation to the full review page.

**Acceptance Criteria:**
- 今日推荐 tab displays daily-generated note packages as visual cards in a responsive grid
- Cards show: cover image preview, selected title, style family badge, ranking score, compliance status badge
- Cards are sorted by composite ranking score (highest first)
- One-tap approve button marks the package as approved and moves it to the scheduled queue
- One-tap reject button opens a brief rejection reason dialog
- Clicking a card opens a detail drawer with full content preview (all title variants, body, hashtags, images)
- Fatigue warnings are displayed as yellow badges on affected cards
- "Generate more" button triggers an on-demand generation for a specific product
- Empty state is shown when no daily packages exist yet (with explanation and next-run time)
- Date picker allows viewing recommendations from previous days
- Skeleton loading states while data is being fetched
- Unit tests cover: card rendering, approve/reject actions, empty state

**Priority:** P0
**Complexity:** M
**Dependencies:** BL-002, BL-109, BL-207

---

## Phase 3 — Quarterly Asset Truth Pipeline

> **Goal:** Implement the slow-clock truth layer: structured ingestion, normalization, and approval of quarterly product asset packs that feed the generation pipeline's visual assets.

---

### BL-301: Asset Pack Onboarding Flow

**Description:**
Build the complete asset pack onboarding wizard in the Product Library (我的产品库) tab. Merchants upload a new seasonal asset pack by selecting products, uploading images, tagging asset types, and setting effective date ranges. The flow guides them through the `draft → pending_review → active` lifecycle.

**Acceptance Criteria:**
- 我的产品库 tab includes an "Upload New Asset Pack" button that opens the onboarding wizard
- Wizard step 1: select quarter label (e.g., 2026_Q2) and effective date range
- Wizard step 2: drag-and-drop batch image upload with progress indicators
- Wizard step 3: tag each asset with type (packshot, cutout, logo, packaging_ref, hero) and link to product
- Wizard step 4: review all uploaded assets and submit for approval
- Asset pack is created in `draft` status on initiation
- Individual assets are created with `approval_status=pending`
- Upload supports batch processing (up to 50 images per upload)
- Image previews are displayed during the tagging step
- The wizard can be saved as draft and resumed later
- Validation: at least one packshot is required before submission
- Unit tests cover: wizard navigation, upload flow, validation

**Priority:** P0
**Complexity:** L
**Dependencies:** BL-002, BL-010

---

### BL-302: Image Normalization Service

**Description:**
Build an image processing service that normalizes uploaded assets: resize to standard dimensions, convert to consistent formats (JPG for photos, PNG for cutouts), strip EXIF metadata, compute perceptual hashes for deduplication, and extract color palettes. This runs automatically on every asset upload.

**Acceptance Criteria:**
- Image normalization runs asynchronously on every new asset upload
- Photos are resized to max 2048px on the longest edge while preserving aspect ratio
- Cutout images (type=cutout) preserve transparency and are stored as PNG
- EXIF metadata is stripped from all processed images
- SHA-256 checksum and perceptual hash are computed and stored
- Color palette (dominant 5 colors) is extracted and stored in `metadata_json`
- Image dimensions (width, height) are updated in the database after processing
- Duplicate detection: warn if a perceptual hash matches an existing asset in the same pack
- Processing status is tracked (pending → processing → complete → error)
- Original files are preserved; normalized versions are stored alongside
- Unit tests cover: resize, format conversion, EXIF stripping, checksum, color extraction

**Priority:** P1
**Complexity:** M
**Dependencies:** BL-010

---

### BL-303: Transparent Cutout Generation

**Description:**
Implement automatic background removal for product images. When a packshot is uploaded, the system can automatically generate a transparent cutout version using a background-removal model. This cutout is used for compositing products into cartoon contexts.

**Acceptance Criteria:**
- "Generate Cutout" button is available on packshot assets
- Background removal runs asynchronously via the worker
- Removed-background image is stored as a PNG with transparency
- The generated cutout is created as a new asset record (type=cutout) linked to the same product
- Source packshot is referenced via the cutout's `metadata_json`
- Quality threshold: cutouts with visible artifacts are flagged for manual review
- Batch mode: "Generate All Cutouts" processes all packshots in a pack
- Processing progress is visible in the UI
- Generated cutouts enter `pending` approval status by default
- Unit tests cover: successful cutout, artifact detection, batch processing

**Priority:** P1
**Complexity:** M
**Dependencies:** BL-010, BL-004

---

### BL-304: Asset Approval Workflow

**Description:**
Implement the asset approval state machine (`pending → approved / rejected`) with role-based access control. Only merchants with `admin` or `owner` roles can approve assets. Approved assets become immutable and available for generation. Rejected assets can be re-uploaded.

**Acceptance Criteria:**
- `PATCH /assets/{id}/approve` transitions asset from `pending` to `approved`
- `PATCH /assets/{id}/reject` transitions asset from `pending` to `rejected` with a reason
- Only users with `admin` or `owner` RBAC roles can approve/reject
- Approved assets are immutable — further updates return `409 Conflict`
- Rejected assets can be replaced with a new upload (new asset record, old one archived)
- Asset approval status is displayed in the asset library UI with visual badges
- Bulk approve/reject: select multiple assets and apply action in one click
- Approval history is logged for audit (timestamp, user, action)
- Side-by-side comparison view for reviewing assets before approval
- Unit tests cover: approval transitions, RBAC enforcement, immutability

**Priority:** P0
**Complexity:** M
**Dependencies:** BL-010, BL-007

---

### BL-305: Asset Pack Activation

**Description:**
Implement the asset pack activation flow: an asset pack transitions from `draft` → `pending_review` → `active` once it contains at least one approved packshot. Activation triggers the quarterly refresh workflow that archives the previous season's pack and re-embeds product facts in the Knowledge Base.

**Acceptance Criteria:**
- `POST /asset-packs/{id}/submit` transitions pack from `draft` to `pending_review`
- Validation: pack must contain at least one approved packshot to be submitted
- `POST /asset-packs/{id}/activate` transitions pack from `pending_review` to `active`
- Activation archives the previous season's pack for the same merchant (status → `archived`)
- Activation triggers a Temporal workflow to re-embed product facts referencing new assets
- Archived packs remain queryable but are excluded from new generation runs
- Only one pack per merchant per quarter can be `active`
- Date range validation: new pack's `effective_from` must not overlap with active pack
- Activation event is logged with timestamp and user
- `GET /asset-packs?status=active` returns the currently active pack for the merchant
- Unit tests cover: activation flow, previous pack archival, validation rules

**Priority:** P0
**Complexity:** M
**Dependencies:** BL-010, BL-304, BL-004

---

### BL-306: Product Truth Management UI (我的产品库)

**Description:**
Build the complete Product Library (我的产品库) tab with product catalog management, asset pack browsing, and asset detail views. Each product has a detail page showing its generation history, linked asset packs, and active assets. This is the merchant's central interface for managing their product truth layer.

**Acceptance Criteria:**
- 我的产品库 tab displays a grid/list of products with search and category filtering
- Product cards show: name, category, status badge, active asset count, last generation date
- Product detail page includes: editable fields, linked asset packs, assets gallery, generation history
- Asset gallery displays thumbnails with type badges, approval status, and dimensions
- Asset detail view shows: full-size preview, metadata, approval history, linked products
- "Add Product" flow creates a new product with required fields
- Product editing supports inline field updates
- Asset pack timeline shows current and historical packs with activation dates
- Products can be filtered by status (active, paused, archived)
- Responsive layout works on desktop and tablet
- Unit tests cover: product listing, filtering, detail view, asset gallery

**Priority:** P1
**Complexity:** L
**Dependencies:** BL-002, BL-009, BL-010, BL-301

---

## Phase 4 — Persona-Enabled Agent Teams

> **Goal:** Enable merchants to configure, customize, and experiment with AI agent team compositions through persona management, team design, and A/B testing.

---

### BL-401: Persona CRUD Service

**Description:**
Build the full persona management service including CRUD operations, version management, and constraint handling. Personas are immutable once referenced by a generation run — updates create new versions. This implements `services/persona-service` as defined in the Architecture doc § 6.9.

**Acceptance Criteria:**
- `POST /personas` creates a persona with full definition (communication_style, decision_style, tone_rules, forbidden_behaviors, behavioral_parameters, cultural_context, system_prompt_overlay)
- `GET /personas` lists personas with filtering by active status, compatible_roles, and tags
- `GET /personas/{id}` returns the full persona definition including constraints
- `PATCH /personas/{id}` creates a new version if the persona is referenced by any generation run; updates in-place otherwise
- Version history is maintained: `GET /personas/{id}/versions` returns all versions
- `POST /personas/{id}/constraints` adds fine-grained behavior constraints
- `POST /personas/{id}/clone` duplicates a persona as a starting point for customization
- Persona deactivation: `PATCH /personas/{id}` with `active=false`
- Compatible roles validation: persona can only be assigned to roles in its `compatible_roles` list
- System_prompt_overlay can be auto-generated from other persona fields
- Unit tests cover: CRUD, versioning, constraint management, cloning, role compatibility

**Priority:** P0
**Complexity:** M
**Dependencies:** BL-011

---

### BL-402: Team Composition Service

**Description:**
Build the team composition service that manages agent team templates, role-to-persona mappings, collaboration graphs, and team versioning. This implements `services/team-composition-service` as defined in the Architecture doc § 6.10 with full validation per Agent Team Spec § 9.1.

**Acceptance Criteria:**
- `POST /agent-teams` creates a team with agents array and collaboration_graph
- `GET /agent-teams/{id}` returns the full team with members, personas, and graph
- `PATCH /agent-teams/{id}` updates team configuration and increments version
- Team validation enforces all rules from Agent Team Spec § 9.1:
  - All `is_required: true` roles present
  - Persona compatible with assigned role
  - No duplicate roles
  - Collaboration graph is a valid DAG (cycle detection)
  - `compliance_reviewer` cannot be disabled
  - Referenced persona versions exist and are active
- `POST /agent-teams/{id}/resolve` produces a `ResolvedTeamComposition` for a generation run
- Platform-level templates (merchant_id=null) are available to all tenants
- Merchant-level customizations override specific bindings from the template
- Team version history: `GET /agent-teams/{id}/versions`
- One-click rollback to a previous version
- Unit tests cover: team creation, validation rules, resolution, version management

**Priority:** P0
**Complexity:** L
**Dependencies:** BL-011, BL-401

---

### BL-403: Persona Library UI

**Description:**
Build the Persona Library interface as described in Agent Team Spec § 10.2. A browsable, searchable gallery of all available personas with persona cards, search/filter, create/edit forms, version management, and cloning.

**Acceptance Criteria:**
- Persona library displays persona cards with: display_name, description, tone preview, compatible roles, tags
- Search by persona name and description
- Filter by: role compatibility, tags, tone style, formality level, active status
- "Create Persona" button opens a form-based editor with all persona fields
- Live preview of system_prompt_overlay as persona fields are edited
- Version management panel: view version history, compare versions side-by-side, pin active version
- "Clone" button duplicates a persona with a new name
- Persona detail page shows: full definition, constraints, test history, team assignments
- Drag-and-drop support for use in the Team Designer (BL-404)
- Persona cards indicate whether they are currently assigned to the active team
- Unit tests cover: persona listing, filtering, creation form, cloning

**Priority:** P1
**Complexity:** M
**Dependencies:** BL-002, BL-401

---

### BL-404: Team Designer UI

**Description:**
Build the Agent Team Designer visual editor as described in Agent Team Spec § 10.1. This is a drag-and-drop interface where merchants compose teams by assigning personas to roles and editing the collaboration graph.

**Acceptance Criteria:**
- Role list displays all 10 agent roles as cards (8 required + 2 optional)
- Required roles are pre-placed and cannot be removed
- Optional roles (workflow_supervisor, persona_orchestrator) can be toggled on/off
- Drag-and-drop persona binding: drag a persona from the library onto a role card
- Collaboration graph editor: visual DAG showing agent execution order with artifact flow edges
- Real-time validation panel: displays warnings for missing roles, incompatible personas, graph cycles
- Version history sidebar: browse and compare previous team configurations
- "Save as Template" button saves the current team as a reusable preset
- "Reset to Defaults" button reverts to platform default personas
- Bulk swap: select multiple roles and apply a persona to all at once
- Two-column mapping table view as alternative to the graph view
- Unit tests cover: drag-and-drop, validation feedback, save/load

**Priority:** P1
**Complexity:** L
**Dependencies:** BL-002, BL-402, BL-403

---

### BL-405: Role-to-Persona Mapping

**Description:**
Implement the backend logic that resolves role-to-persona mappings at generation time. When a pipeline starts, the system resolves the merchant's active team composition, looks up each role's bound persona, freezes the persona snapshot (for reproducibility), and applies any A/B experiment assignments.

**Acceptance Criteria:**
- `resolve_team_composition(tenant_id, team_id)` returns a `ResolvedTeamComposition` artifact
- Each resolved agent includes: agent_role, is_active, persona_snapshot (full definition frozen at resolution time)
- Persona snapshot is immutable for the duration of the pipeline run
- If a persona has been updated since last resolution, the new version is used
- Experiment assignments are applied: control vs. treatment persona for designated roles
- Resolution fails gracefully if a persona is archived (falls back to platform default)
- Resolution is logged with full snapshot for audit and reproducibility
- `GET /agent-teams/{id}/current-mapping` returns the current live mapping table
- Resolution time is tracked as a metric (should be < 100ms)
- Unit tests cover: normal resolution, missing persona fallback, experiment assignment

**Priority:** P0
**Complexity:** M
**Dependencies:** BL-401, BL-402

---

### BL-406: Agent-Team Orchestration Layer

**Description:**
Enhance the orchestrator (BL-108) to consume `ResolvedTeamComposition` for configuring each agent step. The orchestrator loads the persona overlay for each agent, injects it into the system prompt, and enforces persona constraints in post-processing. This connects the persona system to the generation pipeline.

**Acceptance Criteria:**
- Orchestrator calls `resolve_team_composition()` as the first step of every pipeline
- Each agent step receives the persona snapshot from the resolved composition
- Persona `system_prompt_overlay` is injected after the role-level system prompt
- Persona `behavioral_parameters` (temperature, formality) are applied to LLM call configuration
- Persona `forbidden_behaviors` are enforced as post-processing checks on agent output
- Violations of forbidden behaviors trigger retry (up to 3 times)
- Pipeline execution report includes the resolved team composition metadata
- Agents without a persona (e.g., ops_exporter) run with platform defaults only
- Persona influence boundaries are enforced: persona cannot change output schema, compliance decisions, or tool access
- Unit tests cover: persona injection, constraint enforcement, violation retry, no-persona fallback

**Priority:** P0
**Complexity:** L
**Dependencies:** BL-108, BL-405

---

### BL-407: Persona Experiment Framework

**Description:**
Implement the persona A/B testing infrastructure as described in Agent Team Spec § 10.5. Merchants can create experiments that compare two persona variants on the same role, with configurable traffic split and performance tracking.

**Acceptance Criteria:**
- `POST /persona-experiments` creates an experiment with: team_id, role, persona_a, persona_b, traffic_split
- Experiment status lifecycle: `draft → running → completed / cancelled`
- During generation, the orchestrator assigns persona A or B based on the traffic split
- Experiment assignments are deterministic per product (same product always gets same variant within an experiment)
- `GET /persona-experiments/{id}` returns experiment status and results
- Results include: side-by-side metrics (engagement rate, approval rate, edit rate, compliance pass rate)
- Statistical significance calculation: system indicates when results are significant (p < 0.05)
- "Promote winner" action: one-click to set the winning persona as the active binding
- Experiment data is stored in `persona_experiments` table with `result_summary` JSON
- Maximum one active experiment per role per team
- Unit tests cover: experiment creation, assignment, result aggregation, significance calculation

**Priority:** P2
**Complexity:** L
**Dependencies:** BL-402, BL-406, BL-202

---

## Phase 5 — Export and Operational Packaging

> **Goal:** Package approved creative variants into surface-specific, publish-ready bundles for XiaoHongShu native notes, 聚光 paid promotion, and 蒲公英 creator collaboration.

---

### BL-501: Note Export Bundle Service

**Description:**
Implement the `ops_exporter` agent role for 笔记-ready bundles. Package approved note packages into XiaoHongShu-native format with final images in required dimensions, copy with character-count validation, hashtags, first comment, and compliance report summary.

**Acceptance Criteria:**
- Agent accepts ranked variants + export target specs as input
- Agent produces schema-valid `ExportBundleSet` (per Agent Team Spec § 12.7) with `note_ready` populated
- Cover image is validated for XiaoHongShu requirements: 1:1 or 3:4 aspect ratio
- Title is validated: ≤ 20 characters
- Body is validated: ≤ 1000 characters
- Hashtags are formatted with `#` prefix
- First comment is included in the bundle
- Compliance report summary is attached to each bundle
- `POST /note-packages/{id}/export/note` triggers export and returns the bundle
- Exported bundles are stored and downloadable
- Export history is tracked per note package
- Unit tests cover: format validation, character limits, bundle structure

**Priority:** P0
**Complexity:** M
**Dependencies:** BL-108, BL-110, BL-206

---

### BL-502: 聚光-Ready Bundle Export

**Description:**
Implement 聚光 (Spotlight) export formatting. Generate ad creative images in required dimensions, compose headlines and descriptions optimized for paid search, add CTA and targeting metadata, and include bid-range suggestions based on historical performance.

**Acceptance Criteria:**
- `ExportBundleSet` includes `juguang_ready` object when merchant has `uses_juguang=true`
- Ad images are generated in both 3:4 (feed) and 1:1 (search) aspect ratios
- Headline is optimized for search context (shorter, more direct than organic titles)
- Description includes the CTA and key selling points
- CTA type and text are populated from the strategy plan
- Targeting metadata includes: audience_tags, age_range, gender
- Estimated bid range (CPC min/max in CNY) is computed from historical performance data
- Compliance summary is attached for ad review
- `POST /note-packages/{id}/export/juguang` triggers export and returns the 聚光 bundle
- Bundle format is validated against 聚光 ad spec requirements
- Unit tests cover: ad image dimensions, bid estimation, targeting metadata, format compliance

**Priority:** P1
**Complexity:** M
**Dependencies:** BL-501, BL-202

---

### BL-503: 蒲公英-Ready Brief Export

**Description:**
Implement 蒲公英 (Dandelion) creator collaboration brief generation. Auto-generate structured briefs that include product summary, target audience, required talking points, forbidden topics, visual direction, brand guardrails, example titles, suggested hashtags, target creator tags, collaboration type, and budget range.

**Acceptance Criteria:**
- `ExportBundleSet` includes `pugongying_ready` object when merchant has `uses_pugongying=true`
- Brief includes all fields from the schema: product summary, target audience, talking points, visual direction, brand guardrails
- Forbidden topics are derived from merchant's banned_words and compliance rules
- Example titles are selected from the note package's title variants
- Suggested hashtags come from the note package's hashtag list
- Target creator tags are inferred from the product category and audience
- Collaboration type (图文笔记, 视频笔记, 直播) is set from the job request
- Budget range is populated from merchant configuration or estimated from category benchmarks
- `POST /note-packages/{id}/export/pugongying` triggers export and returns the brief
- Brief is downloadable as a formatted PDF and as structured JSON
- Unit tests cover: brief generation, talking point derivation, forbidden topic extraction

**Priority:** P1
**Complexity:** M
**Dependencies:** BL-501

---

### BL-504: Export Center UI (投放中心)

**Description:**
Build the Distribution Center (投放中心) tab. This is the 聚光 integration dashboard where merchants view exported ad bundles, monitor promotion readiness, and manage the export-to-publish workflow. One-click creation of 聚光 ad units from approved note packages.

**Acceptance Criteria:**
- 投放中心 tab displays a list of approved note packages eligible for 聚光 export
- Each item shows: cover preview, headline, CTA, targeting summary, estimated bid range, export status
- "Export to 聚光" button triggers the 聚光 bundle export (BL-502)
- Exported bundles are displayed with all ad specifications for manual submission to 聚光
- Status tracking: draft → exported → submitted → live (manual status updates for now)
- Filtering by product, date range, and export status
- Side-by-side comparison of multiple exported variants for the same product
- Compliance badge shows compliance status of each exported bundle
- Performance metrics overlay when available (for live items)
- Unit tests cover: listing, export trigger, status updates

**Priority:** P1
**Complexity:** M
**Dependencies:** BL-002, BL-501, BL-502

---

### BL-505: Creator Collaboration UI (达人合作)

**Description:**
Build the Creator Collaboration (达人合作) tab. This is the 蒲公英 integration hub where merchants view generated creator briefs, manage collaboration workflows, and track brief delivery status.

**Acceptance Criteria:**
- 达人合作 tab displays generated creator briefs from note packages
- Brief cards show: product, target audience, collaboration type, budget range, brief status
- "Generate Brief" button creates a 蒲公英 brief from a selected note package (BL-503)
- Brief detail view shows the full structured brief with all talking points and guardrails
- Brief can be edited inline before delivery
- "Download Brief" exports as PDF or structured document
- Status tracking: draft → approved → sent → in_progress → complete
- Brief history is maintained per product
- Creator tag suggestions are displayed for matching (read-only for now — full matching is v2)
- Unit tests cover: brief listing, generation trigger, editing, download

**Priority:** P2
**Complexity:** M
**Dependencies:** BL-002, BL-503

---

## Phase 6 — Analytics and Optimization

> **Goal:** Close the feedback loop: ingest performance data from published content, compute fatigue and ranking signals, run experiments, and surface actionable insights on the analytics dashboard.

---

### BL-601: Performance Metric Ingestion Pipeline

**Description:**
Productionize the metric ingestion pipeline (extending BL-202) into a scheduled Temporal workflow. The weekly learning DAG aggregates performance data, computes derived metrics across time windows (7-day, 30-day, all-time), and feeds insights into the knowledge base for RAG retrieval by the strategy planner.

**Acceptance Criteria:**
- Weekly workflow triggers on a configurable schedule (default: every Monday 02:00 CST)
- Aggregates performance metrics across all note packages per product per tenant
- Computes derived metrics: CTR, save rate, comment rate, cost-per-conversion, ROAS
- Time-windowed aggregations: 7-day rolling, 30-day rolling, all-time
- Top-performing packages per product are identified and tagged
- Aggregate insights are written to the Knowledge Base for RAG retrieval
- Per-product performance summaries are generated for merchant dashboards
- Pipeline handles missing data gracefully (packages with no metrics are skipped)
- Execution report includes: tenants processed, packages analyzed, insights generated
- Unit tests cover: aggregation logic, derived metrics, missing data handling

**Priority:** P1
**Complexity:** M
**Dependencies:** BL-202, BL-004

---

### BL-602: Fatigue Scoring Algorithm

**Description:**
Productionize the fatigue detection system (extending BL-203) with a more sophisticated multi-dimensional fatigue model. Track pattern repetition across hooks, styles, tones, compositions, and even persona-specific language patterns. Output fatigue scores that directly influence the ranking model.

**Acceptance Criteria:**
- Fatigue model operates across 5 dimensions: hook_type, style_family, tone, visual_composition, audience_angle
- Engagement decay is measured using exponential moving average (EMA) with configurable half-life
- Frequency-based fatigue: patterns used more than configurable threshold in 7 days receive fatigue penalties
- Cross-product fatigue: similar patterns across different products for the same merchant are detected
- Fatigue scores are normalized to [0, 1] range
- `GET /products/{id}/fatigue` returns per-dimension fatigue scores with trend visualization data
- Fatigue scores are automatically consumed by the ranking engine (BL-206) as a negative signal
- Fatigue alerts are generated when any dimension exceeds the critical threshold
- Historical fatigue trends are stored for analysis (weekly snapshots)
- Unit tests cover: EMA calculation, frequency detection, cross-product detection, threshold alerts

**Priority:** P1
**Complexity:** M
**Dependencies:** BL-203, BL-601

---

### BL-603: Ranking Model Improvements

**Description:**
Upgrade the ranking engine from the initial heuristic model to a learning-informed model. Use historical performance data to train ranking weights, incorporate the `LearningInsights` from the learning analyst agent, and support configurable weight presets per merchant.

**Acceptance Criteria:**
- Ranking weights are updatable based on historical performance correlation
- Weight update logic: compare predicted engagement rank vs. actual engagement rank over 30-day windows
- Learning analyst agent (Agent Team Spec § 3.8) produces `LearningInsights` with `ranking_weight_updates`
- Merchants can view and manually adjust ranking weights via the UI
- Weight presets: "balanced", "engagement-focused", "diversity-focused", "brand-first"
- A/B test support: test new ranking weights on a subset of daily generation before full rollout
- Ranking model performance is tracked: rank correlation metric (Spearman's rho) between predicted and actual
- Dashboard shows ranking effectiveness over time
- Fallback to default heuristic weights if insufficient data (< 30 data points)
- Unit tests cover: weight update logic, preset application, correlation calculation

**Priority:** P2
**Complexity:** L
**Dependencies:** BL-206, BL-601

---

### BL-604: Prompt Experiment Framework

**Description:**
Build an infrastructure for A/B testing prompt template variations. Each experiment compares two versions of a prompt template for a specific agent role, tracks output quality and downstream performance, and determines the winner with statistical significance.

**Acceptance Criteria:**
- `POST /prompt-experiments` creates an experiment with: prompt_family, version_a, version_b, traffic_split
- Experiment assigns prompt versions consistently per tenant (same tenant always sees same variant)
- Output quality metrics are tracked per prompt version: compliance pass rate, merchant approval rate, edit rate
- Downstream performance is tracked when available: engagement rate, save rate
- Statistical significance is calculated using a two-proportion z-test
- `GET /prompt-experiments/{id}` returns status and results
- "Promote winner" action sets the winning version as `active` in `prompt_versions`
- Experiment audit trail: every generation logs which prompt version was used
- Maximum one active experiment per prompt family
- Experiment results feed into the learning analyst's insights
- Unit tests cover: experiment creation, assignment, result aggregation, significance test

**Priority:** P2
**Complexity:** L
**Dependencies:** BL-112, BL-202

---

### BL-605: Persona-Team Experiment Support

**Description:**
Extend the persona experiment framework (BL-407) with deeper analytics integration. Track not just immediate output quality but downstream XiaoHongShu performance, correlate persona variations with engagement patterns, and produce actionable recommendations for persona tuning.

**Acceptance Criteria:**
- Persona experiment results include downstream performance metrics (impressions, CTR, save rate)
- Cross-experiment analysis: compare personas across multiple roles simultaneously
- Persona effectiveness report: which personas produce the best engagement for which product categories
- Recommendations are generated: "Persona X outperforms Persona Y by 15% save rate for skincare products"
- Results are surfaced in the analytics dashboard under a dedicated "Agent Team Experiments" section
- Historical experiment data is maintained for trend analysis
- Export experiment results as CSV or PDF report
- Learning analyst agent consumes experiment results as input for `persona_experiment_results` in `LearningInsights`
- Unit tests cover: multi-metric comparison, cross-experiment analysis, recommendation generation

**Priority:** P2
**Complexity:** M
**Dependencies:** BL-407, BL-601

---

### BL-606: Analytics Dashboard UI (成效分析)

**Description:**
Build the Performance Analytics (成效分析) tab. This is the comprehensive analytics dashboard showing performance across all published content: engagement trends, top-performing styles, audience demographics, conversion funnels, fatigue alerts, and ranking effectiveness. Data feeds back into the generation and ranking algorithms.

**Acceptance Criteria:**
- 成效分析 tab displays a dashboard with multiple chart sections
- Overview section: total impressions, clicks, saves, comments, conversions across all published content
- Time-series charts: engagement metrics over time with date range selection
- Top performers: ranked list of best-performing note packages with key metrics
- Style analysis: engagement breakdown by style family, hook type, and tone
- Fatigue alerts: visual indicators for dimensions approaching or exceeding fatigue thresholds
- Product comparison: side-by-side performance metrics across products
- Ranking effectiveness: chart showing correlation between predicted and actual engagement
- Experiment results: active experiments with current status and interim results
- All data is tenant-scoped and date-range filterable
- Charts are interactive: click to drill down into specific products or packages
- Dashboard loads within 3 seconds for merchants with up to 1000 published packages
- Unit tests cover: data aggregation, chart rendering, filtering

**Priority:** P1
**Complexity:** XL
**Dependencies:** BL-002, BL-202, BL-601, BL-602

---

## Dependency Graph Summary

```
Phase 0 (Foundation)
  BL-001 ─→ BL-002, BL-003, BL-004, BL-005, BL-013
  BL-005 ─→ BL-006
  BL-006 ─→ BL-007, BL-008, BL-009, BL-010, BL-011, BL-012
  BL-007 ─→ BL-008, BL-009, BL-010

Phase 1 (On-Demand MVP)
  BL-002, BL-003 ─→ BL-101, BL-102
  BL-011, BL-012 ─→ BL-103, BL-104, BL-105, BL-106, BL-107
  BL-103..BL-107 ─→ BL-108 (orchestration)
  BL-108 ─→ BL-111
  BL-110 ─→ BL-109

Phase 2 (Daily Engine)
  BL-108 ─→ BL-201 (scheduler)
  BL-201 ─→ BL-205 (batch)
  BL-202 ─→ BL-203 (fatigue), BL-204 (strategy), BL-206 (ranking)
  BL-206, BL-201 ─→ BL-207 (queue) ─→ BL-208 (dashboard)

Phase 3 (Asset Truth)
  BL-010 ─→ BL-301 (onboarding), BL-302 (normalization), BL-303 (cutouts)
  BL-304 (approval) ─→ BL-305 (activation)

Phase 4 (Persona Teams)
  BL-011 ─→ BL-401 (persona CRUD), BL-402 (team composition)
  BL-401, BL-402 ─→ BL-403, BL-404, BL-405, BL-406
  BL-406 ─→ BL-407 (experiments)

Phase 5 (Export)
  BL-108, BL-206 ─→ BL-501 (note export)
  BL-501 ─→ BL-502 (聚光), BL-503 (蒲公英)
  BL-502 ─→ BL-504 (export UI)
  BL-503 ─→ BL-505 (collab UI)

Phase 6 (Analytics)
  BL-202 ─→ BL-601 (ingestion pipeline), BL-602 (fatigue scoring)
  BL-206, BL-601 ─→ BL-603 (ranking improvements)
  BL-601 ─→ BL-604 (prompt experiments), BL-605 (persona experiments)
  BL-601, BL-602 ─→ BL-606 (dashboard)
```

---

## Appendix: Priority Summary

| Priority | Count | Description |
|---|---|---|
| **P0** | 30 | Must-have for the phase gate. Blocks downstream work. |
| **P1** | 14 | Important for a complete experience. Can be deferred within the phase. |
| **P2** | 6 | Nice-to-have. Can be deferred to a later phase without blocking users. |

### P0 Items by Phase

| Phase | P0 Items |
|---|---|
| Phase 0 | BL-001, BL-002, BL-003, BL-004, BL-005, BL-006, BL-007, BL-008, BL-009, BL-010, BL-011, BL-013 |
| Phase 1 | BL-101, BL-102, BL-103, BL-104, BL-105, BL-106, BL-107, BL-108, BL-109, BL-110, BL-111, BL-112 |
| Phase 2 | BL-201, BL-202, BL-206, BL-208 |
| Phase 3 | BL-301, BL-304, BL-305 |
| Phase 4 | BL-401, BL-402, BL-405, BL-406 |
| Phase 5 | BL-501 |
| Phase 6 | (none) |

---

## Appendix: Complexity Summary

| Complexity | Count | Estimate |
|---|---|---|
| **S** | 1 | ≤ 2 days |
| **M** | 23 | 3–5 days |
| **L** | 19 | 1–2 weeks |
| **XL** | 7 | 2+ weeks |

**Total estimated effort:** ~50 engineering-weeks (assuming 2 engineers full-time).

---

## Appendix: Related Documents

| Document | Path | Relationship |
|---|---|---|
| PRD | `docs/prd/PRD.md` | Product requirements driving backlog priorities |
| Architecture | `docs/architecture/ARCHITECTURE.md` | Technical architecture constraining implementation |
| ERD | `docs/architecture/ERD.sql` | Database schema for all 22 tables |
| Agent Team Spec | `docs/architecture/AGENT_TEAM_SPEC.md` | Agent role definitions and I/O contracts |
| Production Plan | `production_plan.md` | Phase structure and build blueprint |
