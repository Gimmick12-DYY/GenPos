"""Initial schema — all 22 tables

Revision ID: 001
Revises: None
Create Date: 2026-03-13

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSON, UUID

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- merchants ---
    op.create_table(
        "merchants",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.String(255), nullable=False, index=True),
        sa.Column("industry", sa.String(128), nullable=False, index=True),
        sa.Column("xhs_account_type", sa.String(64), nullable=False),
        sa.Column("uses_juguang", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.Column("uses_pugongying", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.Column("language", sa.String(10), nullable=False, server_default="zh-CN"),
        sa.Column("timezone", sa.String(64), nullable=False, server_default="Asia/Shanghai"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # --- merchant_rules ---
    op.create_table(
        "merchant_rules",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column(
            "merchant_id",
            UUID(as_uuid=True),
            sa.ForeignKey("merchants.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
            index=True,
        ),
        sa.Column("tone_preset", sa.String(64), nullable=True),
        sa.Column("banned_words", JSON, nullable=True),
        sa.Column("required_claims", JSON, nullable=True),
        sa.Column("banned_claims", JSON, nullable=True),
        sa.Column("compliance_level", sa.String(16), nullable=False, server_default="standard"),
        sa.Column("review_mode", sa.String(16), nullable=False, server_default="all"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # --- products ---
    op.create_table(
        "products",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column(
            "merchant_id",
            UUID(as_uuid=True),
            sa.ForeignKey("merchants.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("name", sa.String(255), nullable=False, index=True),
        sa.Column("category", sa.String(128), nullable=False, index=True),
        sa.Column("status", sa.String(16), nullable=False, server_default="active"),
        sa.Column("primary_objective", sa.String(64), nullable=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # --- asset_packs ---
    op.create_table(
        "asset_packs",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column(
            "merchant_id",
            UUID(as_uuid=True),
            sa.ForeignKey("merchants.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("quarter_label", sa.String(16), nullable=False),
        sa.Column("status", sa.String(24), nullable=False, server_default="draft"),
        sa.Column("effective_from", sa.Date, nullable=True),
        sa.Column("effective_to", sa.Date, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # --- assets ---
    op.create_table(
        "assets",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column(
            "asset_pack_id",
            UUID(as_uuid=True),
            sa.ForeignKey("asset_packs.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "product_id",
            UUID(as_uuid=True),
            sa.ForeignKey("products.id", ondelete="SET NULL"),
            nullable=True,
            index=True,
        ),
        sa.Column("type", sa.String(24), nullable=False),
        sa.Column("storage_url", sa.Text, nullable=False),
        sa.Column("checksum", sa.String(128), nullable=True),
        sa.Column("width", sa.Integer, nullable=True),
        sa.Column("height", sa.Integer, nullable=True),
        sa.Column("metadata_json", JSON, nullable=True),
        sa.Column("approval_status", sa.String(16), nullable=False, server_default="pending"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # --- personas ---
    op.create_table(
        "personas",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("communication_style", sa.String(128), nullable=True),
        sa.Column("decision_style", sa.String(128), nullable=True),
        sa.Column("tone_rules_json", JSON, nullable=True),
        sa.Column("forbidden_behaviors_json", JSON, nullable=True),
        sa.Column("version", sa.Integer, nullable=False, server_default="1"),
        sa.Column("active", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # --- persona_constraints ---
    op.create_table(
        "persona_constraints",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column(
            "persona_id",
            UUID(as_uuid=True),
            sa.ForeignKey("personas.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("constraint_type", sa.String(64), nullable=False),
        sa.Column("constraint_payload", JSON, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # --- agent_roles ---
    op.create_table(
        "agent_roles",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("role_key", sa.String(64), nullable=False, unique=True),
        sa.Column("display_name", sa.String(128), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("required_output_schema", JSON, nullable=True),
        sa.Column("is_required_default", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # --- agent_teams ---
    op.create_table(
        "agent_teams",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column(
            "merchant_id",
            UUID(as_uuid=True),
            sa.ForeignKey("merchants.id", ondelete="CASCADE"),
            nullable=True,
            index=True,
        ),
        sa.Column("team_name", sa.String(128), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("version", sa.Integer, nullable=False, server_default="1"),
        sa.Column("active", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # --- agent_team_members ---
    op.create_table(
        "agent_team_members",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column(
            "team_id",
            UUID(as_uuid=True),
            sa.ForeignKey("agent_teams.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "role_id",
            UUID(as_uuid=True),
            sa.ForeignKey("agent_roles.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "persona_id",
            UUID(as_uuid=True),
            sa.ForeignKey("personas.id", ondelete="SET NULL"),
            nullable=True,
            index=True,
        ),
        sa.Column("is_required", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("ordering", sa.Integer, nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("team_id", "role_id", name="uq_team_role"),
    )

    # --- agent_collaboration_edges ---
    op.create_table(
        "agent_collaboration_edges",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column(
            "team_id",
            UUID(as_uuid=True),
            sa.ForeignKey("agent_teams.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "from_role_id", UUID(as_uuid=True), sa.ForeignKey("agent_roles.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column(
            "to_role_id", UUID(as_uuid=True), sa.ForeignKey("agent_roles.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("edge_type", sa.String(24), nullable=False),
        sa.Column("rule_json", JSON, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("from_role_id != to_role_id", name="ck_no_self_edge"),
    )

    # --- persona_experiments ---
    op.create_table(
        "persona_experiments",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column(
            "team_id",
            UUID(as_uuid=True),
            sa.ForeignKey("agent_teams.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("experiment_name", sa.String(255), nullable=False),
        sa.Column("hypothesis", sa.Text, nullable=True),
        sa.Column("status", sa.String(24), nullable=False, server_default="draft"),
        sa.Column("result_summary", JSON, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
    )

    # --- generation_jobs ---
    op.create_table(
        "generation_jobs",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column(
            "merchant_id",
            UUID(as_uuid=True),
            sa.ForeignKey("merchants.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("source_mode", sa.String(24), nullable=False),
        sa.Column("trigger_type", sa.String(24), nullable=False),
        sa.Column("status", sa.String(24), nullable=False, server_default="pending"),
        sa.Column("team_id", UUID(as_uuid=True), sa.ForeignKey("agent_teams.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
    )

    # --- generation_tasks ---
    op.create_table(
        "generation_tasks",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column(
            "job_id",
            UUID(as_uuid=True),
            sa.ForeignKey("generation_jobs.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("task_type", sa.String(24), nullable=False),
        sa.Column("input_json", JSON, nullable=True),
        sa.Column("output_json", JSON, nullable=True),
        sa.Column("status", sa.String(24), nullable=False, server_default="pending"),
        sa.Column("agent_role", sa.String(64), nullable=True),
        sa.Column("persona_id", UUID(as_uuid=True), sa.ForeignKey("personas.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
    )

    # --- note_packages ---
    op.create_table(
        "note_packages",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column(
            "merchant_id",
            UUID(as_uuid=True),
            sa.ForeignKey("merchants.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "product_id",
            UUID(as_uuid=True),
            sa.ForeignKey("products.id", ondelete="SET NULL"),
            nullable=True,
            index=True,
        ),
        sa.Column(
            "asset_pack_id", UUID(as_uuid=True), sa.ForeignKey("asset_packs.id", ondelete="SET NULL"), nullable=True
        ),
        sa.Column(
            "generation_job_id",
            UUID(as_uuid=True),
            sa.ForeignKey("generation_jobs.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("source_mode", sa.String(24), nullable=False),
        sa.Column("objective", sa.String(24), nullable=False, server_default="seeding"),
        sa.Column("persona", sa.String(255), nullable=True),
        sa.Column("style_family", sa.String(128), nullable=True),
        sa.Column("compliance_status", sa.String(24), nullable=False, server_default="pending"),
        sa.Column("ranking_score", sa.Numeric(5, 4), nullable=True),
        sa.Column("review_status", sa.String(24), nullable=False, server_default="pending"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # --- text_assets ---
    op.create_table(
        "text_assets",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column(
            "note_package_id",
            UUID(as_uuid=True),
            sa.ForeignKey("note_packages.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("asset_role", sa.String(24), nullable=False),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("language", sa.String(10), nullable=False, server_default="zh-CN"),
        sa.Column("version", sa.Integer, nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # --- image_assets ---
    op.create_table(
        "image_assets",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column(
            "note_package_id",
            UUID(as_uuid=True),
            sa.ForeignKey("note_packages.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("asset_role", sa.String(24), nullable=False),
        sa.Column(
            "source_asset_id", UUID(as_uuid=True), sa.ForeignKey("assets.id", ondelete="SET NULL"), nullable=True
        ),
        sa.Column("derived_from", sa.String(255), nullable=True),
        sa.Column("prompt_version", sa.String(64), nullable=True),
        sa.Column("image_url", sa.Text, nullable=True),
        sa.Column("metadata_json", JSON, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # --- briefs ---
    op.create_table(
        "briefs",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column(
            "note_package_id",
            UUID(as_uuid=True),
            sa.ForeignKey("note_packages.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("brief_type", sa.String(24), nullable=False),
        sa.Column("content_json", JSON, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # --- performance_metrics ---
    op.create_table(
        "performance_metrics",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column(
            "note_package_id",
            UUID(as_uuid=True),
            sa.ForeignKey("note_packages.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("date", sa.Date, nullable=False),
        sa.Column("impressions", sa.Integer, nullable=False, server_default="0"),
        sa.Column("clicks", sa.Integer, nullable=False, server_default="0"),
        sa.Column("saves", sa.Integer, nullable=False, server_default="0"),
        sa.Column("comments", sa.Integer, nullable=False, server_default="0"),
        sa.Column("cost", sa.Numeric(12, 2), nullable=False, server_default="0"),
        sa.Column("conversions", sa.Integer, nullable=False, server_default="0"),
        sa.Column("revenue", sa.Numeric(12, 2), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("note_package_id", "date", name="uq_metrics_package_date"),
    )

    # --- review_events ---
    op.create_table(
        "review_events",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column(
            "note_package_id",
            UUID(as_uuid=True),
            sa.ForeignKey("note_packages.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("reviewer_id", UUID(as_uuid=True), nullable=True),
        sa.Column("action", sa.String(24), nullable=False),
        sa.Column("reason", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # --- prompt_versions ---
    op.create_table(
        "prompt_versions",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("prompt_family", sa.String(64), nullable=False),
        sa.Column("version", sa.Integer, nullable=False),
        sa.Column("template", sa.Text, nullable=False),
        sa.Column("variables", JSON, nullable=True),
        sa.Column("status", sa.String(16), nullable=False, server_default="draft"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("prompt_family", "version", name="uq_prompt_family_version"),
    )

    # --- policy_rules ---
    op.create_table(
        "policy_rules",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column(
            "merchant_id",
            UUID(as_uuid=True),
            sa.ForeignKey("merchants.id", ondelete="CASCADE"),
            nullable=True,
            index=True,
        ),
        sa.Column("scope", sa.String(16), nullable=False),
        sa.Column("rule_type", sa.String(32), nullable=False),
        sa.Column("rule_payload", JSON, nullable=True),
        sa.Column("active", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # --- Seed agent_roles ---
    op.execute("""
        INSERT INTO agent_roles (role_key, display_name, description, is_required_default) VALUES
        ('founder_copilot',        'Founder Copilot',         'Interprets merchant requests and produces structured jobs',          true),
        ('strategy_planner',       'Strategy Planner',        'Creates creative strategy plans with angles and style direction',    true),
        ('xhs_note_writer',        'XHS Note Writer',         'Writes XiaoHongShu-native titles, bodies, hashtags, and CTAs',      true),
        ('cartoon_visual_designer', 'Cartoon Visual Designer', 'Designs cartoon scene briefs preserving real product fidelity',     true),
        ('compliance_reviewer',    'Compliance Reviewer',     'Checks content against ad law, platform rules, and brand rules',    true),
        ('ranking_analyst',        'Ranking Analyst',         'Scores and ranks note package candidates',                          true),
        ('ops_exporter',           'Export / Ops Agent',      'Packages outputs into note-ready and paid-ready bundles',            true),
        ('learning_analyst',       'Learning Analyst',        'Analyzes performance data and recommends generation changes',        true)
    """)


def downgrade() -> None:
    tables = [
        "policy_rules",
        "prompt_versions",
        "review_events",
        "performance_metrics",
        "briefs",
        "image_assets",
        "text_assets",
        "note_packages",
        "generation_tasks",
        "generation_jobs",
        "persona_experiments",
        "agent_collaboration_edges",
        "agent_team_members",
        "agent_teams",
        "agent_roles",
        "persona_constraints",
        "personas",
        "assets",
        "asset_packs",
        "products",
        "merchant_rules",
        "merchants",
    ]
    for table in tables:
        op.drop_table(table)
