import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { LibraryCreateDialog } from '@/components/LibraryCreateDialog';
import { LibraryTable } from '@/components/LibraryTable';
import { useLibraries } from '@/hooks/useApi';
import { useSocketEvent } from '@/hooks/useSocket';
import { RefreshCw, Search } from 'lucide-react';

export function LibrariesPage() {
  const [page, setPage] = useState(1);
  const [searchQuery, setSearchQuery] = useState('');
  
  const { data: librariesData, isLoading, refetch } = useLibraries(page, 20);

  // Real-time updates for library changes
  useSocketEvent('library_updated', (data) => {
    console.log('Library updated via socket:', data);
    // Refetch library data when updates occur
    refetch();
  });

  useSocketEvent('sync_complete', (data) => {
    console.log('Sync completed via socket:', data);
    // Refetch to update sync status and game counts
    refetch();
  });

  const handleRefresh = () => {
    refetch();
  };

  // Filter libraries based on search query
  const filteredLibraries = librariesData?.libraries.filter(library =>
    library.display_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    library.platform_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    library.user_identifier.toLowerCase().includes(searchQuery.toLowerCase())
  ) || [];

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Libraries</h1>
          <p className="text-muted-foreground">Manage your connected gaming platforms</p>
        </div>
        <div className="flex items-center space-x-2">
          <Button variant="outline" onClick={handleRefresh} disabled={isLoading}>
            <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
          <LibraryCreateDialog onSuccess={() => refetch()} />
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Libraries</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{librariesData?.total || 0}</div>
            <p className="text-xs text-muted-foreground">Connected platforms</p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Games</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {librariesData?.libraries.reduce((sum, lib) => sum + lib.total_games, 0) || 0}
            </div>
            <p className="text-xs text-muted-foreground">Across all libraries</p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Syncs</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {librariesData?.libraries.filter(lib => lib.sync_status === 'running').length || 0}
            </div>
            <p className="text-xs text-muted-foreground">Currently syncing</p>
          </CardContent>
        </Card>
      </div>

      {/* Search and Filters */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Your Libraries</CardTitle>
            <div className="flex items-center space-x-2">
              <div className="relative">
                <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Search libraries..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-8 w-64"
                />
              </div>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <LibraryTable libraries={filteredLibraries} isLoading={isLoading} />
        </CardContent>
      </Card>

      {/* Pagination */}
      {librariesData && librariesData.pages > 1 && (
        <div className="flex justify-center space-x-2">
          <Button
            variant="outline"
            onClick={() => setPage(page - 1)}
            disabled={page === 1}
          >
            Previous
          </Button>
          <span className="flex items-center px-4 py-2 text-sm">
            Page {page} of {librariesData.pages}
          </span>
          <Button
            variant="outline"
            onClick={() => setPage(page + 1)}
            disabled={page === librariesData.pages}
          >
            Next
          </Button>
        </div>
      )}
    </div>
  );
}