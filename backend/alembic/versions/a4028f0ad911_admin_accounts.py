"""Account approval and platform administration.

Revision ID: a4028f0ad911
Revises: 8aaa48b081f8
"""
from alembic import op
import sqlalchemy as sa

revision = "a4028f0ad911"
down_revision = "8aaa48b081f8"
branch_labels = None
depends_on = None


def upgrade():
    # Preserve existing accounts. Only new registrations enter PENDING.
    op.add_column("users", sa.Column("is_admin", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column("users", sa.Column("account_status", sa.String(16), nullable=False, server_default="APPROVED"))
    op.add_column("users", sa.Column("review_reason", sa.String(1000), nullable=False, server_default=""))
    op.add_column("users", sa.Column("email_verified", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.create_table(
        "account_reviews",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("actor_user_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("target_user_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("previous_status", sa.String(16), nullable=False),
        sa.Column("new_status", sa.String(16), nullable=False),
        sa.Column("reason", sa.String(1000), nullable=False),
    )
    op.create_index("ix_account_reviews_actor_user_id", "account_reviews", ["actor_user_id"])
    op.create_index("ix_account_reviews_target_user_id", "account_reviews", ["target_user_id"])


def downgrade():
    op.drop_table("account_reviews")
    op.drop_column("users", "email_verified")
    op.drop_column("users", "review_reason")
    op.drop_column("users", "account_status")
    op.drop_column("users", "is_admin")
