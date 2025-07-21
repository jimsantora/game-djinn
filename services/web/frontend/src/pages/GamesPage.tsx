import { useState } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { GameCard } from '@/components/GameCard';
import { GameListItem } from '@/components/GameListItem';
import { GameSearchFilters } from '@/components/GameSearchFilters';
import { useGames, useGameSearch } from '@/hooks/useApi';
import { 
  Grid3X3, 
  List, 
  RefreshCw, 
  Gamepad2,
  Search,
  SortAsc,
  SortDesc
} from 'lucide-react';

type ViewMode = 'grid' | 'list';
type SortBy = 'title' | 'release_date' | 'rating' | 'playtime';
type SortOrder = 'asc' | 'desc';

export function GamesPage() {
  const [viewMode, setViewMode] = useState<ViewMode>('grid');
  const [searchQuery, setSearchQuery] = useState('');
  const [searchFilters, setSearchFilters] = useState<Record<string, any>>({});
  const [sortBy, setSortBy] = useState<SortBy>('title');
  const [sortOrder, setSortOrder] = useState<SortOrder>('asc');
  const [page, setPage] = useState(1);
  const [isSearching, setIsSearching] = useState(false);

  // Use search when there's a query or filters, otherwise use regular list
  const shouldSearch = searchQuery.length > 0 || Object.keys(searchFilters).length > 0;
  
  const { 
    data: gamesData, 
    isLoading: isLoadingList, 
    refetch: refetchList 
  } = useGames(page, 20);
  
  const {
    data: searchData,
    isLoading: isLoadingSearch,
    refetch: refetchSearch
  } = useGameSearch(searchQuery, { ...searchFilters, page, limit: 20 });

  const currentData = shouldSearch ? searchData : gamesData;
  const isLoading = shouldSearch ? isLoadingSearch : isLoadingList;

  const handleSearch = () => {
    setIsSearching(true);
    setPage(1);
    if (shouldSearch) {
      refetchSearch();
    } else {
      refetchList();
    }
    setIsSearching(false);
  };

  const handleRefresh = () => {
    if (shouldSearch) {
      refetchSearch();
    } else {
      refetchList();
    }
  };

  const handleSortChange = (newSortBy: SortBy) => {
    if (sortBy === newSortBy) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(newSortBy);
      setSortOrder('asc');
    }
  };

  // Sort games based on current sort settings
  const sortedGames = currentData?.games ? [...currentData.games].sort((a, b) => {
    let aValue: any, bValue: any;
    
    switch (sortBy) {
      case 'title':
        aValue = a.title.toLowerCase();
        bValue = b.title.toLowerCase();
        break;
      case 'release_date':
        aValue = a.release_date ? new Date(a.release_date) : new Date(0);
        bValue = b.release_date ? new Date(b.release_date) : new Date(0);
        break;
      case 'rating':
        aValue = a.metacritic_score || a.steam_score || 0;
        bValue = b.metacritic_score || b.steam_score || 0;
        break;
      case 'playtime':
        aValue = a.user_data?.playtime_minutes || 0;
        bValue = b.user_data?.playtime_minutes || 0;
        break;
      default:
        return 0;
    }
    
    if (aValue < bValue) return sortOrder === 'asc' ? -1 : 1;
    if (aValue > bValue) return sortOrder === 'asc' ? 1 : -1;
    return 0;
  }) : [];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Games</h1>
          <p className="text-muted-foreground">Browse and manage your game collection</p>
        </div>
        
        <div className="flex items-center gap-2">
          <Button variant="outline" onClick={handleRefresh} disabled={isLoading}>
            <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
        </div>
      </div>

      {/* Search and Filters */}
      <GameSearchFilters
        searchQuery={searchQuery}
        onSearchChange={setSearchQuery}
        filters={searchFilters}
        onFiltersChange={setSearchFilters}
        onSearch={handleSearch}
        isLoading={isSearching || isLoading}
      />

      {/* Stats and Controls */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        {/* Results Info */}
        <div className="flex items-center gap-4">
          {currentData && (
            <>
              <Badge variant="secondary" className="text-sm">
                {currentData.total} games found
              </Badge>
              {shouldSearch && (
                <Badge variant="outline" className="text-sm">
                  <Search className="h-3 w-3 mr-1" />
                  Search Results
                </Badge>
              )}
            </>
          )}
        </div>

        {/* View Controls */}
        <div className="flex items-center gap-4">
          {/* Sort Controls */}
          <div className="flex items-center gap-2">
            <span className="text-sm text-muted-foreground">Sort by:</span>
            <div className="flex gap-1">
              <Button
                variant={sortBy === 'title' ? 'default' : 'outline'}
                size="sm"
                onClick={() => handleSortChange('title')}
              >
                Title
                {sortBy === 'title' && (
                  sortOrder === 'asc' ? <SortAsc className="h-3 w-3 ml-1" /> : <SortDesc className="h-3 w-3 ml-1" />
                )}
              </Button>
              <Button
                variant={sortBy === 'release_date' ? 'default' : 'outline'}
                size="sm"
                onClick={() => handleSortChange('release_date')}
              >
                Date
                {sortBy === 'release_date' && (
                  sortOrder === 'asc' ? <SortAsc className="h-3 w-3 ml-1" /> : <SortDesc className="h-3 w-3 ml-1" />
                )}
              </Button>
              <Button
                variant={sortBy === 'rating' ? 'default' : 'outline'}
                size="sm"
                onClick={() => handleSortChange('rating')}
              >
                Rating
                {sortBy === 'rating' && (
                  sortOrder === 'asc' ? <SortAsc className="h-3 w-3 ml-1" /> : <SortDesc className="h-3 w-3 ml-1" />
                )}
              </Button>
            </div>
          </div>

          {/* View Mode Toggle */}
          <div className="flex items-center gap-1 border rounded-lg p-1">
            <Button
              variant={viewMode === 'grid' ? 'default' : 'ghost'}
              size="sm"
              onClick={() => setViewMode('grid')}
            >
              <Grid3X3 className="h-4 w-4" />
            </Button>
            <Button
              variant={viewMode === 'list' ? 'default' : 'ghost'}
              size="sm"
              onClick={() => setViewMode('list')}
            >
              <List className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </div>

      {/* Games Display */}
      {isLoading ? (
        <Card>
          <CardContent className="flex items-center justify-center py-12">
            <div className="text-center">
              <RefreshCw className="h-8 w-8 animate-spin mx-auto mb-4 text-muted-foreground" />
              <p className="text-muted-foreground">Loading games...</p>
            </div>
          </CardContent>
        </Card>
      ) : sortedGames.length === 0 ? (
        <Card>
          <CardContent className="text-center py-12">
            <Gamepad2 className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
            <h3 className="text-lg font-semibold mb-2">No games found</h3>
            <p className="text-muted-foreground mb-4">
              {shouldSearch 
                ? 'Try adjusting your search criteria or filters.'
                : 'Connect a library to start browsing your games.'
              }
            </p>
            {shouldSearch && (
              <Button variant="outline" onClick={() => {
                setSearchQuery('');
                setSearchFilters({});
                setPage(1);
              }}>
                Clear Search
              </Button>
            )}
          </CardContent>
        </Card>
      ) : (
        <>
          {/* Games Grid/List */}
          {viewMode === 'grid' ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6">
              {sortedGames.map((game) => (
                <GameCard 
                  key={game.game_id} 
                  game={game} 
                  showUserData={!!searchFilters.library_id}
                />
              ))}
            </div>
          ) : (
            <div className="space-y-4">
              {sortedGames.map((game) => (
                <GameListItem 
                  key={game.game_id} 
                  game={game} 
                  showUserData={!!searchFilters.library_id}
                />
              ))}
            </div>
          )}

          {/* Pagination */}
          {currentData && currentData.pages > 1 && (
            <div className="flex justify-center items-center space-x-2">
              <Button
                variant="outline"
                onClick={() => setPage(Math.max(1, page - 1))}
                disabled={page === 1}
              >
                Previous
              </Button>
              <div className="flex items-center space-x-1">
                {Array.from({ length: Math.min(currentData.pages, 5) }, (_, i) => {
                  const pageNum = i + 1;
                  return (
                    <Button
                      key={pageNum}
                      variant={page === pageNum ? 'default' : 'outline'}
                      size="sm"
                      onClick={() => setPage(pageNum)}
                    >
                      {pageNum}
                    </Button>
                  );
                })}
                {currentData.pages > 5 && <span className="text-muted-foreground">...</span>}
              </div>
              <Button
                variant="outline"
                onClick={() => setPage(Math.min(currentData.pages, page + 1))}
                disabled={page === currentData.pages}
              >
                Next
              </Button>
            </div>
          )}
        </>
      )}
    </div>
  );
}