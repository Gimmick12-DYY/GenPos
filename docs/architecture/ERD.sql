-- ============================================================================
-- GenPos (小红书AI广告工作台) — Database Schema
-- PostgreSQL 15+ DDL
-- ============================================================================
-- Multi-tenant, China-first XiaoHongShu AI ads workspace.
-- All tables use UUID primary keys via gen_random_uuid().
-- Timestamps default to now() and use timestamptz for timezone awareness.
-- ============================================================================

BEGIN;

-- --------------------------------------------------------------------------
-- 0. Extensions
-- --------------------------------------------------------------------------
CREATE EXTENSION IF NOT EXISTS "pgcrypto";  -- gen_random_uuid()

-- --------------------------------------------------------------------------
-- 1. Enum Types
-- --------------------------------------------------------------------------

CREATE TYPE compliance_level AS ENUM ('strict', 'standard', 'relaxed');
CREATE TYPE review_mode      AS ENUM ('all', 'sampling', 'auto');

CREATE TYPE product_status    AS ENUM ('active', 'paused', 'archived');
CREATE TYPE asset_pack_status AS ENUM ('draft', 'pending_review', 'active', 'archived');

CREATE TYPE asset_type       AS ENUM ('packshot', 'cutout', 'logo', 'packaging_ref', 'hero', 'other');
CREATE TYPE approval_status  AS ENUM ('pending', 'approved', 'rejected');

CREATE TYPE source_mode  AS ENUM ('daily_auto', 'on_demand', 'campaign');
CREATE TYPE trigger_type AS ENUM ('scheduler', 'user_request', 'api');
CREATE TYPE job_status   AS ENUM ('pending', 'running', 'completed', 'failed', 'cancelled');

CREATE TYPE task_type   AS ENUM ('strategy', 'text_gen', 'image_gen', 'compliance', 'ranking');
CREATE TYPE task_status AS ENUM ('pending', 'running', 'completed', 'failed');

CREATE TYPE objective_type     AS ENUM ('seeding', 'conversion', 'awareness', 'engagement');
CREATE TYPE compliance_check   AS ENUM ('pending', 'passed', 'failed', 'review_needed');
CREATE TYPE review_status_type AS ENUM ('pending', 'approved', 'rejected', 'queued', 'live');

CREATE TYPE text_asset_role  AS ENUM ('title', 'body', 'first_comment', 'hashtag', 'cta', 'cover_text');
CREATE TYPE image_asset_role AS ENUM ('cover', 'carousel_1', 'carousel_2', 'carousel_3', 'carousel_4', 'carousel_5');

CREATE TYPE brief_type    AS ENUM ('note_export', 'juguang', 'pugongying');
CREATE TYPE review_action AS ENUM ('approve', 'reject', 'request_revision', 'escalate');
CREATE TYPE prompt_status AS ENUM ('draft', 'active', 'deprecated');

CREATE TYPE policy_scope     AS ENUM ('global', 'merchant', 'category');
CREATE TYPE policy_rule_type AS ENUM (
    'banned_word', 'required_word', 'forbidden_claim',
    'category_restriction', 'style_restriction', 'max_overlay'
);

CREATE TYPE edge_type        AS ENUM ('delegates_to', 'reviews', 'escalates_to', 'debates_with');
CREATE TYPE experiment_status AS ENUM ('draft', 'running', 'completed', 'cancelled');


-- ============================================================================
-- 2. Core Tables
-- ============================================================================

-- --------------------------------------------------------------------------
-- 2.1 merchants — Top-level tenant entity
-- --------------------------------------------------------------------------
CREATE TABLE merchants (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name             VARCHAR(255)  NOT NULL,
    industry         VARCHAR(128),
    xhs_account_type VARCHAR(64),
    uses_juguang     BOOLEAN       NOT NULL DEFAULT FALSE,
    uses_pugongying  BOOLEAN       NOT NULL DEFAULT FALSE,
    language         VARCHAR(10)   NOT NULL DEFAULT 'zh-CN',
    timezone         VARCHAR(64)   NOT NULL DEFAULT 'Asia/Shanghai',
    created_at       TIMESTAMPTZ   NOT NULL DEFAULT now(),
    updated_at       TIMESTAMPTZ   NOT NULL DEFAULT now()
);

COMMENT ON TABLE  merchants              IS '顶层租户实体 — 每个商家一条记录';
COMMENT ON COLUMN merchants.id           IS '全局唯一商家标识';
COMMENT ON COLUMN merchants.xhs_account_type IS '小红书帐号类型 (专业号/企业号 etc.)';
COMMENT ON COLUMN merchants.uses_juguang IS '是否使用聚光投放';
COMMENT ON COLUMN merchants.uses_pugongying IS '是否使用蒲公英达人合作';

