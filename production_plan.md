# XiaoHongShu AI Ads Workspace — Production Plan and AI-Agent Build Blueprint

## 1. Executive Summary

This document defines a production-grade plan for building a **China-first, XiaoHongShu-first AI ad workspace** for entrepreneurs. The product supports:

- **daily automatic ad/note generation**
- **on-demand entrepreneur requests through chat or structured forms**
- **quarterly product-asset refresh cycles**
- **cartoon-first creative generation with real product fidelity preserved**
- **XiaoHongShu note packages as the core output object**
- **聚光-ready paid promotion packaging**
- **蒲公英-ready creator collaboration brief generation**
- **a configurable AI agent team with persona slots that you can define later**

The main product idea is not a generic “ad generator.” It is an **entrepreneur-facing creative operating system** that continuously produces XiaoHongShu-native marketing content and lets founders interact with AI agents to generate urgent content whenever needed.

---

## 2. Product Vision

### 2.1 Product Goal

Build a merchant workspace where entrepreneurs can:

- receive fresh XiaoHongShu-ready content every day
- request custom ads on demand in natural language
- manage product images and brand rules quarterly
- generate cartoon-style covers and note assets around real product images
- review, approve, reject, and export content
- learn which styles and angles perform best over time

### 2.2 Core Principle

Separate the system into two clocks:

#### Quarterly truth layer
Stable source of truth:
- real product photos
- transparent cutouts
- packaging references
- brand rules
- approved claims
- banned claims
- seasonal brand notes

#### Daily creativity layer
Fast-moving creative wrapper:
- new hooks
- new titles
- new note bodies
- new cartoon scenes
- new cover styles
- new CTA variants
- new audience angles

This is the central architectural decision. The system should not reinvent the product every day. It should preserve product truth and vary the creative wrapper.

---

## 3. Market and Channel Scope

### 3.1 Geographic focus
- China only

### 3.2 Primary platform
- XiaoHongShu / RedNote

### 3.3 Channel logic
The system should be designed around XiaoHongShu-native workflows rather than Western ad-platform assumptions. The output should prioritize:

- note-style seeding content
- discovery-oriented covers
- save/share-oriented copy
- paid-ready promotion variants
- creator-brief packaging for collaboration workflows

### 3.4 Operational surfaces to support
The system should support preparation for:

- XiaoHongShu professional/business account workflows
- 聚光-ready promotion packages
- 蒲公英-ready creator collaboration packages

---

## 4. Product Modes

### 4.1 Daily Auto Mode
Every day the system should automatically:

1. read recent performance signals
2. detect fatigue and winners
3. choose products and audiences to prioritize
4. generate new note packages
5. generate new cartoon covers and image sets
6. score and rank outputs
7. send top outputs into review or queueing

### 4.2 On-Demand Request Mode
Entrepreneurs should be able to request content at any time via chat or form.

Example requests:
- “给我一个今天就能发的小红书种草版本”
- “换成更适合学生党的语气”
- “做一个更可爱的卡通封面”
- “给我一个适合聚光投放的版本”
- “帮我生成一个达人合作brief”

### 4.3 Guided Campaign Mode
A structured wizard for users who prefer form input rather than free-form prompting.

Recommended fields:
- 产品
- 行业
- 目标人群
- 目标场景
- 发布目的
- 是否投聚光
- 是否做蒲公英合作
- 风格
- 语气
- 禁用词
- 必须出现的卖点
- 是否带价格
- CTA类型

---

## 5. Core Output Object

The system should use a **XiaoHongShu note package** as the primary unit of output.

### 5.1 Note package example

```json
{
  "note_package_id": "np_20260312_0001",
  "merchant_id": "m_001",
  "product_id": "sku_001",
  "source_mode": "daily_auto",
  "objective": "seeding",
  "channel": "xiaohongshu",
  "persona": "22-30岁都市白领",
  "style_family": "治愈系卡通",
  "quarter_asset_pack": "2026_Q2",
  "cover_asset_id": "img_cover_001",
  "image_asset_ids": ["img_001", "img_002", "img_003"],
  "title_variants": [
    "上班族早八真的会反复回购这个",
    "最近通勤包里离不开的小东西",
    "这个可爱又实用，真的很适合打工人"
  ],
  "body_variants": [
    "...",
    "..."
  ],
  "first_comment": "想看我做的另一个通勤版封面，可以留言。",
  "hashtags": ["#通勤好物", "#种草", "#日常分享"],
  "cta_type": "收藏",
  "paid_ready": true,
  "creator_brief_ready": true,
  "compliance_status": "pending_review",
  "ranking_score": 0.84
}
```

