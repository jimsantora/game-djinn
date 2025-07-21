import { Link } from 'react-router-dom';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { GameListItem as GameType } from '@/lib/api';
import { 
  Calendar, 
  Star, 
  Clock, 
  Heart,
  ExternalLink,
  Play,
  User,
  Monitor
} from 'lucide-react';

interface GameListItemProps {
  game: GameType;
  showUserData?: boolean;
}

export function GameListItem({ game, showUserData = false }: GameListItemProps) {
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  const formatPlaytime = (minutes: number) => {
    const hours = Math.floor(minutes / 60);
    if (hours < 1) return `${minutes}m`;
    if (hours < 100) return `${hours}h ${minutes % 60}m`;
    return `${hours}h`;
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

  return (
    <div className="flex items-center gap-4 p-4 border rounded-lg hover:bg-accent/50 transition-colors">
      {/* Cover Image */}
      <div className="flex-shrink-0">
        <div className="w-16 h-20 bg-gradient-to-br from-gray-100 to-gray-200 rounded overflow-hidden">
          {game.cover_image_url ? (
            <img
              src={game.cover_image_url}
              alt={game.title}
              className="w-full h-full object-cover"
              loading="lazy"
            />
          ) : (
            <div className="w-full h-full flex items-center justify-center">
              <Play className="h-6 w-6 text-gray-400" />
            </div>
          )}
        </div>
      </div>

      {/* Game Info */}
      <div className="flex-1 min-w-0">
        <div className="flex items-start justify-between gap-4">
          <div className="flex-1 min-w-0">
            <h3 className="font-semibold text-base leading-tight truncate hover:text-primary transition-colors">
              <Link to={`/games/${game.game_id}`} className="hover:underline">
                {game.title}
              </Link>
            </h3>
            
            {game.developer && (
              <p className="text-sm text-muted-foreground mt-1 flex items-center gap-1">
                <User className="h-3 w-3" />
                {game.developer}
                {game.publisher && game.publisher !== game.developer && (
                  <span className="ml-2">• {game.publisher}</span>
                )}
              </p>
            )}

            <div className="flex items-center gap-4 mt-2 text-sm text-muted-foreground">
              {/* Release Date */}
              {game.release_date && (
                <div className="flex items-center gap-1">
                  <Calendar className="h-3 w-3" />
                  <span>{formatDate(game.release_date)}</span>
                </div>
              )}

              {/* Rating */}
              {(game.metacritic_score || game.steam_score) && (
                <div className="flex items-center gap-1">
                  <Star className="h-3 w-3" />
                  <span>{game.metacritic_score || Math.round((game.steam_score || 0) / 10)}</span>
                </div>
              )}

              {/* Platforms */}
              {game.platforms_available && game.platforms_available.length > 0 && (
                <div className="flex items-center gap-1">
                  <Monitor className="h-3 w-3" />
                  <span>{game.platforms_available.slice(0, 2).join(', ')}</span>
                  {game.platforms_available.length > 2 && (
                    <span className="text-xs">+{game.platforms_available.length - 2}</span>
                  )}
                </div>
              )}
            </div>

            {/* Genres */}
            {game.genres && game.genres.length > 0 && (
              <div className="flex flex-wrap gap-1 mt-2">
                {game.genres.slice(0, 4).map((genre) => (
                  <Badge key={genre} variant="outline" className="text-xs">
                    {genre}
                  </Badge>
                ))}
                {game.genres.length > 4 && (
                  <Badge variant="outline" className="text-xs">
                    +{game.genres.length - 4}
                  </Badge>
                )}
              </div>
            )}
          </div>

          {/* User Data & Actions */}
          <div className="flex-shrink-0 text-right">
            {showUserData && game.user_data && (
              <div className="space-y-2 mb-3">
                <div className="flex items-center justify-end gap-2">
                  {game.user_data.is_favorite && (
                    <Heart className="h-4 w-4 text-red-500 fill-current" />
                  )}
                  {game.user_data.status !== 'unplayed' && (
                    <Badge className={getStatusColor(game.user_data.status)}>
                      {game.user_data.status}
                    </Badge>
                  )}
                </div>
                
                {game.user_data.playtime_minutes > 0 && (
                  <div className="flex items-center justify-end gap-1 text-sm text-muted-foreground">
                    <Clock className="h-3 w-3" />
                    <span>{formatPlaytime(game.user_data.playtime_minutes)}</span>
                  </div>
                )}
                
                {game.user_data.rating && (
                  <div className="flex items-center justify-end gap-1 text-sm">
                    <Star className="h-3 w-3 text-yellow-500" />
                    <span>{game.user_data.rating}/5</span>
                  </div>
                )}
              </div>
            )}

            <div className="flex gap-2">
              <Button asChild size="sm" variant="outline">
                <Link to={`/games/${game.game_id}`}>
                  <ExternalLink className="h-3 w-3 mr-1" />
                  Details
                </Link>
              </Button>
              {showUserData && game.user_data?.owned && (
                <Button size="sm">
                  <Play className="h-3 w-3 mr-1" />
                  Play
                </Button>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}