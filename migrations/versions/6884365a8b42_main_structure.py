"""Main structure

Revision ID: 6884365a8b42
Revises: 
Create Date: 2021-01-30 05:01:22.999713

"""
import os
import sys
from alembic import op
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker
from application import enums
BASE_PATH = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_PATH)

Session = sessionmaker()


# revision identifiers, used by Alembic.
revision = '6884365a8b42'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('projects',
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(length=128), nullable=True),
    sa.Column('access_token', sa.String(length=128), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('roles',
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('type', sa.String(length=128), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('transaction_types',
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('type', sa.String(length=128), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('users',
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('telegram_id', sa.BigInteger(), nullable=True),
    sa.Column('name', sa.String(length=128), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('transactions',
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('amount', sa.BigInteger(), nullable=True),
    sa.Column('project_id', sa.BigInteger(), nullable=True),
    sa.Column('user_id', sa.BigInteger(), nullable=True),
    sa.Column('type_id', sa.BigInteger(), nullable=True),
    sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
    sa.ForeignKeyConstraint(['type_id'], ['transaction_types.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('users_to_projects',
    sa.Column('user_id', sa.BigInteger(), nullable=False),
    sa.Column('project_id', sa.Integer(), nullable=False),
    sa.Column('role_id', sa.BigInteger(), nullable=True),
    sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
    sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('user_id', 'project_id')
    )
    # ### end Alembic commands ###

    bind = op.get_bind()
    session = Session(bind=bind)

    for role in enums.UserRoles:
        session.execute(f"INSERT INTO roles (type) VALUES ('{role.name.lower()}');")

    for type in enums.TransactionTypes:
        session.execute(f"INSERT INTO transaction_types (type) VALUES ('{type.name.lower()}');")


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('users_to_projects')
    op.drop_table('transactions')
    op.drop_table('users')
    op.drop_table('transaction_types')
    op.drop_table('roles')
    op.drop_table('projects')
    # ### end Alembic commands ###