### 5.2 Why this object matters
This is much better than treating the output as only:
- one image
- one caption
- one ad block

XiaoHongShu is content-native. The system should package all note components together.

---

## 6. User Experience and Interface Design

### 6.1 Main workspace tabs
Recommended navigation:

- 今日推荐
- 一键生成
- AI对话
- 我的产品库
- 内容工厂
- 待审核
- 投放中心
- 达人合作
- 成效分析
- 品牌规则

### 6.2 Chat workspace
Use for:
- urgent campaigns
- rewriting
- style changes
- audience changes
- tone changes
- special events
- seasonal campaigns

### 6.3 Structured generation panel
Use for repeatable, predictable generation.

### 6.4 Approval dashboard
Should show:
- daily generated packages
- manually requested packages
- approved / rejected / queued / live
- compliance risk state
- ranking score
- fatigue warnings
- export readiness

### 6.5 Asset library
Should support:
- quarterly asset packs
- product cutouts
- logos
- packaging references
- hero packshots
- approval state
- version history

---

## 7. Creative Strategy

### 7.1 Visual rule
**Keep the product real. Cartoon the context.**

This means:
- product packaging stays accurate
- logo stays accurate
- key colors stay accurate
- shape and proportions stay accurate
- surrounding environment becomes cartoon
- props, characters, background, framing, and storytelling can be stylized

### 7.2 Cartoon style families
Examples:
- 治愈系插画
- 轻漫画分镜
- 可爱Q版生活场景
- 手账贴纸风
- 极简软萌插画

### 7.3 Avoid
- copying famous copyrighted cartoon or anime IP
- changing the product so much that trust drops
- over-chaotic, cluttered, low-conversion covers
- fully synthetic product rendering when accurate packshots already exist

### 7.4 Daily variation strategy
Each day, vary along:
- message angle
- cover style family
- CTA family
- audience persona
- use-case scenario
- note tone

Suggested daily combinatorics per product:
- 3 message angles
- 2 style families
- 2 CTA variants
- 2 persona variants

Total: **24 candidate creative combinations per product per day** before ranking and pruning.

---

## 8. Product Requirements

### 8.1 Primary users
- entrepreneurs / merchants
- XiaoHongShu operators
- growth marketers
- small agencies serving merchants

### 8.2 Core use cases
1. Generate daily XiaoHongShu note drafts automatically
2. Generate custom ad/note instantly on request
3. Create cartoon-first visual assets while preserving product truth
4. Generate 聚光-ready variants
5. Generate 蒲公英 creator briefs
6. Manage brand rules and asset packs
7. Approve/reject and queue content
8. Learn from performance over time

### 8.3 Non-goals for v1
- fully autonomous publishing for every merchant
- full multi-country platform coverage
- fully autonomous budget optimization
- long-form video-first generation

---

## 9. Configurable AI Agent Team with Persona Slots

This section adds the feature you requested: a team of agents with different personas, while leaving room for you to define the personas later.

### 9.1 Design goal
The system should allow you to compose an AI team where:
- each agent has a role
- each agent may have a persona
- persona slots are configurable by you
- the role contract stays stable even if persona changes

This is important because personas should change tone, style, behavior framing, and collaboration style, but **should not break the production responsibilities of each agent**.

### 9.2 Architecture rule
Separate:
- **role** = what the agent does
- **persona** = how the agent behaves, writes, critiques, or collaborates

### 9.3 Recommended agent-team model

#### Agent role layer
These are fixed operational responsibilities:
- Founder Copilot Agent
- Strategy Planner Agent
- XiaoHongShu Note Agent
- Cartoon Visual Agent
- Compliance Agent
- Ranking Agent
- Export / Ops Agent
- Learning Agent
- Workflow Supervisor Agent
- Persona Orchestrator Agent

