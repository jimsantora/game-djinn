import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { Switch } from '@/components/ui/switch';
import { useLibraries } from '@/hooks/useApi';
import { Search, X, SlidersHorizontal } from 'lucide-react';

interface GameSearchFiltersProps {
  searchQuery: string;
  onSearchChange: (query: string) => void;
  filters: {
    platforms?: string[];
    genres?: string[];
    min_rating?: number;
    owned_only?: boolean;
    library_id?: string;
  };
  onFiltersChange: (filters: any) => void;
  onSearch: () => void;
  isLoading?: boolean;
}

export function GameSearchFilters({
  searchQuery,
  onSearchChange,
  filters,
  onFiltersChange,
  onSearch,
  isLoading = false,
}: GameSearchFiltersProps) {
  const [showAdvanced, setShowAdvanced] = useState(false);
  const { data: librariesData } = useLibraries(1, 100);

  const commonGenres = [
    'Action', 'Adventure', 'RPG', 'Strategy', 'Simulation', 'Sports',
    'Racing', 'Puzzle', 'Platform', 'Fighting', 'Shooter', 'Horror',
    'Indie', 'Casual', 'MMO', 'Survival'
  ];

  const commonPlatforms = [
    'steam', 'xbox', 'playstation', 'nintendo', 'epic', 'gog'
  ];

  const handlePlatformToggle = (platform: string) => {
    const currentPlatforms = filters.platforms || [];
    const newPlatforms = currentPlatforms.includes(platform)
      ? currentPlatforms.filter(p => p !== platform)
      : [...currentPlatforms, platform];
    
    onFiltersChange({ ...filters, platforms: newPlatforms });
  };

  const handleGenreToggle = (genre: string) => {
    const currentGenres = filters.genres || [];
    const newGenres = currentGenres.includes(genre)
      ? currentGenres.filter(g => g !== genre)
      : [...currentGenres, genre];
    
    onFiltersChange({ ...filters, genres: newGenres });
  };

  const handleRatingChange = (rating: string) => {
    const minRating = rating === 'any' ? undefined : parseInt(rating);
    onFiltersChange({ ...filters, min_rating: minRating });
  };

  const handleLibraryChange = (libraryId: string) => {
    onFiltersChange({ 
      ...filters, 
      library_id: libraryId === 'all' ? undefined : libraryId 
    });
  };

  const clearFilters = () => {
    onFiltersChange({});
    onSearchChange('');
  };

  const activeFilterCount = Object.values(filters).filter(value => 
    value !== undefined && value !== null && 
    (Array.isArray(value) ? value.length > 0 : true)
  ).length;

  return (
    <div className="space-y-4">
      {/* Search Bar */}
      <div className="flex gap-2">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search games by title, developer, or publisher..."
            value={searchQuery}
            onChange={(e) => onSearchChange(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && onSearch()}
            className="pl-9"
          />
        </div>
        <Button onClick={onSearch} disabled={isLoading}>
          {isLoading ? 'Searching...' : 'Search'}
        </Button>
        <Button
          variant="outline"
          onClick={() => setShowAdvanced(!showAdvanced)}
          className="relative"
        >
          <SlidersHorizontal className="h-4 w-4 mr-2" />
          Filters
          {activeFilterCount > 0 && (
            <Badge variant="secondary" className="ml-2 px-1 py-0 text-xs">
              {activeFilterCount}
            </Badge>
          )}
        </Button>
      </div>

      {/* Advanced Filters */}
      {showAdvanced && (
        <div className="border rounded-lg p-4 space-y-4 bg-card">
          <div className="flex items-center justify-between">
            <h3 className="font-medium">Advanced Filters</h3>
            <div className="flex gap-2">
              <Button variant="ghost" size="sm" onClick={clearFilters}>
                <X className="h-4 w-4 mr-1" />
                Clear All
              </Button>
            </div>
          </div>

          <Separator />

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {/* Library Filter */}
            <div className="space-y-2">
              <Label>Library</Label>
              <Select 
                value={filters.library_id || 'all'} 
                onValueChange={handleLibraryChange}
              >
                <SelectTrigger>
                  <SelectValue placeholder="All libraries" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Libraries</SelectItem>
                  {librariesData?.libraries.map((library) => (
                    <SelectItem key={library.library_id} value={library.library_id}>
                      {library.display_name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Rating Filter */}
            <div className="space-y-2">
              <Label>Minimum Rating</Label>
              <Select 
                value={filters.min_rating?.toString() || 'any'} 
                onValueChange={handleRatingChange}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Any rating" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="any">Any Rating</SelectItem>
                  <SelectItem value="90">90+ (Exceptional)</SelectItem>
                  <SelectItem value="80">80+ (Great)</SelectItem>
                  <SelectItem value="70">70+ (Good)</SelectItem>
                  <SelectItem value="60">60+ (Mixed)</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {/* Owned Only Toggle */}
            <div className="space-y-2">
              <Label>Show Only</Label>
              <div className="flex items-center space-x-2">
                <Switch
                  checked={filters.owned_only || false}
                  onCheckedChange={(checked) =>
                    onFiltersChange({ ...filters, owned_only: checked })
                  }
                />
                <Label className="text-sm">Owned games only</Label>
              </div>
            </div>
          </div>

          {/* Platform Filters */}
          <div className="space-y-2">
            <Label>Platforms</Label>
            <div className="flex flex-wrap gap-2">
              {commonPlatforms.map((platform) => (
                <Button
                  key={platform}
                  variant={filters.platforms?.includes(platform) ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => handlePlatformToggle(platform)}
                >
                  {platform.toUpperCase()}
                </Button>
              ))}
            </div>
          </div>

          {/* Genre Filters */}
          <div className="space-y-2">
            <Label>Genres</Label>
            <div className="flex flex-wrap gap-2">
              {commonGenres.map((genre) => (
                <Button
                  key={genre}
                  variant={filters.genres?.includes(genre) ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => handleGenreToggle(genre)}
                >
                  {genre}
                </Button>
              ))}
            </div>
          </div>

          {/* Active Filters Summary */}
          {activeFilterCount > 0 && (
            <>
              <Separator />
              <div className="space-y-2">
                <Label>Active Filters</Label>
                <div className="flex flex-wrap gap-1">
                  {filters.platforms?.map((platform) => (
                    <Badge key={`platform-${platform}`} variant="secondary">
                      Platform: {platform.toUpperCase()}
                      <X 
                        className="h-3 w-3 ml-1 cursor-pointer"
                        onClick={() => handlePlatformToggle(platform)}
                      />
                    </Badge>
                  ))}
                  {filters.genres?.map((genre) => (
                    <Badge key={`genre-${genre}`} variant="secondary">
                      Genre: {genre}
                      <X 
                        className="h-3 w-3 ml-1 cursor-pointer"
                        onClick={() => handleGenreToggle(genre)}
                      />
                    </Badge>
                  ))}
                  {filters.min_rating && (
                    <Badge variant="secondary">
                      Rating: {filters.min_rating}+
                      <X 
                        className="h-3 w-3 ml-1 cursor-pointer"
                        onClick={() => handleRatingChange('any')}
                      />
                    </Badge>
                  )}
                  {filters.owned_only && (
                    <Badge variant="secondary">
                      Owned Only
                      <X 
                        className="h-3 w-3 ml-1 cursor-pointer"
                        onClick={() => onFiltersChange({ ...filters, owned_only: false })}
                      />
                    </Badge>
                  )}
                </div>
              </div>
            </>
          )}
        </div>
      )}
    </div>
  );
}