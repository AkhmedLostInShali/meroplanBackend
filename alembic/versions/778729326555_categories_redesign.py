"""categories redesign

Revision ID: 778729326555
Revises: 23fa464b1923
Create Date: 2023-11-04 17:39:11.402132

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '778729326555'
down_revision = '23fa464b1923'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('events', schema=None) as batch_op:
        batch_op.add_column(sa.Column('category_id', sa.Integer(), nullable=True))
        batch_op.drop_constraint('events_ibfk_2', type_='foreignkey')
        batch_op.create_foreign_key(None, 'categories', ['category_id'], ['id'])
        batch_op.drop_column('category_root_chain')
        batch_op.drop_index('ix_events_category_root_chain')

    with op.batch_alter_table('categories', schema=None) as batch_op:
        batch_op.drop_column('root_chain')
        batch_op.drop_index('root_chain')
        batch_op.drop_column('parents_id')

    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('favorite_categories', sa.String(length=16), nullable=True))

    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('favorite_categories')

    with op.batch_alter_table('events', schema=None) as batch_op:
        batch_op.add_column(sa.Column('category_root_chain', mysql.VARCHAR(length=128), nullable=False))
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key('events_ibfk_2', 'categories', ['category_root_chain'], ['root_chain'])
        batch_op.create_index('ix_events_category_root_chain', ['category_root_chain'], unique=False)
        batch_op.drop_column('category_id')

    with op.batch_alter_table('categories', schema=None) as batch_op:
        batch_op.add_column(sa.Column('parents_id', mysql.INTEGER(), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column('root_chain', mysql.VARCHAR(length=128), nullable=False))
        batch_op.create_index('root_chain', ['root_chain'], unique=False)

    # ### end Alembic commands ###