#### Persona layer
This is configurable by you.
Examples of persona slots:
- warm consultant
- sharp creative director
- performance marketer
- cautious reviewer
- playful XiaoHongShu-native operator
- premium brand strategist
- data-driven analyst

Do not hardcode the persona content. Leave persona definitions in configurable files or database records.

### 9.4 Agent team schema

```json
{
  "team_id": "team_default_cn_001",
  "team_name": "XHS Merchant Creative Team",
  "agents": [
    {
      "agent_role": "founder_copilot",
      "persona_id": "PERSONA_SLOT_1",
      "is_required": true
    },
    {
      "agent_role": "strategy_planner",
      "persona_id": "PERSONA_SLOT_2",
      "is_required": true
    },
    {
      "agent_role": "xhs_note_writer",
      "persona_id": "PERSONA_SLOT_3",
      "is_required": true
    },
    {
      "agent_role": "cartoon_visual_designer",
      "persona_id": "PERSONA_SLOT_4",
      "is_required": true
    },
    {
      "agent_role": "compliance_reviewer",
      "persona_id": "PERSONA_SLOT_5",
      "is_required": true
    },
    {
      "agent_role": "ranking_analyst",
      "persona_id": "PERSONA_SLOT_6",
      "is_required": true
    },
    {
      "agent_role": "ops_exporter",
      "persona_id": "PERSONA_SLOT_7",
      "is_required": true
    },
    {
      "agent_role": "learning_analyst",
      "persona_id": "PERSONA_SLOT_8",
      "is_required": true
    }
  ]
}
```

### 9.5 Persona definition schema
Keep persona definitions external and editable.

```json
{
  "persona_id": "PERSONA_SLOT_1",
  "display_name": "TO_BE_DEFINED_BY_OWNER",
  "description": "TO_BE_DEFINED_BY_OWNER",
  "communication_style": "TO_BE_DEFINED_BY_OWNER",
  "decision_style": "TO_BE_DEFINED_BY_OWNER",
  "tone_rules": [
    "TO_BE_DEFINED_BY_OWNER"
  ],
  "forbidden_behaviors": [
    "TO_BE_DEFINED_BY_OWNER"
  ],
  "collaboration_preferences": {
    "escalates_to": [],
    "debates_with": []
  }
}
```

### 9.6 Suggested agent roles

#### Founder Copilot Agent
Role:
- talks to the entrepreneur
- interprets vague requests
- translates requests into structured jobs
- can use a friendlier, founder-facing persona

#### Strategy Planner Agent
Role:
- decides objective, audience, angle, CTA, and style direction
- can use a strategist persona

#### XiaoHongShu Note Agent
Role:
- writes titles, note body, first comment, hashtags, cover text
- can use a platform-native content persona

#### Cartoon Visual Agent
Role:
- creates visual scene briefs, cartoon wrappers, covers, and visual variations
- can use an art-director persona

#### Compliance Agent
Role:
- blocks unsafe or noncompliant outputs
- should prioritize rule fidelity over persona flair
- persona can still shape explanation style

#### Ranking Agent
Role:
- scores outputs for likely performance
- recommends top candidates

#### Export / Ops Agent
Role:
- packages outputs into note-ready, 聚光-ready, and 蒲公英-ready bundles

#### Learning Agent
Role:
- reads performance and adjusts generation priorities

#### Workflow Supervisor Agent
Optional supervisory layer:
- manages agent handoffs
- resolves conflicts
- ensures output completeness

#### Persona Orchestrator Agent
Optional persona-management layer:
- attaches persona templates to roles
- validates persona constraints
- enables A/B testing of different team persona configurations

### 9.7 Rules for persona-enabled teams
1. Personas must not override compliance rules.
2. Personas must not change output schemas.
3. Personas must remain swappable without changing orchestration logic.
4. Every role must still produce deterministic, schema-valid outputs.
5. Persona definitions should be versioned.
6. Teams should be saved as reusable templates.

### 9.8 UI support for agent-team composition
Add a dedicated admin/workspace section:
- Agent Team Designer
- Persona Library
- Team Presets
- Role-to-Persona Mapping
- Persona A/B Tests
- Collaboration Graph

