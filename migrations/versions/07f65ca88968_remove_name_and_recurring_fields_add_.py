"""Remove name and recurring fields, add status to ToDoItem

Revision ID: 07f65ca88968
Revises: 9a0da5364a79
Create Date: 2024-08-14 15:39:50.175662

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '07f65ca88968'
down_revision = '9a0da5364a79'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('to_do_item', schema=None) as batch_op:
        batch_op.add_column(sa.Column('status', sa.String(length=20), nullable=True))
        batch_op.drop_column('name')
        batch_op.drop_column('recurring')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('to_do_item', schema=None) as batch_op:
        batch_op.add_column(sa.Column('recurring', sa.VARCHAR(length=20), nullable=True))
        batch_op.add_column(sa.Column('name', sa.VARCHAR(length=100), nullable=False))
        batch_op.drop_column('status')

    # ### end Alembic commands ###