-- --------------------------------------------------------------------------
-- 2.2 merchant_rules — Per-merchant brand guardrails
-- --------------------------------------------------------------------------
CREATE TABLE merchant_rules (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    merchant_id      UUID             NOT NULL REFERENCES merchants(id) ON DELETE CASCADE,
    tone_preset      VARCHAR(128),
    banned_words     JSONB            NOT NULL DEFAULT '[]'::jsonb,
    required_claims  JSONB            NOT NULL DEFAULT '[]'::jsonb,
    banned_claims    JSONB            NOT NULL DEFAULT '[]'::jsonb,
    compliance_level compliance_level NOT NULL DEFAULT 'standard',
    review_mode      review_mode      NOT NULL DEFAULT 'all',
    created_at       TIMESTAMPTZ      NOT NULL DEFAULT now(),
    updated_at       TIMESTAMPTZ      NOT NULL DEFAULT now()
);

COMMENT ON TABLE  merchant_rules                  IS '商家品牌规则 — 禁用词、必须卖点、合规等级';
COMMENT ON COLUMN merchant_rules.tone_preset      IS '预设语气风格 (轻松/专业/种草感 etc.)';
COMMENT ON COLUMN merchant_rules.banned_words     IS '禁用词列表 (JSON array of strings)';
COMMENT ON COLUMN merchant_rules.required_claims  IS '必须出现的卖点 (JSON array)';
COMMENT ON COLUMN merchant_rules.compliance_level IS '合规审查严格程度';
COMMENT ON COLUMN merchant_rules.review_mode      IS '审核模式: all=全部人审, sampling=抽检, auto=自动通过';

-- --------------------------------------------------------------------------
-- 2.3 products — Merchant product catalogue
-- --------------------------------------------------------------------------
CREATE TABLE products (
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    merchant_id       UUID           NOT NULL REFERENCES merchants(id) ON DELETE CASCADE,
    name              VARCHAR(255)   NOT NULL,
    category          VARCHAR(128),
    status            product_status NOT NULL DEFAULT 'active',
    primary_objective VARCHAR(128),
    description       TEXT,
    created_at        TIMESTAMPTZ    NOT NULL DEFAULT now(),
    updated_at        TIMESTAMPTZ    NOT NULL DEFAULT now()
);

COMMENT ON TABLE  products                    IS '商家产品目录';
COMMENT ON COLUMN products.primary_objective  IS '产品主要营销目标 (种草/转化 etc.)';
COMMENT ON COLUMN products.status             IS '产品状态: active/paused/archived';

-- --------------------------------------------------------------------------
-- 2.4 asset_packs — Quarterly visual asset bundles
-- --------------------------------------------------------------------------
CREATE TABLE asset_packs (
    id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    merchant_id    UUID              NOT NULL REFERENCES merchants(id) ON DELETE CASCADE,
    quarter_label  VARCHAR(16)       NOT NULL,
    status         asset_pack_status NOT NULL DEFAULT 'draft',
    effective_from DATE,
    effective_to   DATE,
    created_at     TIMESTAMPTZ       NOT NULL DEFAULT now(),
    updated_at     TIMESTAMPTZ       NOT NULL DEFAULT now(),

    CONSTRAINT asset_packs_date_range CHECK (effective_to IS NULL OR effective_to >= effective_from)
);

COMMENT ON TABLE  asset_packs               IS '季度素材包 — 每季度刷新的产品图片/视觉资产';
COMMENT ON COLUMN asset_packs.quarter_label IS '季度标签, e.g. 2026_Q2';

-- --------------------------------------------------------------------------
-- 2.5 assets — Individual visual assets within a pack
-- --------------------------------------------------------------------------
CREATE TABLE assets (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    asset_pack_id   UUID            NOT NULL REFERENCES asset_packs(id) ON DELETE CASCADE,
    product_id      UUID            REFERENCES products(id) ON DELETE SET NULL,
    type            asset_type      NOT NULL,
    storage_url     TEXT            NOT NULL,
    checksum        VARCHAR(128),
    width           INT,
    height          INT,
    metadata_json   JSONB           NOT NULL DEFAULT '{}'::jsonb,
    approval_status approval_status NOT NULL DEFAULT 'pending',
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT now()
);

COMMENT ON TABLE  assets                IS '单个视觉素材 (产品图/抠图/logo/包装参考 etc.)';
COMMENT ON COLUMN assets.type           IS '素材类型: packshot/cutout/logo/packaging_ref/hero/other';
COMMENT ON COLUMN assets.storage_url    IS '对象存储 URL (CDN)';
COMMENT ON COLUMN assets.checksum       IS '文件校验和 (SHA-256)';
COMMENT ON COLUMN assets.metadata_json  IS '扩展元数据 (EXIF, color palette etc.)';