### 9.9 Future feature idea
Allow merchants to choose a team preset such as:
- “soft and warm brand team”
- “performance-first growth team”
- “premium lifestyle team”
- “cute cartoon-focused team”

You can define the actual persona content later.

---

## 10. System Architecture

### 10.1 Top-level services
Recommended service domains:
- frontend
- API gateway
- identity and tenant service
- merchant config service
- product and asset registry
- knowledge base / RAG service
- orchestrator
- agent runtime
- text and image generation service
- compliance service
- ranking service
- analytics service
- workflow scheduler
- export/publishing adapter service
- observability service

### 10.2 Recommended stack
- Frontend: Next.js + TypeScript
- API: FastAPI or NestJS
- Scheduler/orchestration: Temporal, Prefect, or Dagster
- Queue: Redis Streams, RabbitMQ, or Kafka
- Database: Postgres
- Vector store: pgvector or Qdrant
- Object storage: S3-compatible storage
- Monitoring: OpenTelemetry + Grafana + Sentry
- Auth: Clerk/Auth0/custom JWT depending on preference

### 10.3 Monorepo layout

```text
repo/
  apps/
    web/
    api/
    worker/
    admin/
  packages/
    ui/
    config/
    db/
    types/
    prompts/
    agent-sdk/
    xhs-domain/
    compliance-rules/
    analytics/
  services/
    asset-service/
    knowledge-service/
    generation-service/
    compliance-service/
    ranking-service/
    workflow-service/
    export-service/
    persona-service/
    team-composition-service/
  infra/
    terraform/
    docker/
    k8s/
    scripts/
  docs/
    prd/
    architecture/
    runbooks/
    api/
    prompts/
```

### 10.4 Why add persona-service and team-composition-service
Because persona-enabled teams should not be scattered across unrelated services.

Recommended split:
- **persona-service** stores persona definitions, versions, and constraints
- **team-composition-service** stores agent teams, role mappings, and orchestration configurations

---

## 11. Bounded Contexts

### 11.1 Merchant service
Stores:
- merchant profile
- industry
- tone presets
- banned words
- required claims
- banned claims
- review settings

### 11.2 Product and asset service
Stores:
- products
- quarterly asset packs
- packshots
- transparent cutouts
- logos
- packaging references
- asset approval state

### 11.3 Knowledge base service
Stores and retrieves:
- brand guidelines
- successful past creatives
- product facts
- note-writing templates
- compliance guidance
- campaign learnings

### 11.4 Generation service
Handles:
- prompt construction
- LLM text generation
- image editing/generation
- variant packaging
- structured output validation

### 11.5 Compliance service
Checks:
- banned words
- unsupported claims
- style/IP risks
- category rules
- product fidelity
- hard-sell risk

### 11.6 Workflow service
Runs:
- daily jobs
- weekly jobs
- quarterly jobs
- real-time request jobs
- review workflows

### 11.7 Analytics service
Stores:
- impressions
- clicks
- saves
- comments
- conversions
- costs
- fatigue score
- content-level learnings

### 11.8 Export service
Produces:
- note-ready exports
- 聚光-ready bundles
- 蒲公英-ready brief packages

### 11.9 Persona service
Stores:
- persona definitions
- persona versions
- persona constraints
- persona behavior settings
- persona test history

### 11.10 Team composition service
Stores:
- agent-team templates
- role-to-persona mapping
- collaboration graphs
- team versions
- merchant-specific team overrides

---

## 12. Data Model

### 12.1 Core tables

#### merchants
- id
- name
- industry
- xhs_account_type
- uses_juguang
- uses_pugongying
- language
- timezone
- created_at

#### merchant_rules
- merchant_id
- tone_preset
- banned_words
- required_claims
- banned_claims
- compliance_level
- review_mode

#### products
- id
- merchant_id
- name
- category
- status
- primary_objective
- created_at

#### asset_packs
- id
- merchant_id
- quarter_label
- status
- effective_from
- effective_to

#### assets
- id
- asset_pack_id
- product_id
- type
- storage_url
- checksum
- width
- height
- metadata_json
- approval_status

#### generation_jobs
- id
- merchant_id
- source_mode
- trigger_type
- status
- created_at
- completed_at

