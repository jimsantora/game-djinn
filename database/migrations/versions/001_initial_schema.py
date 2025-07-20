"""Initial database schema

Revision ID: 001
Revises: 
Create Date: 2024-07-20 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Enable UUID extension
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
    
    # Create enum types
    sync_status_enum = postgresql.ENUM(
        'pending', 'in_progress', 'completed', 'failed', 'rate_limited',
        name='sync_status_enum'
    )
    sync_status_enum.create(op.get_bind())
    
    game_status_enum = postgresql.ENUM(
        'unplayed', 'playing', 'completed', 'abandoned', 'wishlist',
        name='game_status_enum'
    )
    game_status_enum.create(op.get_bind())
    
    operation_status_enum = postgresql.ENUM(
        'started', 'in_progress', 'completed', 'failed', 'cancelled',
        name='operation_status_enum'
    )
    operation_status_enum.create(op.get_bind())
    
    esrb_rating_enum = postgresql.ENUM(
        'E', 'E10+', 'T', 'M', 'AO', 'RP',
        name='esrb_rating_enum'
    )
    esrb_rating_enum.create(op.get_bind())
    
    # Create platforms table
    op.create_table(
        'platforms',
        sa.Column('platform_id', postgresql.UUID(as_uuid=True), 
                 server_default=sa.text('uuid_generate_v4()'), nullable=False),
        sa.Column('platform_code', sa.String(50), nullable=False),
        sa.Column('platform_name', sa.String(100), nullable=False),
        sa.Column('api_available', sa.Boolean(), server_default=sa.text('false')),
        sa.Column('icon_url', sa.String(500)),
        sa.Column('base_url', sa.String(500)),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), 
                 server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), 
                 server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('platform_id'),
        sa.UniqueConstraint('platform_code')
    )
    
    # Create user_libraries table
    op.create_table(
        'user_libraries',
        sa.Column('library_id', postgresql.UUID(as_uuid=True), 
                 server_default=sa.text('uuid_generate_v4()'), nullable=False),
        sa.Column('platform_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_identifier', sa.String(255), nullable=False),
        sa.Column('display_name', sa.String(255), nullable=False),
        sa.Column('api_credentials', postgresql.JSONB()),
        sa.Column('sync_enabled', sa.Boolean(), server_default=sa.text('true')),
        sa.Column('last_sync_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('sync_status', sync_status_enum, server_default=sa.text("'pending'")),
        sa.Column('sync_error', sa.Text()),
        sa.Column('sync_position', postgresql.JSONB()),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), 
                 server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), 
                 server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['platform_id'], ['platforms.platform_id'], 
                               ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('library_id'),
        sa.UniqueConstraint('platform_id', 'user_identifier')
    )
    
    # Create games table
    op.create_table(
        'games',
        sa.Column('game_id', postgresql.UUID(as_uuid=True), 
                 server_default=sa.text('uuid_generate_v4()'), nullable=False),
        sa.Column('title', sa.String(500), nullable=False),
        sa.Column('normalized_title', sa.String(500), nullable=False),
        sa.Column('slug', sa.String(500)),
        sa.Column('description', sa.Text()),
        sa.Column('short_description', sa.Text()),
        sa.Column('release_date', sa.Date()),
        sa.Column('developer', sa.String(255)),
        sa.Column('publisher', sa.String(255)),
        sa.Column('genres', postgresql.JSONB()),
        sa.Column('tags', postgresql.JSONB()),
        sa.Column('platforms_available', postgresql.JSONB()),
        sa.Column('esrb_rating', esrb_rating_enum),
        sa.Column('esrb_descriptors', postgresql.JSONB()),
        sa.Column('pegi_rating', sa.Integer()),
        sa.Column('metacritic_score', sa.Integer()),
        sa.Column('metacritic_url', sa.String(500)),
        sa.Column('steam_score', sa.Integer()),
        sa.Column('steam_review_count', sa.Integer()),
        sa.Column('cover_image_url', sa.String(500)),
        sa.Column('background_image_url', sa.String(500)),
        sa.Column('screenshots', postgresql.JSONB()),
        sa.Column('videos', postgresql.JSONB()),
        sa.Column('website_url', sa.String(500)),
        sa.Column('steam_appid', sa.Integer()),
        sa.Column('gog_id', sa.String(100)),
        sa.Column('epic_id', sa.String(100)),
        sa.Column('xbox_id', sa.String(100)),
        sa.Column('rawg_id', sa.Integer()),
        sa.Column('igdb_id', sa.Integer()),
        sa.Column('playtime_main_hours', sa.Integer()),
        sa.Column('playtime_completionist_hours', sa.Integer()),
        sa.Column('search_vector', postgresql.TSVECTOR()),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), 
                 server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), 
                 server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.CheckConstraint('metacritic_score BETWEEN 0 AND 100'),
        sa.CheckConstraint('steam_score BETWEEN 0 AND 100'),
        sa.PrimaryKeyConstraint('game_id'),
        sa.UniqueConstraint('slug')
    )
    
    # Continue with remaining tables...
    # (This is a simplified version - the full migration would include all tables)
    
    # Create indexes
    op.create_index('idx_games_normalized_title', 'games', ['normalized_title'])
    op.create_index('idx_games_steam_appid', 'games', ['steam_appid'])
    op.create_index('idx_games_rawg_id', 'games', ['rawg_id'])
    op.create_index('idx_games_igdb_id', 'games', ['igdb_id'])
    op.create_index('idx_games_search_vector', 'games', ['search_vector'], postgresql_using='gin')
    op.create_index('idx_games_esrb_rating', 'games', ['esrb_rating'])
    op.create_index('idx_games_metacritic_score', 'games', ['metacritic_score'])
    op.create_index('idx_games_release_date', 'games', ['release_date'])
    
    op.create_index('idx_user_libraries_platform', 'user_libraries', ['platform_id'])
    op.create_index('idx_user_libraries_sync_status', 'user_libraries', ['sync_status'])
    op.create_index('idx_user_libraries_last_sync', 'user_libraries', ['last_sync_at'])


def downgrade() -> None:
    # Drop all tables and types in reverse order
    op.drop_table('user_libraries')
    op.drop_table('games') 
    op.drop_table('platforms')
    
    # Drop enum types
    op.execute('DROP TYPE IF EXISTS sync_status_enum')
    op.execute('DROP TYPE IF EXISTS game_status_enum') 
    op.execute('DROP TYPE IF EXISTS operation_status_enum')
    op.execute('DROP TYPE IF EXISTS esrb_rating_enum')
    
    # Drop extension
    op.execute('DROP EXTENSION IF EXISTS "uuid-ossp"')