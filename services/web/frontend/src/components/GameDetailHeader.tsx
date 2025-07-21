import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { GameListItem } from '@/lib/api';
import { 
  Calendar, 
  Star, 
  Heart,
  Play,
  Download,
  ExternalLink,
  User,
  Building,
  Monitor,
  Tag
} from 'lucide-react';

interface GameDetailHeaderProps {
  game: GameListItem;
  showUserData?: boolean;
}

export function GameDetailHeader({ game, showUserData = false }: GameDetailHeaderProps) {
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  const formatPlaytime = (minutes: number) => {
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    if (hours < 1) return `${minutes} minutes`;
    if (mins === 0) return `${hours} ${hours === 1 ? 'hour' : 'hours'}`;
    return `${hours}h ${mins}m`;
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'bg-green-100 text-green-800';
      case 'playing': return 'bg-blue-100 text-blue-800';
      case 'abandoned': return 'bg-red-100 text-red-800';
      case 'backlog': return 'bg-yellow-100 text-yellow-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getRatingColor = (score: number) => {
    if (score >= 90) return 'text-green-600';
    if (score >= 80) return 'text-blue-600';
    if (score >= 70) return 'text-yellow-600';
    if (score >= 60) return 'text-orange-600';
    return 'text-red-600';
  };

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Cover Art */}
        <div className="lg:col-span-1">
          <div className="aspect-[3/4] bg-gradient-to-br from-gray-100 to-gray-200 rounded-lg overflow-hidden shadow-lg">
            {game.cover_image_url ? (
              <img
                src={game.cover_image_url}
                alt={game.title}
                className="w-full h-full object-cover"
              />
            ) : (
              <div className="w-full h-full flex items-center justify-center">
                <Play className="h-16 w-16 text-gray-400" />
              </div>
            )}
          </div>
        </div>

        {/* Game Info */}
        <div className="lg:col-span-2 space-y-6">
          {/* Title and Basic Info */}
          <div>
            <div className="flex items-start justify-between gap-4 mb-4">
              <h1 className="text-4xl font-bold leading-tight">{game.title}</h1>
              {showUserData && game.user_data?.is_favorite && (
                <Heart className="h-8 w-8 text-red-500 fill-current flex-shrink-0" />
              )}
            </div>

            <div className="flex flex-wrap gap-4 text-muted-foreground mb-4">
              {game.developer && (
                <div className="flex items-center gap-1">
                  <User className="h-4 w-4" />
                  <span>{game.developer}</span>
                </div>
              )}
              {game.publisher && game.publisher !== game.developer && (
                <div className="flex items-center gap-1">
                  <Building className="h-4 w-4" />
                  <span>{game.publisher}</span>
                </div>
              )}
              {game.release_date && (
                <div className="flex items-center gap-1">
                  <Calendar className="h-4 w-4" />
                  <span>{formatDate(game.release_date)}</span>
                </div>
              )}
            </div>

            {/* Description */}
            {game.description && (
              <p className="text-muted-foreground leading-relaxed mb-6">
                {game.description}
              </p>
            )}
          </div>

          {/* Ratings and Scores */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {(game.metacritic_score || game.steam_score) && (
              <div className="space-y-3">
                <h3 className="font-semibold flex items-center gap-2">
                  <Star className="h-4 w-4" />
                  Ratings
                </h3>
                <div className="space-y-2">
                  {game.metacritic_score && (
                    <div className="flex items-center justify-between">
                      <span className="text-sm">Metacritic</span>
                      <Badge className={getRatingColor(game.metacritic_score)}>
                        {game.metacritic_score}
                      </Badge>
                    </div>
                  )}
                  {game.steam_score && (
                    <div className="flex items-center justify-between">
                      <span className="text-sm">Steam</span>
                      <Badge className={getRatingColor(Math.round(game.steam_score / 10))}>
                        {Math.round(game.steam_score / 10)}%
                      </Badge>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* User Data */}
            {showUserData && game.user_data && (
              <div className="space-y-3">
                <h3 className="font-semibold flex items-center gap-2">
                  <User className="h-4 w-4" />
                  Your Progress
                </h3>
                <div className="space-y-3">
                  {game.user_data.status !== 'unplayed' && (
                    <div className="flex items-center justify-between">
                      <span className="text-sm">Status</span>
                      <Badge className={getStatusColor(game.user_data.status)}>
                        {game.user_data.status}
                      </Badge>
                    </div>
                  )}
                  
                  {game.user_data.playtime_minutes > 0 && (
                    <div className="flex items-center justify-between">
                      <span className="text-sm">Playtime</span>
                      <span className="text-sm font-medium">
                        {formatPlaytime(game.user_data.playtime_minutes)}
                      </span>
                    </div>
                  )}
                  
                  {game.user_data.rating && (
                    <div className="flex items-center justify-between">
                      <span className="text-sm">Your Rating</span>
                      <div className="flex items-center gap-1">
                        <Star className="h-4 w-4 text-yellow-500 fill-current" />
                        <span className="text-sm font-medium">{game.user_data.rating}/5</span>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>

          {/* Genres and Platforms */}
          <div className="space-y-4">
            {game.genres && game.genres.length > 0 && (
              <div>
                <h4 className="font-medium mb-2 flex items-center gap-2">
                  <Tag className="h-4 w-4" />
                  Genres
                </h4>
                <div className="flex flex-wrap gap-2">
                  {game.genres.map((genre) => (
                    <Badge key={genre} variant="secondary">
                      {genre}
                    </Badge>
                  ))}
                </div>
              </div>
            )}

            {game.platforms_available && game.platforms_available.length > 0 && (
              <div>
                <h4 className="font-medium mb-2 flex items-center gap-2">
                  <Monitor className="h-4 w-4" />
                  Platforms
                </h4>
                <div className="flex flex-wrap gap-2">
                  {game.platforms_available.map((platform) => (
                    <Badge key={platform} variant="outline">
                      {platform.toUpperCase()}
                    </Badge>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Action Buttons */}
          <div className="flex flex-wrap gap-3 pt-4">
            {showUserData && game.user_data?.owned && (
              <Button size="lg" className="flex items-center gap-2">
                <Play className="h-4 w-4" />
                Play Game
              </Button>
            )}
            
            {!showUserData && (
              <Button size="lg" variant="outline" className="flex items-center gap-2">
                <Download className="h-4 w-4" />
                Add to Library
              </Button>
            )}
            
            <Button size="lg" variant="outline" className="flex items-center gap-2">
              <ExternalLink className="h-4 w-4" />
              View on Steam
            </Button>
            
            {showUserData && (
              <Button size="lg" variant="outline" className="flex items-center gap-2">
                <Heart className="h-4 w-4" />
                {game.user_data?.is_favorite ? 'Remove from Favorites' : 'Add to Favorites'}
              </Button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}