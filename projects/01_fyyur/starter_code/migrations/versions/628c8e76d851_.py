"""empty message

Revision ID: 628c8e76d851
Revises: c14075d977eb
Create Date: 2021-01-27 21:13:40.626214

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '628c8e76d851'
down_revision = 'c14075d977eb'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    # op.create_table('Shows',
    # sa.Column('id', sa.Integer(), nullable=False),
    # sa.Column('start_time', sa.DateTime(), nullable=True),
    # sa.Column('artist_id', sa.Integer(), nullable=True),
    # sa.Column('venue_id', sa.Integer(), nullable=True),
    # sa.ForeignKeyConstraint(['artist_id'], ['Artist.id'], ),
    # sa.ForeignKeyConstraint(['venue_id'], ['Venue.id'], ),
    # sa.PrimaryKeyConstraint('id')
    # )
    op.alter_column('Show', 'artist_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.alter_column('Show', 'venue_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('Show', 'venue_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.alter_column('Show', 'artist_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    # op.drop_table('Shows')
    # ### end Alembic commands ###