-- ============================================================================
-- 3. Generation Pipeline
-- ============================================================================

-- --------------------------------------------------------------------------
-- 3.1 generation_jobs — Top-level generation orchestration unit
-- --------------------------------------------------------------------------
CREATE TABLE generation_jobs (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    merchant_id  UUID         NOT NULL REFERENCES merchants(id) ON DELETE CASCADE,
    source_mode  source_mode  NOT NULL,
    trigger_type trigger_type NOT NULL,
    status       job_status   NOT NULL DEFAULT 'pending',
    team_id      UUID,        -- FK added after agent_teams is created
    created_at   TIMESTAMPTZ  NOT NULL DEFAULT now(),
    completed_at TIMESTAMPTZ
);

COMMENT ON TABLE  generation_jobs              IS '生成任务 — 每次生成请求的顶层追踪';
COMMENT ON COLUMN generation_jobs.source_mode  IS '生成来源: daily_auto/on_demand/campaign';
COMMENT ON COLUMN generation_jobs.trigger_type IS '触发方式: scheduler/user_request/api';

-- --------------------------------------------------------------------------
-- 3.2 generation_tasks — Individual agent tasks within a job
-- --------------------------------------------------------------------------
CREATE TABLE generation_tasks (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id       UUID        NOT NULL REFERENCES generation_jobs(id) ON DELETE CASCADE,
    task_type    task_type   NOT NULL,
    input_json   JSONB       NOT NULL DEFAULT '{}'::jsonb,
    output_json  JSONB       NOT NULL DEFAULT '{}'::jsonb,
    status       task_status NOT NULL DEFAULT 'pending',
    agent_role   VARCHAR(64),
    persona_id   UUID,       -- FK added after personas is created
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
    completed_at TIMESTAMPTZ
);

COMMENT ON TABLE  generation_tasks            IS '生成子任务 — 单个 Agent 执行的原子任务';
COMMENT ON COLUMN generation_tasks.task_type  IS '任务类型: strategy/text_gen/image_gen/compliance/ranking';
COMMENT ON COLUMN generation_tasks.agent_role IS '执行此任务的 Agent 角色标识';


-- ============================================================================
-- 4. Note Package & Output Tables
-- ============================================================================

-- --------------------------------------------------------------------------
-- 4.1 note_packages — Core output object (笔记包)
-- --------------------------------------------------------------------------
CREATE TABLE note_packages (
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    merchant_id       UUID              NOT NULL REFERENCES merchants(id) ON DELETE CASCADE,
    product_id        UUID              NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    asset_pack_id     UUID              REFERENCES asset_packs(id) ON DELETE SET NULL,
    generation_job_id UUID              REFERENCES generation_jobs(id) ON DELETE SET NULL,
    source_mode       source_mode       NOT NULL,
    objective         objective_type    NOT NULL,
    persona           VARCHAR(128),
    style_family      VARCHAR(64),
    compliance_status compliance_check  NOT NULL DEFAULT 'pending',
    ranking_score     DECIMAL(6,4),
    review_status     review_status_type NOT NULL DEFAULT 'pending',
    created_at        TIMESTAMPTZ       NOT NULL DEFAULT now(),
    updated_at        TIMESTAMPTZ       NOT NULL DEFAULT now()
);

COMMENT ON TABLE  note_packages                   IS '笔记包 — GenPos 核心输出对象';
COMMENT ON COLUMN note_packages.objective         IS '营销目标: seeding(种草)/conversion(转化)/awareness(曝光)/engagement(互动)';
COMMENT ON COLUMN note_packages.persona           IS '生成此笔记包的 AI Persona 标识';
COMMENT ON COLUMN note_packages.style_family      IS '视觉风格族: watercolor/flat_vector/pixel_art/collage/minimal_line/pop_art';
COMMENT ON COLUMN note_packages.compliance_status IS '合规状态: pending/passed/failed/review_needed';
COMMENT ON COLUMN note_packages.ranking_score     IS '综合排名分 (0.0000–1.0000)';
COMMENT ON COLUMN note_packages.review_status     IS '人工审核状态';

-- --------------------------------------------------------------------------
-- 4.2 text_assets — Text components of a note package
-- --------------------------------------------------------------------------
CREATE TABLE text_assets (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    note_package_id UUID            NOT NULL REFERENCES note_packages(id) ON DELETE CASCADE,
    asset_role      text_asset_role NOT NULL,
    content         TEXT            NOT NULL,
    language        VARCHAR(10)     NOT NULL DEFAULT 'zh-CN',
    version         INT             NOT NULL DEFAULT 1,
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT now()
);

