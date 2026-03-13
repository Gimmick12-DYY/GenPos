"""Seed 意睡眠 Easysleep merchant (only if no merchants exist)

Revision ID: 002
Revises: 001
Create Date: 2026-03-13

Inserts the default merchant and rules so the app works after first deploy
without calling POST /auth/bootstrap.
"""
from typing import Sequence, Union

from alembic import op

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Fixed UUID so we can reference it for merchant_rules (idempotent seed)
SEED_MERCHANT_ID = "a0000001-0001-4000-8000-000000000001"


def upgrade() -> None:
    # Insert 意睡眠 Easysleep merchant only when no merchants exist
    op.execute(
        f"""
        INSERT INTO merchants (id, name, industry, xhs_account_type, uses_juguang, uses_pugongying, language, timezone)
        SELECT '{SEED_MERCHANT_ID}', '意睡眠 Easysleep', '家居', 'professional', false, false, 'zh-CN', 'Asia/Shanghai'
        WHERE NOT EXISTS (SELECT 1 FROM merchants LIMIT 1)
        """
    )
    # Insert default rules for that merchant (only if our merchant exists and has no rules yet)
    op.execute(
        f"""
        INSERT INTO merchant_rules (id, merchant_id, compliance_level, review_mode)
        SELECT gen_random_uuid(), '{SEED_MERCHANT_ID}', 'standard', 'all'
        WHERE EXISTS (SELECT 1 FROM merchants WHERE id = '{SEED_MERCHANT_ID}'::uuid)
          AND NOT EXISTS (SELECT 1 FROM merchant_rules WHERE merchant_id = '{SEED_MERCHANT_ID}'::uuid)
        """
    )


def downgrade() -> None:
    op.execute(f"DELETE FROM merchant_rules WHERE merchant_id = '{SEED_MERCHANT_ID}'::uuid")
    op.execute(f"DELETE FROM merchants WHERE id = '{SEED_MERCHANT_ID}'::uuid")
