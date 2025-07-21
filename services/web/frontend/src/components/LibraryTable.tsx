import { useState } from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { useUpdateLibrary, useDeleteLibrary, useSyncLibrary } from '@/hooks/useApi';
import { useSocket } from '@/hooks/useSocket';
import { Library } from '@/lib/api';
import { 
  Edit, 
  Trash2, 
  RefreshCw, 
  Calendar,
  Monitor,
  Loader2
} from 'lucide-react';

interface LibraryTableProps {
  libraries: Library[];
  isLoading?: boolean;
}

export function LibraryTable({ libraries, isLoading }: LibraryTableProps) {
  const [editingLibrary, setEditingLibrary] = useState<Library | null>(null);
  const [editFormData, setEditFormData] = useState({
    display_name: '',
    sync_enabled: true,
  });

  const updateLibrary = useUpdateLibrary();
  const deleteLibrary = useDeleteLibrary();
  const syncLibrary = useSyncLibrary();
  const { syncProgress } = useSocket();

  const handleEdit = (library: Library) => {
    setEditingLibrary(library);
    setEditFormData({
      display_name: library.display_name,
      sync_enabled: library.sync_enabled,
    });
  };

  const handleUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingLibrary) return;

    try {
      await updateLibrary.mutateAsync({
        libraryId: editingLibrary.library_id,
        data: editFormData,
      });
      setEditingLibrary(null);
    } catch (error) {
      console.error('Failed to update library:', error);
    }
  };

  const handleDelete = async (libraryId: string) => {
    if (!confirm('Are you sure you want to delete this library?')) return;

    try {
      await deleteLibrary.mutateAsync(libraryId);
    } catch (error) {
      console.error('Failed to delete library:', error);
    }
  };

  const handleSync = async (libraryId: string) => {
    try {
      await syncLibrary.mutateAsync(libraryId);
    } catch (error) {
      console.error('Failed to sync library:', error);
    }
  };

  const getStatusBadge = (status: string, library: Library) => {
    // Check if this library is currently syncing based on real-time progress
    const isCurrentlySync = syncProgress?.platform.toLowerCase() === library.platform_name.toLowerCase() && syncProgress?.status === 'running';
    
    if (isCurrentlySync) {
      return (
        <div className="space-y-1">
          <Badge variant="default" className="bg-blue-100 text-blue-800 flex items-center gap-1">
            <Loader2 className="h-3 w-3 animate-spin" />
            Syncing
          </Badge>
          {syncProgress.progress > 0 && (
            <div className="w-20">
              <Progress value={syncProgress.progress} className="h-1" />
              <div className="text-xs text-muted-foreground text-center">
                {Math.round(syncProgress.progress)}%
              </div>
            </div>
          )}
        </div>
      );
    }

    switch (status) {
      case 'completed':
        return <Badge variant="default" className="bg-green-100 text-green-800">Synced</Badge>;
      case 'running':
        return <Badge variant="default" className="bg-blue-100 text-blue-800">Syncing</Badge>;
      case 'failed':
        return <Badge variant="destructive">Failed</Badge>;
      case 'pending':
        return <Badge variant="secondary">Pending</Badge>;
      default:
        return <Badge variant="outline">{status}</Badge>;
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  if (isLoading) {
    return (
      <div className="text-center py-8">
        <RefreshCw className="h-8 w-8 animate-spin mx-auto mb-4 text-muted-foreground" />
        <p className="text-muted-foreground">Loading libraries...</p>
      </div>
    );
  }

  if (libraries.length === 0) {
    return (
      <div className="text-center py-8">
        <Monitor className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
        <h3 className="text-lg font-semibold mb-2">No libraries found</h3>
        <p className="text-muted-foreground">Add a library to start managing your games.</p>
      </div>
    );
  }

  return (
    <>
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Platform</TableHead>
            <TableHead>Display Name</TableHead>
            <TableHead>User ID</TableHead>
            <TableHead>Games</TableHead>
            <TableHead>Status</TableHead>
            <TableHead>Last Sync</TableHead>
            <TableHead>Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {libraries.map((library) => (
            <TableRow key={library.library_id}>
              <TableCell className="font-medium">
                <div className="flex items-center space-x-2">
                  <Monitor className="h-4 w-4" />
                  <span>{library.platform_name}</span>
                </div>
              </TableCell>
              <TableCell>{library.display_name}</TableCell>
              <TableCell className="font-mono text-sm">
                {library.user_identifier}
              </TableCell>
              <TableCell>
                <Badge variant="outline">{library.total_games}</Badge>
              </TableCell>
              <TableCell>{getStatusBadge(library.sync_status, library)}</TableCell>
              <TableCell>
                {library.last_sync_at ? (
                  <div className="flex items-center space-x-1 text-sm text-muted-foreground">
                    <Calendar className="h-3 w-3" />
                    <span>{formatDate(library.last_sync_at)}</span>
                  </div>
                ) : (
                  <span className="text-muted-foreground">Never</span>
                )}
              </TableCell>
              <TableCell>
                <div className="flex items-center space-x-2">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleSync(library.library_id)}
                    disabled={
                      syncLibrary.isPending || 
                      (syncProgress?.platform.toLowerCase() === library.platform_name.toLowerCase() && 
                       syncProgress?.status === 'running')
                    }
                    title="Sync library"
                  >
                    <RefreshCw 
                      className={`h-4 w-4 ${
                        (syncProgress?.platform.toLowerCase() === library.platform_name.toLowerCase() && 
                         syncProgress?.status === 'running') ? 'animate-spin' : ''
                      }`} 
                    />
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleEdit(library)}
                  >
                    <Edit className="h-4 w-4" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleDelete(library.library_id)}
                    disabled={deleteLibrary.isPending}
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>

      {/* Edit Dialog */}
      <Dialog open={!!editingLibrary} onOpenChange={() => setEditingLibrary(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Edit Library</DialogTitle>
          </DialogHeader>
          <form onSubmit={handleUpdate} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="edit_display_name">Display Name</Label>
              <Input
                id="edit_display_name"
                value={editFormData.display_name}
                onChange={(e) =>
                  setEditFormData(prev => ({ ...prev, display_name: e.target.value }))
                }
                required
              />
            </div>
            <div className="flex items-center space-x-2">
              <input
                type="checkbox"
                id="edit_sync_enabled"
                checked={editFormData.sync_enabled}
                onChange={(e) =>
                  setEditFormData(prev => ({ ...prev, sync_enabled: e.target.checked }))
                }
              />
              <Label htmlFor="edit_sync_enabled">Enable automatic sync</Label>
            </div>
            <div className="flex justify-end space-x-2">
              <Button
                type="button"
                variant="outline"
                onClick={() => setEditingLibrary(null)}
              >
                Cancel
              </Button>
              <Button type="submit" disabled={updateLibrary.isPending}>
                {updateLibrary.isPending ? 'Updating...' : 'Update'}
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>
    </>
  );
}