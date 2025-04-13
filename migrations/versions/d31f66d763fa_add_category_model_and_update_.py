"""Add Category model and update relationships

Revision ID: d31f66d763fa
Revises: 682fa60ea438
Create Date: 2024-03-19 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd31f66d763fa'
down_revision = '682fa60ea438'
branch_labels = None
depends_on = None


def upgrade():
    # Category tablosunu oluştur
    op.create_table('category',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=64), nullable=False),
        sa.Column('type', sa.String(length=10), nullable=False),
        sa.PrimaryKeyConstraint('id', name='pk_category'),
        sa.UniqueConstraint('name', name='uq_category_name')
    )

    # Budget tablosunu güncelle
    with op.batch_alter_table('budget', schema=None) as batch_op:
        batch_op.add_column(sa.Column('spent_amount', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('category_id', sa.Integer(), nullable=True))
        batch_op.alter_column('period', type_=sa.String(length=10))
        batch_op.alter_column('start_date', type_=sa.DateTime())
        batch_op.alter_column('end_date', type_=sa.DateTime())
        batch_op.drop_column('updated_at')
        batch_op.drop_column('category')
        batch_op.drop_column('created_at')
        batch_op.create_foreign_key('fk_budget_category', 'category', ['category_id'], ['id'])

    # Goal tablosunu güncelle
    with op.batch_alter_table('goal', schema=None) as batch_op:
        batch_op.add_column(sa.Column('is_completed', sa.Boolean(), nullable=True))
        batch_op.alter_column('description', type_=sa.String(length=200))
        batch_op.alter_column('deadline', type_=sa.DateTime())
        batch_op.drop_column('updated_at')
        batch_op.drop_column('status')
        batch_op.drop_column('created_at')

    # Transaction tablosunu güncelle
    with op.batch_alter_table('transaction', schema=None) as batch_op:
        batch_op.add_column(sa.Column('category_id', sa.Integer(), nullable=True))
        batch_op.alter_column('date', nullable=False)
        batch_op.drop_column('category')
        batch_op.create_foreign_key('fk_transaction_category', 'category', ['category_id'], ['id'])


def downgrade():
    # Transaction tablosunu eski haline getir
    with op.batch_alter_table('transaction', schema=None) as batch_op:
        batch_op.drop_constraint('fk_transaction_category', type_='foreignkey')
        batch_op.add_column(sa.Column('category', sa.String(length=50), nullable=True))
        batch_op.drop_column('category_id')
        batch_op.alter_column('date', nullable=True)

    # Goal tablosunu eski haline getir
    with op.batch_alter_table('goal', schema=None) as batch_op:
        batch_op.add_column(sa.Column('created_at', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('status', sa.String(length=20), nullable=True))
        batch_op.add_column(sa.Column('updated_at', sa.DateTime(), nullable=True))
        batch_op.alter_column('deadline', type_=sa.Date())
        batch_op.alter_column('description', type_=sa.Text())
        batch_op.drop_column('is_completed')

    # Budget tablosunu eski haline getir
    with op.batch_alter_table('budget', schema=None) as batch_op:
        batch_op.drop_constraint('fk_budget_category', type_='foreignkey')
        batch_op.add_column(sa.Column('created_at', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('category', sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column('updated_at', sa.DateTime(), nullable=True))
        batch_op.alter_column('end_date', type_=sa.Date())
        batch_op.alter_column('start_date', type_=sa.Date())
        batch_op.alter_column('period', type_=sa.String(length=20))
        batch_op.drop_column('category_id')
        batch_op.drop_column('spent_amount')

    # Category tablosunu sil
    op.drop_table('category')
