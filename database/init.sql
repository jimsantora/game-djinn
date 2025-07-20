-- Game Djinn Database Initialization
-- This file is run when the PostgreSQL container first starts

-- Create the database user if it doesn't exist
-- (This is handled by the POSTGRES_USER environment variable in docker-compose)

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create enum types for consistent values
CREATE TYPE sync_status_enum AS ENUM (
    'pending', 'in_progress', 'completed', 'failed', 'rate_limited'
);

CREATE TYPE game_status_enum AS ENUM (
    'unplayed', 'playing', 'completed', 'abandoned', 'wishlist'
);

CREATE TYPE operation_status_enum AS ENUM (
    'started', 'in_progress', 'completed', 'failed', 'cancelled'
);

CREATE TYPE esrb_rating_enum AS ENUM (
    'E', 'E10+', 'T', 'M', 'AO', 'RP'
);

-- Insert default platforms
INSERT INTO platforms (platform_code, platform_name, api_available, icon_url) VALUES
    ('steam', 'Steam', true, 'https://steamcdn-a.akamaihd.net/steam/apps/APPID/header.jpg'),
    ('xbox', 'Xbox Game Pass', true, null),
    ('gog', 'GOG Galaxy', false, null),
    ('epic', 'Epic Games Store', false, null),
    ('playstation', 'PlayStation Network', false, null),
    ('nintendo', 'Nintendo eShop', false, null),
    ('manual', 'Manual Import', false, null)
ON CONFLICT (platform_code) DO NOTHING;

-- Create initial admin configuration (if needed)
-- This will be handled by the application initialization