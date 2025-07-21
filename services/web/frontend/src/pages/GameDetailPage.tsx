import { useParams, Link, useSearchParams } from "react-router-dom";
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { GameDetailHeader } from '@/components/GameDetailHeader';
import { GameDetailContent } from '@/components/GameDetailContent';
import { useGame, useLibraries } from '@/hooks/useApi';
import { ArrowLeft, RefreshCw, ExternalLink } from 'lucide-react';

export function GameDetailPage() {
  const { gameId } = useParams<{ gameId: string }>();
  const [searchParams] = useSearchParams();
  const libraryId = searchParams.get('library');

  const { data: game, isLoading, error, refetch } = useGame(gameId!, libraryId || undefined);
  const { data: librariesData } = useLibraries(1, 100);

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="sm" asChild>
            <Link to="/games">
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Games
            </Link>
          </Button>
        </div>
        
        <Card>
          <CardContent className="flex items-center justify-center py-12">
            <div className="text-center">
              <RefreshCw className="h-8 w-8 animate-spin mx-auto mb-4 text-muted-foreground" />
              <p className="text-muted-foreground">Loading game details...</p>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (error || !game) {
    return (
      <div className="space-y-6">
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="sm" asChild>
            <Link to="/games">
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Games
            </Link>
          </Button>
        </div>
        
        <Card>
          <CardContent className="text-center py-12">
            <h3 className="text-lg font-semibold mb-2">Game Not Found</h3>
            <p className="text-muted-foreground mb-4">
              The game you're looking for doesn't exist or couldn't be loaded.
            </p>
            <div className="flex gap-2 justify-center">
              <Button variant="outline" onClick={() => refetch()}>
                <RefreshCw className="h-4 w-4 mr-2" />
                Try Again
              </Button>
              <Button asChild>
                <Link to="/games">Back to Games</Link>
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  const selectedLibrary = libraryId 
    ? librariesData?.libraries.find(lib => lib.library_id === libraryId)
    : null;

  return (
    <div className="space-y-6">
      {/* Navigation */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="sm" asChild>
            <Link to="/games">
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Games
            </Link>
          </Button>
          
          {selectedLibrary && (
            <Badge variant="secondary" className="flex items-center gap-1">
              <ExternalLink className="h-3 w-3" />
              {selectedLibrary.display_name}
            </Badge>
          )}
        </div>
        
        <Button variant="outline" onClick={() => refetch()} disabled={isLoading}>
          <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
          Refresh
        </Button>
      </div>

      {/* Game Header */}
      <GameDetailHeader game={game} showUserData={!!libraryId} />

      {/* Game Content */}
      <GameDetailContent game={game} showUserData={!!libraryId} />

      {/* Related Games - Placeholder */}
      <Card>
        <CardContent className="py-6">
          <h3 className="text-lg font-semibold mb-4">You might also like</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
            {Array.from({ length: 6 }, (_, i) => (
              <div key={i} className="aspect-[3/4] bg-gradient-to-br from-gray-100 to-gray-200 rounded-lg">
                <div className="w-full h-full flex items-center justify-center">
                  <span className="text-xs text-gray-400">Game {i + 1}</span>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}