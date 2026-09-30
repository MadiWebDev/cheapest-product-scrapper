"""Initial schema migration

Revision ID: 001_initial_schema
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('plan', sa.Enum('free', 'pro', 'business', 'enterprise', name='planenum'), nullable=False),
        sa.Column('searches_this_month', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False)
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)

    # Create suppliers table
    op.create_table(
        'suppliers',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('country_code', sa.String(length=2), nullable=False),
        sa.Column('categories', postgresql.ARRAY(sa.String()), nullable=False),
        sa.Column('min_order_qty', sa.Integer(), nullable=False),
        sa.Column('price_usd_per_unit', sa.Float(), nullable=False),
        sa.Column('trust_score', sa.Float(), nullable=False),
        sa.Column('verified', sa.Boolean(), nullable=False),
        sa.Column('website_url', sa.String(), nullable=False),
        sa.Column('contact_email', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('embedding', postgresql.VECTOR(1536), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False)
    )
    op.create_index(op.f('ix_suppliers_country_code'), 'suppliers', ['country_code'], unique=False)
    op.create_index(op.f('ix_suppliers_id'), 'suppliers', ['id'], unique=False)
    op.create_index(op.f('ix_suppliers_name'), 'suppliers', ['name'], unique=False)

    # Create searches table
    op.create_table(
        'searches',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('image_s3_key', sa.String(), nullable=False),
        sa.Column('image_expires_at', sa.DateTime(), nullable=False),
        sa.Column('detected_category', sa.String(), nullable=True),
        sa.Column('detected_attributes', postgresql.JSON(), nullable=True),
        sa.Column('confidence_score', sa.Float(), nullable=True),
        sa.Column('filters_applied', postgresql.JSON(), nullable=True),
        sa.Column('result_supplier_ids', postgresql.ARRAY(postgresql.UUID(as_uuid=True)), nullable=True),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('error_message', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE')
    )
    op.create_index(op.f('ix_searches_id'), 'searches', ['id'], unique=False)

    # Create saved_suppliers table
    op.create_table(
        'saved_suppliers',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('supplier_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['supplier_id'], ['suppliers.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE')
    )
    op.create_index(op.f('ix_saved_suppliers_id'), 'saved_suppliers', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_saved_suppliers_id'), table_name='saved_suppliers')
    op.drop_table('saved_suppliers')
    
    op.drop_index(op.f('ix_searches_id'), table_name='searches')
    op.drop_table('searches')
    
    op.drop_index(op.f('ix_suppliers_name'), table_name='suppliers')
    op.drop_index(op.f('ix_suppliers_id'), table_name='suppliers')
    op.drop_index(op.f('ix_suppliers_country_code'), table_name='suppliers')
    op.drop_table('suppliers')
    
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
    
    op.execute('DROP TYPE IF EXISTS planenum')