COMMENT ON TABLE  text_assets            IS '笔记包文本素材 (标题/正文/首评/话题/CTA/封面文字)';
COMMENT ON COLUMN text_assets.asset_role IS '文本角色: title/body/first_comment/hashtag/cta/cover_text';
COMMENT ON COLUMN text_assets.version    IS '版本号, 支持多版本对比';

-- --------------------------------------------------------------------------
-- 4.3 image_assets — Image components of a note package
-- --------------------------------------------------------------------------
CREATE TABLE image_assets (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    note_package_id UUID             NOT NULL REFERENCES note_packages(id) ON DELETE CASCADE,
    asset_role      image_asset_role NOT NULL,
    source_asset_id UUID             REFERENCES assets(id) ON DELETE SET NULL,
    derived_from    VARCHAR(128),
    prompt_version  VARCHAR(64),
    image_url       TEXT             NOT NULL,
    metadata_json   JSONB            NOT NULL DEFAULT '{}'::jsonb,
    created_at      TIMESTAMPTZ      NOT NULL DEFAULT now()
);

COMMENT ON TABLE  image_assets                IS '笔记包图片素材 (封面/轮播图)';
COMMENT ON COLUMN image_assets.source_asset_id IS '来源原始素材 (如产品图)';
COMMENT ON COLUMN image_assets.derived_from   IS '派生来源描述 (e.g. cartoon_composite)';
COMMENT ON COLUMN image_assets.prompt_version IS '生成所用 prompt 版本标识';

