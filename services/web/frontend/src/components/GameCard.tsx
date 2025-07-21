import { Link } from 'react-router-dom';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { GameListItem } from '@/lib/api';
import { 
  Calendar, 
  Star, 
  Clock, 
  Heart,
  ExternalLink,
  Play
} from 'lucide-react';

interface GameCardProps {
  game: GameListItem;
  showUserData?: boolean;
}

export function GameCard({ game, showUserData = false }: GameCardProps) {
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
    <Card className="group hover:shadow-lg transition-shadow duration-200">
      <div className="relative">
        {/* Cover Image */}
        <div className="aspect-[3/4] bg-gradient-to-br from-gray-100 to-gray-200 rounded-t-lg overflow-hidden">
          {game.cover_image_url ? (
            <img
              src={game.cover_image_url}
              alt={game.title}
              className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
              loading="lazy"
            />
          ) : (
            <div className="w-full h-full flex items-center justify-center">
              <Play className="h-12 w-12 text-gray-400" />
            </div>
          )}
        </div>

        {/* User Status Badges */}
        {showUserData && game.user_data && (
          <div className="absolute top-2 right-2 flex flex-col gap-1">
            {game.user_data.is_favorite && (
              <Badge variant="secondary" className="bg-red-100 text-red-800">
                <Heart className="h-3 w-3 mr-1 fill-current" />
              </Badge>
            )}
            {game.user_data.status !== 'unplayed' && (
              <Badge className={getStatusColor(game.user_data.status)}>
                {game.user_data.status}
              </Badge>
            )}
          </div>
        )}

        {/* Rating Badge */}
        {(game.metacritic_score || game.steam_score) && (
          <div className="absolute top-2 left-2">
            <Badge variant="secondary" className="bg-black/75 text-white">
              <Star className="h-3 w-3 mr-1" />
              {game.metacritic_score || Math.round((game.steam_score || 0) / 10)}
            </Badge>
          </div>
        )}
      </div>

      <CardContent className="p-4">
        <div className="space-y-3">
          {/* Title and Developer */}
          <div>
            <h3 className="font-semibold text-sm leading-tight line-clamp-2 group-hover:text-primary transition-colors">
              {game.title}
            </h3>
            {game.developer && (
              <p className="text-xs text-muted-foreground mt-1">{game.developer}</p>
            )}
          </div>

          {/* Genres */}
          {game.genres && game.genres.length > 0 && (
            <div className="flex flex-wrap gap-1">
              {game.genres.slice(0, 2).map((genre) => (
                <Badge key={genre} variant="outline" className="text-xs">
                  {genre}
                </Badge>
              ))}
              {game.genres.length > 2 && (
                <Badge variant="outline" className="text-xs">
                  +{game.genres.length - 2}
                </Badge>
              )}
            </div>
          )}

          {/* User Game Data */}
          {showUserData && game.user_data && game.user_data.playtime_minutes > 0 && (
            <div className="flex items-center gap-2 text-xs text-muted-foreground">
              <Clock className="h-3 w-3" />
              <span>{formatPlaytime(game.user_data.playtime_minutes)}</span>
              {game.user_data.rating && (
                <>
                  <Star className="h-3 w-3 ml-2" />
                  <span>{game.user_data.rating}/5</span>
                </>
              )}
            </div>
          )}

          {/* Release Date */}
          {game.release_date && (
            <div className="flex items-center gap-1 text-xs text-muted-foreground">
              <Calendar className="h-3 w-3" />
              <span>{formatDate(game.release_date)}</span>
            </div>
          )}

          {/* Platforms */}
          {game.platforms_available && game.platforms_available.length > 0 && (
            <div className="flex flex-wrap gap-1">
              {game.platforms_available.slice(0, 3).map((platform) => (
                <Badge key={platform} variant="outline" className="text-xs">
                  {platform.toUpperCase()}
                </Badge>
              ))}
            </div>
          )}

          {/* Actions */}
          <div className="flex gap-2 pt-2">
            <Button asChild size="sm" className="flex-1">
              <Link to={`/games/${game.game_id}`}>
                <ExternalLink className="h-3 w-3 mr-1" />
                Details
              </Link>
            </Button>
            {showUserData && game.user_data?.owned && (
              <Button variant="outline" size="sm">
                <Play className="h-3 w-3" />
              </Button>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}