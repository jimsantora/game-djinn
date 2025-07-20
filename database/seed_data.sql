-- Game Djinn Seed Data for Testing
-- This file contains test data for development and testing

-- Insert platforms (these should be stable across environments)
INSERT INTO platforms (platform_code, platform_name, api_available, icon_url, base_url) VALUES
    ('steam', 'Steam', true, 'https://steamcdn-a.akamaihd.net/steam/apps/APPID/header.jpg', 'https://store.steampowered.com/'),
    ('xbox', 'Xbox Game Pass', true, null, 'https://www.xbox.com/'),
    ('gog', 'GOG Galaxy', false, null, 'https://www.gog.com/'),
    ('epic', 'Epic Games Store', false, null, 'https://store.epicgames.com/'),
    ('playstation', 'PlayStation Network', false, null, 'https://store.playstation.com/'),
    ('nintendo', 'Nintendo eShop', false, null, 'https://www.nintendo.com/'),
    ('manual', 'Manual Import', false, null, null)
ON CONFLICT (platform_code) DO NOTHING;

-- Insert sample games for testing
INSERT INTO games (
    title, normalized_title, slug, description, short_description,
    release_date, developer, publisher, genres, tags, platforms_available,
    esrb_rating, esrb_descriptors, metacritic_score, steam_score,
    cover_image_url, website_url, steam_appid,
    playtime_main_hours, playtime_completionist_hours
) VALUES 
(
    'The Witcher 3: Wild Hunt',
    'the witcher 3 wild hunt',
    'the-witcher-3-wild-hunt',
    'As war rages on throughout the Northern Realms, you take on the greatest contract of your life — tracking down the Child of Prophecy, a living weapon that can alter the shape of the world.',
    'An open-world RPG masterpiece with rich storytelling and immersive gameplay.',
    '2015-05-19',
    'CD Projekt Red',
    'CD Projekt',
    '["RPG", "Open World", "Fantasy"]',
    '["Singleplayer", "Story Rich", "Choices Matter", "Medieval"]',
    '["steam", "gog", "xbox", "playstation", "nintendo"]',
    'M',
    '["Blood and Gore", "Intense Violence", "Nudity", "Strong Language", "Strong Sexual Content", "Use of Alcohol"]',
    93,
    96,
    'https://cdn.akamai.steamstatic.com/steam/apps/292030/header.jpg',
    'https://thewitcher.com/en/witcher3',
    292030,
    51,
    173
),
(
    'Cyberpunk 2077',
    'cyberpunk 2077',
    'cyberpunk-2077',
    'Cyberpunk 2077 is an open-world, action-adventure story set in Night City, a megalopolis obsessed with power, glamour and body modification.',
    'An open-world action-adventure set in the dystopian Night City.',
    '2020-12-10',
    'CD Projekt Red',
    'CD Projekt',
    '["RPG", "Open World", "Sci-Fi", "Action"]',
    '["Cyberpunk", "Futuristic", "Story Rich", "Character Customization"]',
    '["steam", "gog", "xbox", "playstation"]',
    'M',
    '["Intense Violence", "Blood and Gore", "Nudity", "Strong Sexual Content", "Strong Language", "Use of Drugs and Alcohol"]',
    86,
    78,
    'https://cdn.akamai.steamstatic.com/steam/apps/1091500/header.jpg',
    'https://www.cyberpunk.net/',
    1091500,
    24,
    60
),
(
    'Hades',
    'hades',
    'hades',
    'Defy the god of the dead as you hack and slash out of the Underworld in this rogue-like dungeon crawler.',
    'A rogue-like dungeon crawler with stunning art and tight gameplay.',
    '2020-09-17',
    'Supergiant Games',
    'Supergiant Games',
    '["Roguelike", "Action", "Indie"]',
    '["Dungeon Crawler", "Mythology", "Story Rich", "Fast-Paced"]',
    '["steam", "epic", "xbox", "playstation", "nintendo"]',
    'T',
    '["Blood", "Violence", "Mild Language", "Suggestive Themes"]',
    93,
    98,
    'https://cdn.akamai.steamstatic.com/steam/apps/1145360/header.jpg',
    'https://www.supergiantgames.com/games/hades/',
    1145360,
    22,
    95
),
(
    'Among Us',
    'among us',
    'among-us',
    'An online and local party game of teamwork and betrayal for 4-15 players...in space!',
    'A social deduction party game of teamwork and betrayal.',
    '2018-06-15',
    'InnerSloth',
    'InnerSloth',
    '["Party", "Multiplayer", "Social Deduction"]',
    '["Online Co-Op", "Local Co-Op", "Cross-Platform Multiplayer", "Colorful"]',
    '["steam", "xbox", "playstation", "nintendo"]',
    'E10+',
    '["Fantasy Violence", "Mild Blood"]',
    85,
    84,
    'https://cdn.akamai.steamstatic.com/steam/apps/945360/header.jpg',
    'https://www.innersloth.com/games/among-us/',
    945360,
    2,
    10
),
(
    'Minecraft',
    'minecraft',
    'minecraft',
    'Minecraft is a game about placing blocks and going on adventures. Explore randomly generated worlds and build amazing things.',
    'A sandbox game where you can build anything you can imagine.',
    '2011-11-18',
    'Mojang Studios',
    'Microsoft',
    '["Sandbox", "Survival", "Building"]',
    '["Crafting", "Multiplayer", "Procedural Generation", "Pixelated"]',
    '["xbox", "playstation", "nintendo"]',
    'E10+',
    '["Fantasy Violence"]',
    93,
    null,
    null,
    'https://www.minecraft.net/',
    null,
    null,
    null
)
ON CONFLICT (slug) DO NOTHING;

-- Insert sample user library for testing
DO $$
DECLARE
    steam_platform_id UUID;
    test_library_id UUID;
    witcher_game_id UUID;
    cyberpunk_game_id UUID;
    hades_game_id UUID;
BEGIN
    -- Get platform IDs
    SELECT platform_id INTO steam_platform_id FROM platforms WHERE platform_code = 'steam';
    
    -- Insert test user library
    INSERT INTO user_libraries (
        platform_id, user_identifier, display_name, sync_enabled, sync_status
    ) VALUES (
        steam_platform_id, 'test_user_123', 'Test Steam User', true, 'completed'
    ) RETURNING library_id INTO test_library_id;
    
    -- Get game IDs
    SELECT game_id INTO witcher_game_id FROM games WHERE slug = 'the-witcher-3-wild-hunt';
    SELECT game_id INTO cyberpunk_game_id FROM games WHERE slug = 'cyberpunk-2077';
    SELECT game_id INTO hades_game_id FROM games WHERE slug = 'hades';
    
    -- Insert user games
    INSERT INTO user_games (
        library_id, game_id, platform_game_id, owned, total_playtime_minutes,
        game_status, user_rating, is_favorite, last_played_at
    ) VALUES 
    (
        test_library_id, witcher_game_id, '292030', true, 3060,
        'completed', 5, true, '2024-01-15 14:30:00'
    ),
    (
        test_library_id, cyberpunk_game_id, '1091500', true, 1440,
        'playing', 4, false, '2024-07-18 20:15:00'
    ),
    (
        test_library_id, hades_game_id, '1145360', true, 2280,
        'completed', 5, true, '2024-06-20 16:45:00'
    );
    
    -- Insert a sample collection
    INSERT INTO game_collections (
        library_id, name, description, color, is_smart
    ) VALUES (
        test_library_id, 'Favorites', 'My favorite games', '#ff6b6b', false
    );
    
END $$;