#### generation_tasks
- id
- job_id
- task_type
- input_json
- output_json
- status

#### note_packages
- id
- merchant_id
- product_id
- asset_pack_id
- source_mode
- objective
- persona
- style_family
- compliance_status
- ranking_score
- review_status
- created_at

#### text_assets
- id
- note_package_id
- asset_role
- content
- language
- version

#### image_assets
- id
- note_package_id
- asset_role
- source_asset_id
- derived_from
- prompt_version
- image_url
- metadata_json

#### briefs
- id
- note_package_id
- brief_type
- content_json

#### performance_metrics
- id
- note_package_id
- date
- impressions
- clicks
- saves
- comments
- cost
- conversions
- revenue

#### review_events
- id
- note_package_id
- reviewer_id
- action
- reason
- created_at

#### prompt_versions
- id
- prompt_family
- version
- template
- status

#### policy_rules
- id
- scope
- rule_type
- rule_payload
- active

### 12.2 Persona/team tables

#### personas
- id
- name
- description
- communication_style
- decision_style
- tone_rules_json
- forbidden_behaviors_json
- version
- active
- created_at

#### persona_constraints
- id
- persona_id
- constraint_type
- constraint_payload

#### agent_roles
- id
- role_key
- display_name
- required_output_schema
- is_required_default

#### agent_teams
- id
- merchant_id nullable
- team_name
- description
- version
- active
- created_at

#### agent_team_members
- id
- team_id
- role_id
- persona_id
- is_required
- ordering

#### agent_collaboration_edges
- id
- team_id
- from_role_id
- to_role_id
- edge_type
- rule_json

#### persona_experiments
- id
- team_id
- experiment_name
- hypothesis
- status
- result_summary

---

## 13. Workflow Design

### 13.1 Daily DAG
1. ingest yesterday’s performance
2. compute fatigue and winners
3. select priority products
4. build daily strategy plans
5. run agent-team orchestration
6. generate note copy
7. generate cartoon covers/images
8. run compliance checks
9. score and rank candidates
10. persist note packages
11. queue top results for review

### 13.2 On-demand DAG
1. parse entrepreneur request
2. fetch merchant/product/team context
3. run Founder Copilot Agent
4. run Strategy Planner Agent
5. run Note Agent + Visual Agent
6. run Compliance Agent
7. run Ranking Agent
8. return top options
9. allow edit loop
10. persist approved output

### 13.3 Quarterly DAG
1. upload asset pack
2. normalize images
3. generate transparent cutouts
4. manual approval
5. update product truth records
6. update brand claims/rules
7. activate asset pack

### 13.4 Weekly learning DAG
1. aggregate performance
2. identify winning styles and angles
3. detect fatigue
4. update ranking weights
5. recommend prompt changes
6. optionally evaluate persona-team effectiveness

### 13.5 Persona/team experiment DAG
1. select comparison group
2. assign alternative team/persona mapping
3. run generation tasks on same product/context
4. compare review quality and performance metrics
5. save experiment results

---

## 14. Prompt Architecture

### 14.1 Planner output schema

```json
{
  "objective": "seeding",
  "persona": "都市通勤女性",
  "message_angles": ["省时", "颜值", "日常治愈"],
  "style_family": "治愈系卡通",
  "cta_type": "收藏",
  "safety_rules": ["不得夸大", "不得承诺效果"]
}
```

### 14.2 Note prompt inputs
- product facts
- audience
- objective
- style family
- banned claims
- required points
- XiaoHongShu-native tone rules
- active agent persona context where applicable

### 14.3 Image prompt inputs
- product reference asset ID
- visual style family
- scene direction
- composition rules
- preserve-product rules
- text overlay constraints
- persona-informed art direction if needed

### 14.4 Persona influence rule
Persona may influence:
- tone
- phrasing style
- critique style
- explanation style
- ideation preferences

Persona must not influence:
- output schema
- compliance bypass
- required business rules
- product truth constraints

---

## 15. Compliance and Safety Rules

### 15.1 Three-layer compliance system

#### Layer A: deterministic rules
- banned words
- required words
- forbidden claims
- category restrictions
- prohibited style/IP references
- max overlay text

