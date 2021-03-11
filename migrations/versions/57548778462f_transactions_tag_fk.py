"""transactions_tag_fk

Revision ID: 57548778462f
Revises: 79e0be852858
Create Date: 2021-02-27 03:53:24.900539

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '57548778462f'
down_revision = '79e0be852858'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('transactions', sa.Column('tag_id', sa.BigInteger(), nullable=True))
    op.create_foreign_key(None, 'transactions', 'tags', ['tag_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'transactions', type_='foreignkey')
    op.drop_column('transactions', 'tag_id')
    # ### end Alembic commands ###
