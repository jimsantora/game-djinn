-- Game Djinn Database Schema
-- PostgreSQL with JSONB for flexible platform data

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Platform registry table
CREATE TABLE platforms (
    platform_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    platform_code VARCHAR(50) UNIQUE NOT NULL, -- steam, xbox, gog, manual, etc.
    platform_name VARCHAR(100) NOT NULL,
    api_available BOOLEAN DEFAULT false,
    icon_url VARCHAR(500),
    base_url VARCHAR(500),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- User libraries across platforms
CREATE TABLE user_libraries (
    library_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    platform_id UUID NOT NULL REFERENCES platforms(platform_id) ON DELETE CASCADE,
    user_identifier VARCHAR(255) NOT NULL, -- Platform-specific user ID
    display_name VARCHAR(255) NOT NULL,
    api_credentials JSONB, -- Encrypted platform credentials/tokens
    sync_enabled BOOLEAN DEFAULT true,
    last_sync_at TIMESTAMP WITH TIME ZONE,
    sync_status VARCHAR(50) DEFAULT 'pending', -- pending, in_progress, completed, failed, rate_limited
    sync_error TEXT,
    sync_position JSONB, -- For resumable sync operations
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(platform_id, user_identifier)
);

-- Universal games catalog with rich metadata
CREATE TABLE games (
    game_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(500) NOT NULL,
    normalized_title VARCHAR(500) NOT NULL, -- For matching across platforms
    slug VARCHAR(500) UNIQUE, -- URL-friendly identifier
    
    -- Rich metadata
    description TEXT,
    short_description TEXT,
    release_date DATE,
    developer VARCHAR(255),
    publisher VARCHAR(255),
    genres JSONB, -- Array of genre strings
    tags JSONB, -- Array of tag strings
    platforms_available JSONB, -- Array of platform codes where game is available
    
    -- Content ratings
    esrb_rating VARCHAR(20), -- E, E10+, T, M, AO, RP
    esrb_descriptors JSONB, -- Array of content descriptors
    pegi_rating INTEGER, -- 3, 7, 12, 16, 18
    
    -- Review scores
    metacritic_score INTEGER CHECK (metacritic_score BETWEEN 0 AND 100),
    metacritic_url VARCHAR(500),
    steam_score INTEGER CHECK (steam_score BETWEEN 0 AND 100), -- Steam positive percentage
    steam_review_count INTEGER,
    
    -- Media
    cover_image_url VARCHAR(500),
    background_image_url VARCHAR(500),
    screenshots JSONB, -- Array of screenshot URLs
    videos JSONB, -- Array of video objects
    
    -- Game details
    website_url VARCHAR(500),
    steam_appid INTEGER,
    gog_id VARCHAR(100),
    epic_id VARCHAR(100),
    xbox_id VARCHAR(100),
    
    -- Enrichment metadata
    igdb_id INTEGER,
    
    -- Time estimates
    playtime_main_hours INTEGER,
    playtime_completionist_hours INTEGER,
    
    -- Search optimization
    search_vector tsvector,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- User-specific game data
CREATE TABLE user_games (
    user_game_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    library_id UUID NOT NULL REFERENCES user_libraries(library_id) ON DELETE CASCADE,
    game_id UUID NOT NULL REFERENCES games(game_id) ON DELETE CASCADE,
    
    -- Platform-specific identifiers
    platform_game_id VARCHAR(255), -- Platform's internal game ID
    
    -- User data
    owned BOOLEAN DEFAULT true,
    owned_date TIMESTAMP WITH TIME ZONE,
    
    -- Playtime tracking
    total_playtime_minutes INTEGER DEFAULT 0,
    last_played_at TIMESTAMP WITH TIME ZONE,
    first_played_at TIMESTAMP WITH TIME ZONE,
    
    -- User preferences
    game_status VARCHAR(50) DEFAULT 'unplayed', -- unplayed, playing, completed, abandoned, wishlist
    user_rating INTEGER CHECK (user_rating BETWEEN 1 AND 5),
    user_notes TEXT,
    is_favorite BOOLEAN DEFAULT false,
    
    -- Platform-specific data
    platform_data JSONB, -- Store platform-specific fields
    
    -- Sync metadata
    last_synced_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(library_id, game_id)
);

-- Cross-platform achievements/trophies
CREATE TABLE game_achievements (
    achievement_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    game_id UUID NOT NULL REFERENCES games(game_id) ON DELETE CASCADE,
    platform_id UUID NOT NULL REFERENCES platforms(platform_id) ON DELETE CASCADE,
    
    platform_achievement_id VARCHAR(255) NOT NULL, -- Platform's internal achievement ID
    title VARCHAR(255) NOT NULL,
    description TEXT,
    icon_url VARCHAR(500),
    points INTEGER DEFAULT 0,
    rarity_percentage DECIMAL(5,2), -- What % of players have this
    is_hidden BOOLEAN DEFAULT false,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(game_id, platform_id, platform_achievement_id)
);

-- User achievement unlocks
CREATE TABLE user_achievements (
    user_achievement_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_game_id UUID NOT NULL REFERENCES user_games(user_game_id) ON DELETE CASCADE,
    achievement_id UUID NOT NULL REFERENCES game_achievements(achievement_id) ON DELETE CASCADE,
    
    unlocked_at TIMESTAMP WITH TIME ZONE NOT NULL,
    progress_percentage INTEGER DEFAULT 100 CHECK (progress_percentage BETWEEN 0 AND 100),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(user_game_id, achievement_id)
);

-- Smart collections for organizing games
CREATE TABLE game_collections (
    collection_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    library_id UUID NOT NULL REFERENCES user_libraries(library_id) ON DELETE CASCADE,
    
    name VARCHAR(255) NOT NULL,
    description TEXT,
    color VARCHAR(20), -- Hex color for UI
    icon VARCHAR(50), -- Icon identifier
    
    -- Collection rules (for smart collections)
    is_smart BOOLEAN DEFAULT false,
    rules JSONB, -- JSON rules for automatic game inclusion
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(library_id, name)
);

-- Many-to-many relationship for collections
CREATE TABLE collection_games (
    collection_id UUID NOT NULL REFERENCES game_collections(collection_id) ON DELETE CASCADE,
    game_id UUID NOT NULL REFERENCES games(game_id) ON DELETE CASCADE,
    added_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    PRIMARY KEY (collection_id, game_id)
);

-- Game matching for cross-platform detection
CREATE TABLE game_matches (
    match_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    primary_game_id UUID NOT NULL REFERENCES games(game_id) ON DELETE CASCADE,
    matched_game_id UUID NOT NULL REFERENCES games(game_id) ON DELETE CASCADE,
    
    match_confidence DECIMAL(3,2) CHECK (match_confidence BETWEEN 0.0 AND 1.0),
    match_method VARCHAR(50), -- title_exact, title_fuzzy, external_id, manual
    verified BOOLEAN DEFAULT false, -- Manual verification
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(primary_game_id, matched_game_id)
);

-- Sync operations log for tracking and debugging
CREATE TABLE sync_operations (
    operation_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    library_id UUID NOT NULL REFERENCES user_libraries(library_id) ON DELETE CASCADE,
    
    operation_type VARCHAR(50) NOT NULL, -- full_sync, incremental_sync, manual_sync
    status VARCHAR(50) NOT NULL, -- started, in_progress, completed, failed, cancelled
    
    started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE,
    
    games_processed INTEGER DEFAULT 0,
    games_added INTEGER DEFAULT 0,
    games_updated INTEGER DEFAULT 0,
    errors_count INTEGER DEFAULT 0,
    
    error_details JSONB,
    operation_log JSONB, -- Detailed operation log
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX idx_games_normalized_title ON games(normalized_title);
CREATE INDEX idx_games_steam_appid ON games(steam_appid) WHERE steam_appid IS NOT NULL;
CREATE INDEX idx_games_igdb_id ON games(igdb_id) WHERE igdb_id IS NOT NULL;
CREATE INDEX idx_games_search_vector ON games USING gin(search_vector);
CREATE INDEX idx_games_esrb_rating ON games(esrb_rating);
CREATE INDEX idx_games_metacritic_score ON games(metacritic_score) WHERE metacritic_score IS NOT NULL;
CREATE INDEX idx_games_release_date ON games(release_date) WHERE release_date IS NOT NULL;

CREATE INDEX idx_user_games_library_id ON user_games(library_id);
CREATE INDEX idx_user_games_status ON user_games(game_status);
CREATE INDEX idx_user_games_last_played ON user_games(last_played_at) WHERE last_played_at IS NOT NULL;
CREATE INDEX idx_user_games_playtime ON user_games(total_playtime_minutes);
CREATE INDEX idx_user_games_favorites ON user_games(is_favorite) WHERE is_favorite = true;

CREATE INDEX idx_user_libraries_platform ON user_libraries(platform_id);
CREATE INDEX idx_user_libraries_sync_status ON user_libraries(sync_status);
CREATE INDEX idx_user_libraries_last_sync ON user_libraries(last_sync_at);

-- Full-text search trigger for games
CREATE OR REPLACE FUNCTION update_games_search_vector()
RETURNS TRIGGER AS $$
BEGIN
    NEW.search_vector := 
        setweight(to_tsvector('english', COALESCE(NEW.title, '')), 'A') ||
        setweight(to_tsvector('english', COALESCE(NEW.developer, '')), 'B') ||
        setweight(to_tsvector('english', COALESCE(NEW.publisher, '')), 'B') ||
        setweight(to_tsvector('english', COALESCE(NEW.description, '')), 'C');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_games_search_vector
    BEFORE INSERT OR UPDATE ON games
    FOR EACH ROW EXECUTE FUNCTION update_games_search_vector();

-- Updated timestamp triggers
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_platforms_updated_at BEFORE UPDATE ON platforms FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_user_libraries_updated_at BEFORE UPDATE ON user_libraries FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_games_updated_at BEFORE UPDATE ON games FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_user_games_updated_at BEFORE UPDATE ON user_games FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_game_achievements_updated_at BEFORE UPDATE ON game_achievements FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_game_collections_updated_at BEFORE UPDATE ON game_collections FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();