#### Layer B: model-based classifiers
- unsupported efficacy claim risk
- hard-sell risk
- medical/financial sensitivity
- style imitation risk
- mismatch with merchant tone

#### Layer C: human review
Required for:
- new merchants
- regulated categories
- first quarterly asset pack
- first paid-ready package
- low-confidence compliance cases

### 15.2 Persona rule
No persona may override compliance decisions.

---

## 16. Ranking and Learning

### 16.1 Initial ranking features
- title quality
- visual quality
- merchant fit
- objective fit
- compliance confidence
- novelty score
- fatigue avoidance

### 16.2 Later ranking model
Train on:
- saves
- clicks
- comments
- conversions
- paid performance
- approval rate
- rejection rate
- persona/team impact if you enable experiments

### 16.3 Fatigue detection
Track:
- repeated hook usage
- repeated style usage
- declining engagement
- repeated cover composition
- repeated persona-language patterns if needed

---

## 17. Export and Operational Routing

### 17.1 v1 strategy
Start with export-ready operational bundles:
- XiaoHongShu note package export
- 聚光-ready bundle export
- 蒲公英 brief export

### 17.2 v2 strategy
Add richer adapters and workflow automation for merchants with the right operational setup.

### 17.3 Export bundle examples

#### Note-ready bundle
- cover assets
- image set
- title variants
- body variants
- hashtags
- first comment
- style notes

#### 聚光-ready bundle
- paid-optimized title/copy
- cover variations
- objective tag
- CTA emphasis
- operator notes

#### 蒲公英-ready bundle
- creator brief
- target audience
- must-say points
- taboo points
- visual reference guidance
- expected style direction

---

## 18. API Design Outline

### Merchant
- `POST /merchants`
- `GET /merchants/:id`
- `PATCH /merchants/:id`
- `GET /merchants/:id/rules`
- `PATCH /merchants/:id/rules`

### Products / assets
- `POST /products`
- `GET /products/:id`
- `POST /asset-packs`
- `POST /asset-packs/:id/assets`
- `POST /asset-packs/:id/activate`

### Generation
- `POST /generate/request`
- `POST /generate/daily/run`
- `GET /generation-jobs/:id`
- `POST /note-packages/:id/regenerate`

### Review
- `GET /review/queue`
- `POST /note-packages/:id/approve`
- `POST /note-packages/:id/reject`

### Export
- `POST /note-packages/:id/export/note`
- `POST /note-packages/:id/export/juguang`
- `POST /note-packages/:id/export/pugongying`

### Analytics
- `POST /metrics/ingest`
- `GET /products/:id/performance`
- `GET /note-packages/:id/performance`

### Persona/team composition
- `POST /personas`
- `GET /personas`
- `PATCH /personas/:id`
- `POST /agent-teams`
- `GET /agent-teams/:id`
- `PATCH /agent-teams/:id`
- `POST /agent-teams/:id/members`
- `POST /agent-teams/:id/experiments`

---

## 19. Codebase Generation Strategy Using AI Agents

### 19.1 Principle
Do **not** ask one AI agent to build the entire product in one pass.

Use a bounded, contract-first, module-based AI development workflow.

### 19.2 Recommended AI coding-agent hierarchy

#### Architect Agent
Outputs:
- service boundaries
- architecture docs
- event schemas
- API contracts
- DB schema plan

#### Backend Agent
Outputs:
- API services
- domain models
- repositories
- task handlers
- business services

#### Frontend Agent
Outputs:
- pages
- forms
- dashboards
- chat UI
- team/persona management UI

#### Prompt/LLM Agent
Outputs:
- prompt templates
- validators
- response schemas
- retry logic

#### Workflow Agent
Outputs:
- DAGs
- queues
- scheduled jobs
- orchestration logic

#### Infra Agent
Outputs:
- Dockerfiles
- Terraform
- CI/CD
- env contracts

#### QA Agent
Outputs:
- unit tests
- integration tests
- prompt regression tests
- contract tests

### 19.3 Golden rule
Every AI-generated module must be constrained by:
- a spec
- a schema
- a test
- an owner

---

## 20. Suggested Build Phases

