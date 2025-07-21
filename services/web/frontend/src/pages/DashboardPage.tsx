import { Link } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { LibraryCreateDialog } from '@/components/LibraryCreateDialog';
import { useLibraries, useGames } from '@/hooks/useApi';
import { Library, Plus, Gamepad2, Clock, Trophy } from 'lucide-react';

export function DashboardPage() {
  const { data: librariesData, refetch: refetchLibraries } = useLibraries(1, 100);
  const { data: gamesData } = useGames(1, 1); // Just get total count

  const totalLibraries = librariesData?.total || 0;
  const totalGames = gamesData?.total || 0;
  // Note: totalPlaytime calculation is a placeholder for future implementation
  // const totalPlaytime = librariesData?.libraries.reduce((sum, lib) => {
  //   return sum + 0; // Placeholder
  // }, 0) || 0;
  const activeSyncs = librariesData?.libraries.filter(lib => lib.sync_status === 'running').length || 0;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
        <p className="text-muted-foreground">Welcome to Game Djinn - AI-powered gaming library management</p>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Libraries</CardTitle>
            <Library className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{totalLibraries}</div>
            <p className="text-xs text-muted-foreground">Connected platforms</p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Games</CardTitle>
            <Gamepad2 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{totalGames}</div>
            <p className="text-xs text-muted-foreground">Total games</p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Syncs</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{activeSyncs}</div>
            <p className="text-xs text-muted-foreground">Currently syncing</p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Achievements</CardTitle>
            <Trophy className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">0</div>
            <p className="text-xs text-muted-foreground">Unlocked</p>
          </CardContent>
        </Card>
      </div>
      
      <Card>
        <CardHeader>
          <CardTitle>Quick Actions</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <LibraryCreateDialog onSuccess={() => refetchLibraries()}>
              <Button variant="outline" className="h-20 flex-col w-full">
                <Plus className="h-6 w-6 mb-2" />
                <p className="font-medium">Add Library</p>
                <p className="text-sm text-muted-foreground">Connect a gaming platform</p>
              </Button>
            </LibraryCreateDialog>
            
            <Link to="/libraries">
              <Button variant="outline" className="h-20 flex-col w-full">
                <Library className="h-6 w-6 mb-2" />
                <p className="font-medium">Manage Libraries</p>
                <p className="text-sm text-muted-foreground">View and sync libraries</p>
              </Button>
            </Link>
            
            <Link to="/games">
              <Button variant="outline" className="h-20 flex-col w-full">
                <Gamepad2 className="h-6 w-6 mb-2" />
                <p className="font-medium">Browse Games</p>
                <p className="text-sm text-muted-foreground">Explore your collection</p>
              </Button>
            </Link>
          </div>
        </CardContent>
      </Card>

      {/* Recent Activity */}
      {librariesData && librariesData.libraries.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Recent Libraries</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {librariesData.libraries.slice(0, 3).map((library) => (
                <div key={library.library_id} className="flex items-center justify-between">
                  <div>
                    <p className="font-medium">{library.display_name}</p>
                    <p className="text-sm text-muted-foreground">
                      {library.platform_name} • {library.total_games} games
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-medium capitalize">{library.sync_status}</p>
                    <p className="text-xs text-muted-foreground">
                      {library.last_sync_at ? 
                        new Date(library.last_sync_at).toLocaleDateString() : 
                        'Never synced'
                      }
                    </p>
                  </div>
                </div>
              ))}
            </div>
            <div className="mt-4">
              <Link to="/libraries">
                <Button variant="outline" className="w-full">
                  View All Libraries
                </Button>
              </Link>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}