-- --------------------------------------------------------------------------
-- 4.4 briefs — Export briefs (聚光/蒲公英/标准导出)
-- --------------------------------------------------------------------------
CREATE TABLE briefs (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    note_package_id UUID        NOT NULL REFERENCES note_packages(id) ON DELETE CASCADE,
    brief_type      brief_type  NOT NULL,
    content_json    JSONB       NOT NULL DEFAULT '{}'::jsonb,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

COMMENT ON TABLE  briefs            IS '导出 Brief — 聚光投放包/蒲公英达人 Brief/标准导出';
COMMENT ON COLUMN briefs.brief_type IS 'note_export=标准导出, juguang=聚光, pugongying=蒲公英';


-- ============================================================================
-- 5. Metrics & Review
-- ============================================================================

-- --------------------------------------------------------------------------
-- 5.1 performance_metrics — Daily performance data per note package
-- --------------------------------------------------------------------------
CREATE TABLE performance_metrics (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    note_package_id UUID          NOT NULL REFERENCES note_packages(id) ON DELETE CASCADE,
    date            DATE          NOT NULL,
    impressions     INT           NOT NULL DEFAULT 0,
    clicks          INT           NOT NULL DEFAULT 0,
    saves           INT           NOT NULL DEFAULT 0,
    comments        INT           NOT NULL DEFAULT 0,
    cost            DECIMAL(12,2) NOT NULL DEFAULT 0,
    conversions     INT           NOT NULL DEFAULT 0,
    revenue         DECIMAL(12,2) NOT NULL DEFAULT 0,
    created_at      TIMESTAMPTZ   NOT NULL DEFAULT now(),

    CONSTRAINT perf_metrics_unique_pkg_date UNIQUE (note_package_id, date)
);

COMMENT ON TABLE  performance_metrics IS '笔记包每日效果数据 — 曝光/点击/收藏/评论/花费/转化/收入';

-- --------------------------------------------------------------------------
-- 5.2 review_events — Audit log of human review actions
-- --------------------------------------------------------------------------
CREATE TABLE review_events (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    note_package_id UUID          NOT NULL REFERENCES note_packages(id) ON DELETE CASCADE,
    reviewer_id     UUID          NOT NULL,
    action          review_action NOT NULL,
    reason          TEXT,
    created_at      TIMESTAMPTZ   NOT NULL DEFAULT now()
);

COMMENT ON TABLE  review_events        IS '审核事件日志 — 记录每次审核操作';
COMMENT ON COLUMN review_events.action IS 'approve/reject/request_revision/escalate';


-- ============================================================================
-- 6. Prompt & Policy Engine
-- ============================================================================

-- --------------------------------------------------------------------------
-- 6.1 prompt_versions — Versioned prompt templates
-- --------------------------------------------------------------------------
CREATE TABLE prompt_versions (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    prompt_family VARCHAR(128)  NOT NULL,
    version       INT           NOT NULL,
    template      TEXT          NOT NULL,
    variables     JSONB         NOT NULL DEFAULT '{}'::jsonb,
    status        prompt_status NOT NULL DEFAULT 'draft',
    created_at    TIMESTAMPTZ   NOT NULL DEFAULT now(),

    CONSTRAINT prompt_versions_family_version UNIQUE (prompt_family, version)
);

COMMENT ON TABLE  prompt_versions               IS 'Prompt 版本管理 — 按 family+version 追踪模板迭代';
COMMENT ON COLUMN prompt_versions.prompt_family IS 'Prompt 族标识 (e.g. xhs_title_gen, compliance_check)';
COMMENT ON COLUMN prompt_versions.variables     IS '模板变量定义 (JSON schema of expected vars)';

-- --------------------------------------------------------------------------
-- 6.2 policy_rules — Compliance & content policy rules
-- --------------------------------------------------------------------------
CREATE TABLE policy_rules (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    merchant_id  UUID             REFERENCES merchants(id) ON DELETE CASCADE,
    scope        policy_scope     NOT NULL DEFAULT 'global',
    rule_type    policy_rule_type NOT NULL,
    rule_payload JSONB            NOT NULL DEFAULT '{}'::jsonb,
    active       BOOLEAN          NOT NULL DEFAULT TRUE,
    created_at   TIMESTAMPTZ      NOT NULL DEFAULT now()
);

COMMENT ON TABLE  policy_rules              IS '合规/内容策略规则 — 全局或商家级';
COMMENT ON COLUMN policy_rules.merchant_id  IS 'NULL = 全局规则, 非 NULL = 商家专属规则';
COMMENT ON COLUMN policy_rules.scope        IS 'global=全局, merchant=商家, category=行业';
COMMENT ON COLUMN policy_rules.rule_payload IS '规则定义 (JSON), 结构取决于 rule_type';


-- ============================================================================
-- 7. Persona & Agent Team Tables
-- ============================================================================

-- --------------------------------------------------------------------------
-- 7.1 personas — AI agent personality definitions
-- --------------------------------------------------------------------------
CREATE TABLE personas (
    id                     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name                   VARCHAR(128) NOT NULL,
    description            TEXT,
    communication_style    VARCHAR(128),
    decision_style         VARCHAR(128),
    tone_rules_json        JSONB        NOT NULL DEFAULT '{}'::jsonb,
    forbidden_behaviors_json JSONB      NOT NULL DEFAULT '[]'::jsonb,
    version                INT          NOT NULL DEFAULT 1,
    active                 BOOLEAN      NOT NULL DEFAULT TRUE,
    created_at             TIMESTAMPTZ  NOT NULL DEFAULT now(),
    updated_at             TIMESTAMPTZ  NOT NULL DEFAULT now()
);

COMMENT ON TABLE  personas                         IS 'AI Persona 定义 — 人格/风格/行为约束';
COMMENT ON COLUMN personas.communication_style     IS '沟通风格 (e.g. 闺蜜聊天/专业测评)';
COMMENT ON COLUMN personas.decision_style          IS '决策风格 (e.g. data_driven/intuitive)';
COMMENT ON COLUMN personas.tone_rules_json         IS '语气规则 (JSON)';
COMMENT ON COLUMN personas.forbidden_behaviors_json IS '禁止行为列表 (JSON array)';

-- --------------------------------------------------------------------------
-- 7.2 persona_constraints — Fine-grained persona behaviour constraints
-- --------------------------------------------------------------------------
CREATE TABLE persona_constraints (
    id                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    persona_id         UUID        NOT NULL REFERENCES personas(id) ON DELETE CASCADE,
    constraint_type    VARCHAR(64) NOT NULL,
    constraint_payload JSONB       NOT NULL DEFAULT '{}'::jsonb,
    created_at         TIMESTAMPTZ NOT NULL DEFAULT now()
);

COMMENT ON TABLE persona_constraints IS 'Persona 行为约束 — 细粒度限制 (token budget, forbidden topics etc.)';

-- --------------------------------------------------------------------------
-- 7.3 agent_roles — Canonical roles an agent can fulfil
-- --------------------------------------------------------------------------
CREATE TABLE agent_roles (
    id                     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    role_key               VARCHAR(64)  NOT NULL UNIQUE,
    display_name           VARCHAR(128) NOT NULL,
    description            TEXT,
    required_output_schema JSONB        NOT NULL DEFAULT '{}'::jsonb,
    is_required_default    BOOLEAN      NOT NULL DEFAULT TRUE,
    created_at             TIMESTAMPTZ  NOT NULL DEFAULT now()
);

COMMENT ON TABLE  agent_roles          IS 'Agent 角色注册表 — 系统内置 + 商家自定义角色';
COMMENT ON COLUMN agent_roles.role_key IS '唯一角色标识 (e.g. xhs_note_writer)';
COMMENT ON COLUMN agent_roles.required_output_schema IS '角色输出的 JSON Schema';

-- --------------------------------------------------------------------------
-- 7.4 agent_teams — Named sets of agents assigned to a merchant
-- --------------------------------------------------------------------------
CREATE TABLE agent_teams (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    merchant_id UUID         REFERENCES merchants(id) ON DELETE SET NULL,
    team_name   VARCHAR(128) NOT NULL,
    description TEXT,
    version     INT          NOT NULL DEFAULT 1,
    active      BOOLEAN      NOT NULL DEFAULT TRUE,
    created_at  TIMESTAMPTZ  NOT NULL DEFAULT now(),
    updated_at  TIMESTAMPTZ  NOT NULL DEFAULT now()
);

COMMENT ON TABLE  agent_teams             IS 'Agent 团队 — 一组 Agent 角色+人格的组合';
COMMENT ON COLUMN agent_teams.merchant_id IS 'NULL = 系统默认团队, 非 NULL = 商家专属';

-- --------------------------------------------------------------------------
-- 7.5 agent_team_members — Role ↔ Persona binding within a team
-- --------------------------------------------------------------------------
CREATE TABLE agent_team_members (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    team_id     UUID    NOT NULL REFERENCES agent_teams(id) ON DELETE CASCADE,
    role_id     UUID    NOT NULL REFERENCES agent_roles(id) ON DELETE CASCADE,
    persona_id  UUID    NOT NULL REFERENCES personas(id) ON DELETE CASCADE,
    is_required BOOLEAN NOT NULL DEFAULT TRUE,
    ordering    INT     NOT NULL DEFAULT 0,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT team_role_unique UNIQUE (team_id, role_id)
);

COMMENT ON TABLE  agent_team_members IS 'Agent 团队成员 — 角色+人格在团队中的绑定';
COMMENT ON COLUMN agent_team_members.ordering IS '执行顺序 (越小越先)';

-- --------------------------------------------------------------------------
-- 7.6 agent_collaboration_edges — Directed interaction graph between roles
-- --------------------------------------------------------------------------
CREATE TABLE agent_collaboration_edges (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    team_id      UUID      NOT NULL REFERENCES agent_teams(id) ON DELETE CASCADE,
    from_role_id UUID      NOT NULL REFERENCES agent_roles(id) ON DELETE CASCADE,
    to_role_id   UUID      NOT NULL REFERENCES agent_roles(id) ON DELETE CASCADE,
    edge_type    edge_type NOT NULL,
    rule_json    JSONB     NOT NULL DEFAULT '{}'::jsonb,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT collab_edge_unique UNIQUE (team_id, from_role_id, to_role_id, edge_type),
    CONSTRAINT no_self_edge CHECK (from_role_id <> to_role_id)
);

COMMENT ON TABLE  agent_collaboration_edges           IS 'Agent 协作图边 — 描述角色间的委派/审核/辩论关系';
COMMENT ON COLUMN agent_collaboration_edges.edge_type IS 'delegates_to/reviews/escalates_to/debates_with';

-- --------------------------------------------------------------------------
-- 7.7 persona_experiments — A/B tests on team composition
-- --------------------------------------------------------------------------
CREATE TABLE persona_experiments (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    team_id         UUID              NOT NULL REFERENCES agent_teams(id) ON DELETE CASCADE,
    experiment_name VARCHAR(255)      NOT NULL,
    hypothesis      TEXT,
    status          experiment_status NOT NULL DEFAULT 'draft',
    result_summary  JSONB             NOT NULL DEFAULT '{}'::jsonb,
    created_at      TIMESTAMPTZ       NOT NULL DEFAULT now(),
    completed_at    TIMESTAMPTZ
);

COMMENT ON TABLE persona_experiments IS 'Persona 实验 — 团队组合的 A/B 测试';


-- ============================================================================
-- 8. Deferred Foreign Keys
-- ============================================================================
-- These FKs reference tables defined after the referencing table.

ALTER TABLE generation_jobs
    ADD CONSTRAINT fk_generation_jobs_team
    FOREIGN KEY (team_id) REFERENCES agent_teams(id) ON DELETE SET NULL;

ALTER TABLE generation_tasks
    ADD CONSTRAINT fk_generation_tasks_persona
    FOREIGN KEY (persona_id) REFERENCES personas(id) ON DELETE SET NULL;


-- ============================================================================
-- 9. Indexes
-- ============================================================================

-- merchants
CREATE INDEX idx_merchants_created_at ON merchants (created_at);

-- merchant_rules
CREATE INDEX idx_merchant_rules_merchant_id ON merchant_rules (merchant_id);

-- products
CREATE INDEX idx_products_merchant_id ON products (merchant_id);
CREATE INDEX idx_products_status      ON products (status);
CREATE INDEX idx_products_merchant_status ON products (merchant_id, status);

-- asset_packs
CREATE INDEX idx_asset_packs_merchant_id ON asset_packs (merchant_id);
CREATE INDEX idx_asset_packs_status      ON asset_packs (status);
CREATE INDEX idx_asset_packs_quarter     ON asset_packs (merchant_id, quarter_label);

-- assets
CREATE INDEX idx_assets_asset_pack_id    ON assets (asset_pack_id);
CREATE INDEX idx_assets_product_id       ON assets (product_id);
CREATE INDEX idx_assets_approval_status  ON assets (approval_status);

-- generation_jobs
CREATE INDEX idx_gen_jobs_merchant_id ON generation_jobs (merchant_id);
CREATE INDEX idx_gen_jobs_status      ON generation_jobs (status);
CREATE INDEX idx_gen_jobs_created_at  ON generation_jobs (created_at);
CREATE INDEX idx_gen_jobs_team_id     ON generation_jobs (team_id);

-- generation_tasks
CREATE INDEX idx_gen_tasks_job_id     ON generation_tasks (job_id);
CREATE INDEX idx_gen_tasks_status     ON generation_tasks (status);
CREATE INDEX idx_gen_tasks_persona_id ON generation_tasks (persona_id);

-- note_packages
CREATE INDEX idx_note_pkgs_merchant_id       ON note_packages (merchant_id);
CREATE INDEX idx_note_pkgs_product_id        ON note_packages (product_id);
CREATE INDEX idx_note_pkgs_asset_pack_id     ON note_packages (asset_pack_id);
CREATE INDEX idx_note_pkgs_gen_job_id        ON note_packages (generation_job_id);
CREATE INDEX idx_note_pkgs_compliance        ON note_packages (compliance_status);
CREATE INDEX idx_note_pkgs_review_status     ON note_packages (review_status);
CREATE INDEX idx_note_pkgs_created_at        ON note_packages (created_at);
CREATE INDEX idx_note_pkgs_merchant_review   ON note_packages (merchant_id, review_status);
CREATE INDEX idx_note_pkgs_ranking           ON note_packages (merchant_id, ranking_score DESC NULLS LAST);

-- text_assets
CREATE INDEX idx_text_assets_note_pkg_id ON text_assets (note_package_id);
CREATE INDEX idx_text_assets_role        ON text_assets (asset_role);

-- image_assets
CREATE INDEX idx_image_assets_note_pkg_id  ON image_assets (note_package_id);
CREATE INDEX idx_image_assets_source_asset ON image_assets (source_asset_id);

-- briefs
CREATE INDEX idx_briefs_note_pkg_id ON briefs (note_package_id);
CREATE INDEX idx_briefs_type        ON briefs (brief_type);

-- performance_metrics
CREATE INDEX idx_perf_metrics_note_pkg_id ON performance_metrics (note_package_id);
CREATE INDEX idx_perf_metrics_date        ON performance_metrics (date);

-- review_events
CREATE INDEX idx_review_events_note_pkg_id ON review_events (note_package_id);
CREATE INDEX idx_review_events_reviewer    ON review_events (reviewer_id);
CREATE INDEX idx_review_events_created_at  ON review_events (created_at);

-- prompt_versions
CREATE INDEX idx_prompt_versions_family ON prompt_versions (prompt_family);
CREATE INDEX idx_prompt_versions_status ON prompt_versions (status);

-- policy_rules
CREATE INDEX idx_policy_rules_merchant_id ON policy_rules (merchant_id);
CREATE INDEX idx_policy_rules_scope       ON policy_rules (scope);
CREATE INDEX idx_policy_rules_active      ON policy_rules (active) WHERE active = TRUE;

-- personas
CREATE INDEX idx_personas_active ON personas (active) WHERE active = TRUE;

-- persona_constraints
CREATE INDEX idx_persona_constraints_persona_id ON persona_constraints (persona_id);

-- agent_teams
CREATE INDEX idx_agent_teams_merchant_id ON agent_teams (merchant_id);
CREATE INDEX idx_agent_teams_active      ON agent_teams (active) WHERE active = TRUE;

-- agent_team_members
CREATE INDEX idx_team_members_team_id    ON agent_team_members (team_id);
CREATE INDEX idx_team_members_role_id    ON agent_team_members (role_id);
CREATE INDEX idx_team_members_persona_id ON agent_team_members (persona_id);

-- agent_collaboration_edges
CREATE INDEX idx_collab_edges_team_id      ON agent_collaboration_edges (team_id);
CREATE INDEX idx_collab_edges_from_role_id ON agent_collaboration_edges (from_role_id);
CREATE INDEX idx_collab_edges_to_role_id   ON agent_collaboration_edges (to_role_id);

-- persona_experiments
CREATE INDEX idx_persona_exp_team_id ON persona_experiments (team_id);
CREATE INDEX idx_persona_exp_status  ON persona_experiments (status);


-- ============================================================================
-- 10. Seed Data — Standard Agent Roles
-- ============================================================================

INSERT INTO agent_roles (role_key, display_name, description, required_output_schema, is_required_default) VALUES
(
    'founder_copilot',
    '创始人副驾',
    'Top-level orchestrator that translates merchant intent into structured generation briefs. Owns the conversation loop in AI Chat mode.',
    '{"type":"object","properties":{"brief":{"type":"object"},"clarifications":{"type":"array"}}}'::jsonb,
    TRUE
),
(
    'strategy_planner',
    '策略规划师',
    'Analyses market trends, competitor content, and performance history to recommend angles, hooks, and audience targeting for each generation batch.',
    '{"type":"object","properties":{"angles":{"type":"array"},"target_audience":{"type":"object"},"hooks":{"type":"array"}}}'::jsonb,
    TRUE
),
(
    'xhs_note_writer',
    '小红书文案专家',
    'Generates XiaoHongShu-native titles, body copy, first comments, hashtags, and CTAs. Fluent in platform vernacular and trending formats.',
    '{"type":"object","properties":{"titles":{"type":"array"},"bodies":{"type":"array"},"first_comment":{"type":"string"},"hashtags":{"type":"array"}}}'::jsonb,
    TRUE
),
(
    'cartoon_visual_designer',
    '卡通视觉设计师',
    'Plans cartoon/illustration scene contexts and composites real product photography. Selects style families and directs image generation prompts.',
    '{"type":"object","properties":{"style_family":{"type":"string"},"composition":{"type":"object"},"prompts":{"type":"array"}}}'::jsonb,
    TRUE
),
(
    'compliance_reviewer',
    '合规审查员',
    'Runs three-layer compliance checks (deterministic rules, model classifiers, policy rules) and flags violations before content enters the review queue.',
    '{"type":"object","properties":{"layer_1":{"type":"string"},"layer_2":{"type":"string"},"flags":{"type":"array"},"overall":{"type":"string"}}}'::jsonb,
    TRUE
),
(
    'ranking_analyst',
    '排名分析师',
    'Scores note packages using predicted engagement, style diversity, and brand alignment signals. Orders daily slates by composite ranking.',
    '{"type":"object","properties":{"predicted_engagement":{"type":"number"},"diversity_score":{"type":"number"},"brand_alignment":{"type":"number"},"composite":{"type":"number"}}}'::jsonb,
    TRUE
),
(
    'ops_exporter',
    '运营导出员',
    'Packages approved note packages into platform-specific export formats: 聚光 ad units, 蒲公英 creator briefs, and standard note exports.',
    '{"type":"object","properties":{"export_type":{"type":"string"},"payload":{"type":"object"},"validation_passed":{"type":"boolean"}}}'::jsonb,
    TRUE
),
(
    'learning_analyst',
    '学习分析师',
    'Ingests performance data and review feedback to update strategy weights, style preferences, and prompt effectiveness scores over time.',
    '{"type":"object","properties":{"insights":{"type":"array"},"weight_updates":{"type":"object"},"recommendations":{"type":"array"}}}'::jsonb,
    FALSE
);


-- ============================================================================
-- 11. Updated-at Trigger (utility)
-- ============================================================================
-- Automatically maintain updated_at on tables that carry it.

CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_merchants_updated_at      BEFORE UPDATE ON merchants       FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER trg_merchant_rules_updated_at  BEFORE UPDATE ON merchant_rules  FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER trg_products_updated_at        BEFORE UPDATE ON products        FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER trg_asset_packs_updated_at     BEFORE UPDATE ON asset_packs     FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER trg_note_packages_updated_at   BEFORE UPDATE ON note_packages   FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER trg_personas_updated_at        BEFORE UPDATE ON personas        FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER trg_agent_teams_updated_at     BEFORE UPDATE ON agent_teams     FOR EACH ROW EXECUTE FUNCTION set_updated_at();

COMMIT;
