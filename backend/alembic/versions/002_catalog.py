"""catalog domain (phase 1)
Revision ID: 002_catalog
Revises: 001
"""
revision="002_catalog"; down_revision="001"; branch_labels=None; depends_on=None
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
def _t(name, *cols): op.create_table(name, sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True), *cols)
def upgrade():
    _t("products", sa.Column("title",sa.String()), sa.Column("brand",sa.String()), sa.Column("model",sa.String()), sa.Column("gtin",sa.String()), sa.Column("asin",sa.String()), sa.Column("mpn",sa.String()), sa.Column("category",sa.String()), sa.Column("attributes",sa.JSON()), sa.Column("image",sa.String()), sa.Column("created_at",sa.DateTime(timezone=True), server_default=sa.func.now()))
    _t("sellers", sa.Column("connector",sa.String()), sa.Column("name",sa.String()), sa.Column("rating",sa.Float()), sa.Column("feedback_count",sa.Integer()), sa.Column("age_years",sa.Float()), sa.Column("official_store",sa.Boolean()), sa.Column("return_rate",sa.Float()))
    _t("offers", sa.Column("product_id",postgresql.UUID(as_uuid=True)), sa.Column("seller_id",postgresql.UUID(as_uuid=True)), sa.Column("connector",sa.String()), sa.Column("title",sa.String()), sa.Column("url",sa.Text()), sa.Column("price",sa.Float()), sa.Column("currency",sa.String()), sa.Column("shipping_price",sa.Float()), sa.Column("availability",sa.String()), sa.Column("stock_qty",sa.Integer()), sa.Column("delivery_days",sa.Integer()), sa.Column("rating",sa.Float()), sa.Column("review_count",sa.Integer()), sa.Column("condition",sa.String()), sa.Column("quality_score",sa.Float()), sa.Column("last_verified_at",sa.DateTime(timezone=True), server_default=sa.func.now()), sa.Column("raw",sa.JSON()))
    _t("price_history", sa.Column("product_id",postgresql.UUID(as_uuid=True)), sa.Column("connector",sa.String()), sa.Column("country",sa.String()), sa.Column("price",sa.Float()), sa.Column("currency",sa.String()), sa.Column("landed_total",sa.Float()), sa.Column("recorded_at",sa.DateTime(timezone=True), server_default=sa.func.now()))
    _t("watchlist_items", sa.Column("user_id",postgresql.UUID(as_uuid=True)), sa.Column("product_id",postgresql.UUID(as_uuid=True)), sa.Column("target_price",sa.Float()), sa.Column("currency",sa.String()), sa.Column("created_at",sa.DateTime(timezone=True), server_default=sa.func.now()))
    _t("alerts", sa.Column("user_id",postgresql.UUID(as_uuid=True)), sa.Column("product_id",postgresql.UUID(as_uuid=True)), sa.Column("kind",sa.String()), sa.Column("target_price",sa.Float()), sa.Column("channel",sa.String()), sa.Column("destination",sa.String()), sa.Column("active",sa.Boolean()), sa.Column("last_fired_at",sa.DateTime(timezone=True)))
    _t("saved_searches", sa.Column("user_id",postgresql.UUID(as_uuid=True)), sa.Column("query",sa.String()), sa.Column("filters",sa.JSON()), sa.Column("created_at",sa.DateTime(timezone=True), server_default=sa.func.now()))
    _t("fx_rates", sa.Column("base",sa.String()), sa.Column("rates",sa.JSON()), sa.Column("fetched_at",sa.DateTime(timezone=True), server_default=sa.func.now()), sa.Column("stale",sa.Boolean()))
    _t("tax_rules", sa.Column("country",sa.String()), sa.Column("kind",sa.String()), sa.Column("category",sa.String()), sa.Column("rate",sa.Float()), sa.Column("version",sa.String()), sa.Column("label",sa.String()))
    _t("api_keys", sa.Column("user_id",postgresql.UUID(as_uuid=True)), sa.Column("key_hash",sa.String(), unique=True), sa.Column("name",sa.String()), sa.Column("active",sa.Boolean()), sa.Column("usage_count",sa.Integer()), sa.Column("created_at",sa.DateTime(timezone=True), server_default=sa.func.now()))
    _t("connector_health", sa.Column("connector",sa.String(), unique=True), sa.Column("enabled",sa.Boolean()), sa.Column("successes",sa.Integer()), sa.Column("failures",sa.Integer()), sa.Column("blocks",sa.Integer()), sa.Column("avg_latency_ms",sa.Float()), sa.Column("drift_suspected",sa.Boolean()), sa.Column("last_error",sa.Text()), sa.Column("updated_at",sa.DateTime(timezone=True), server_default=sa.func.now()))
    _t("match_feedback", sa.Column("product_title",sa.String()), sa.Column("offer_url",sa.Text()), sa.Column("reason",sa.Text()), sa.Column("created_at",sa.DateTime(timezone=True), server_default=sa.func.now()))
def downgrade():
    for t in ["match_feedback","connector_health","api_keys","tax_rules","fx_rates","saved_searches","alerts","watchlist_items","price_history","offers","sellers","products"]: op.drop_table(t)