### Phase 0 — Foundation
Deliver:
- PRD
- architecture docs
- monorepo scaffold
- auth
- merchant model
- product model
- asset upload and storage
- DB migrations
- persona and team schema

### Phase 1 — Manual on-demand MVP
Deliver:
- chat workspace
- structured form
- Founder Copilot Agent
- Strategy Planner Agent
- XiaoHongShu Note Agent
- Cartoon Visual Agent
- Compliance Agent
- review page
- note package persistence

### Phase 2 — Daily generation engine
Deliver:
- daily scheduler
- daily ranking
- auto-generated recommendation queue
- dashboard for today’s items

### Phase 3 — Quarterly asset truth pipeline
Deliver:
- asset pack onboarding
- cutout processing
- asset approval flow
- asset-pack activation

### Phase 4 — Persona-enabled agent team composition
Deliver:
- persona library UI
- team designer UI
- role-to-persona mapping
- agent-team orchestration layer
- persona experiment support

### Phase 5 — Export and operational packaging
Deliver:
- note export bundles
- 聚光-ready bundles
- 蒲公英-ready briefs
- operator workflow tools

### Phase 6 — Analytics and optimization
Deliver:
- performance ingestion
- fatigue scoring
- ranking improvements
- prompt experiments
- persona-team experiments

---

## 21. Quality Gates

### 21.1 Before merge
Require:
- lint
- type check
- unit tests
- schema validation
- API contract tests
- prompt-output validation

### 21.2 Before release
Require:
- staging run of daily DAG
- staging run of on-demand generation
- compliance suite
- image generation smoke tests
- sample persona-team orchestration tests
- export bundle validation

---

## 22. Observability and Auditability

Track:
- every generation request
- prompt version
- model version
- product assets used
- compliance failures
- ranking score
- review actions
- export actions
- active agent team used
- active persona mapping used

This system must be auditable because it is a business-operations platform.

---

## 23. Recommended Task Order for AI Coding Agents

1. generate `PRD.md`
2. generate `ARCHITECTURE.md`
3. generate ERD and SQL migrations
4. generate OpenAPI spec
5. generate monorepo scaffold
6. generate backend domain models
7. generate asset upload service
8. generate persona-service and team-composition-service
9. generate on-demand generation pipeline
10. generate note-package UI
11. generate compliance service
12. generate daily scheduler
13. generate analytics ingestion
14. generate export adapters
15. generate tests and CI

---

## 24. Standard Instruction Block for AI Coding Agents

```text
You are building a production-grade, multi-tenant, China-first XiaoHongShu AI ads workspace.
Follow the architecture docs exactly.
Do not invent new services without updating the architecture spec.
All outputs must be typed, tested, and schema-validated.
Separate role contracts from persona definitions.
Personas must be swappable without changing output schemas or compliance logic.
Return:
1. files created
2. files modified
3. rationale
4. risks
5. tests added
```

For each coding task, also provide:
- exact folder
- interfaces to implement
- input/output contract
- acceptance criteria

---

## 25. Final Recommendation

Build this as:

**an entrepreneur-facing XiaoHongShu creative operating system**
with
- **daily automatic note generation**
- **on-demand conversational generation**
- **quarterly product-truth management**
- **cartoon-first visual generation around real products**
- **聚光-ready and 蒲公英-ready packaging**
- **a configurable AI agent team with role-persona separation and user-defined persona slots**

The strongest architectural decision is:

**stable role contracts + configurable persona layer + quarterly product truth + daily creative variation**

That gives you:
- scalability
- explainability
- business control
- safer compliance
- easier AI-assisted code generation
- easier experimentation later

---

## 26. Immediate Next Documents to Generate

After this markdown blueprint, generate these files next:

1. `PRD.md`
2. `ARCHITECTURE.md`
3. `ERD.sql`
4. `openapi.yaml`
5. `AGENT_TEAM_SPEC.md`
6. `BUILD_BACKLOG.md`
7. `PROMPT_CONTRACTS.md`
8. `WORKFLOW_DAGS.md`
9. `COMPLIANCE_RULES.md`
10. `FRONTEND_INFORMATION_ARCHITECTURE.md`

These should become the canonical inputs for your AI coding agents.
