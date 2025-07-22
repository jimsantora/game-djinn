import { useState, useEffect } from 'react';
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
import { useUpdateLibrary, useDeleteLibrary, useSyncLibrary, useSyncStatus, useCancelSync } from '@/hooks/useApi';
import { useSocket } from '@/hooks/useSocket';
import { Library } from '@/lib/api';
import { 
  Edit, 
  Trash2, 
  RefreshCw, 
  Calendar,
  Monitor,
  Loader2,
  Info,
  X
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
  const [checkingStatusFor, setCheckingStatusFor] = useState<string | null>(null);

  const updateLibrary = useUpdateLibrary();
  const deleteLibrary = useDeleteLibrary();
  const syncLibrary = useSyncLibrary();
  const cancelSync = useCancelSync();
  const { syncProgress, joinLibrary, leaveLibrary, connected } = useSocket();
  
  // Check sync status for library if selected
  const { data: syncStatusData } = useSyncStatus(checkingStatusFor);
  
  // Debug: Log sync progress changes
  useEffect(() => {
    if (syncProgress) {
      console.log('LibraryTable - syncProgress updated:', syncProgress);
    }
  }, [syncProgress]);

  // Join library rooms when component mounts and libraries are available
  // Re-join when socket reconnects
  useEffect(() => {
    if (connected && libraries.length > 0) {
      console.log('Joining library rooms for', libraries.length, 'libraries');
      libraries.forEach(library => {
        joinLibrary(library.library_id);
        
        // If any library is syncing, we should expect to receive progress events
        if (library.sync_status === 'syncing') {
          console.log(`Library ${library.library_id} is syncing, expecting progress events`);
        }
      });

      // Cleanup: leave rooms when component unmounts
      return () => {
        libraries.forEach(library => {
          leaveLibrary(library.library_id);
        });
      };
    }
  }, [connected, libraries, joinLibrary, leaveLibrary]);

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
    console.log('Sync button clicked for library:', libraryId);
    try {
      const result = await syncLibrary.mutateAsync(libraryId);
      console.log('Sync started successfully:', result);
    } catch (error) {
      console.error('Failed to sync library:', error);
    }
  };

  const handleCancelSync = async (libraryId: string) => {
    if (!confirm('Are you sure you want to cancel this sync?')) return;
    
    try {
      await cancelSync.mutateAsync(libraryId);
      setCheckingStatusFor(null);
    } catch (error) {
      console.error('Failed to cancel sync:', error);
    }
  };

  const getStatusBadge = (status: string, library: Library) => {
    // Check if this library is currently syncing based on real-time progress
    // The syncProgress should contain library_id to match specific libraries
    const isCurrentlySync = syncProgress && 
      (syncProgress as any).library_id === library.library_id && 
      (syncProgress.status === 'running' || syncProgress.status === 'syncing' || syncProgress.status === 'starting');
    
    // Also check if the status from the database says syncing
    const showSyncUI = isCurrentlySync || status === 'syncing';
    
    if (showSyncUI) {
      const progress = isCurrentlySync ? syncProgress.progress : 0;
      const message = isCurrentlySync ? (syncProgress as any).message : 
        (status === 'syncing' && !isCurrentlySync ? 'Waiting for sync updates...' : 'Syncing...');
      
      // If status is syncing but no real-time updates, show a different UI
      const isStaleSync = status === 'syncing' && !isCurrentlySync;
      
      // Check if we're checking status for this library
      const isCheckingStatus = checkingStatusFor === library.library_id;
      const statusInfo = isCheckingStatus && syncStatusData ? syncStatusData : null;
      
      return (
        <div className="flex flex-col gap-1">
          <div className="flex items-center gap-2">
            <Badge 
              variant="default" 
              className={isStaleSync ? "bg-yellow-100 text-yellow-800" : "bg-blue-100 text-blue-800"}
            >
              <Loader2 className="h-3 w-3 animate-spin mr-1" />
              {isStaleSync ? 'Sync in Progress' : 'Syncing'}
            </Badge>
            {progress > 0 && (
              <span className="text-xs text-muted-foreground">
                {Math.round(progress)}%
              </span>
            )}
            {isStaleSync && (
              <Button
                variant="ghost"
                size="sm"
                className="h-5 w-5 p-0"
                onClick={() => setCheckingStatusFor(
                  checkingStatusFor === library.library_id ? null : library.library_id
                )}
                title={checkingStatusFor === library.library_id ? "Hide sync status" : "Check sync status"}
              >
                <Info className="h-3 w-3" />
              </Button>
            )}
          </div>
          {progress > 0 && (
            <Progress value={progress} className="h-1.5 w-full max-w-[120px]" />
          )}
          {message && (
            <div className="text-xs text-muted-foreground truncate max-w-[120px]" title={message}>
              {message}
            </div>
          )}
          {statusInfo && (
            <div className="text-xs bg-gray-100 p-2 rounded space-y-1">
              <div className="font-medium">Sync Status Check:</div>
              <div>Status: {statusInfo.status}</div>
              <div>Progress: {Math.round(statusInfo.progress_percentage || 0)}%</div>
              {statusInfo.games_processed !== undefined && (
                <div>Games: {statusInfo.games_processed}/{statusInfo.total_games || '?'}</div>
              )}
              {statusInfo.current_step && (
                <div>Step: {statusInfo.current_step}</div>
              )}
              {statusInfo.error_message && (
                <div className="text-red-600">Error: {statusInfo.error_message}</div>
              )}
              <Button
                size="sm"
                variant="destructive"
                className="h-6 text-xs"
                onClick={() => handleCancelSync(library.library_id)}
                disabled={cancelSync.isPending}
              >
                <X className="h-3 w-3 mr-1" />
                Cancel Sync
              </Button>
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
                      !!(syncProgress && 
                       (syncProgress as any).library_id === library.library_id &&
                       (syncProgress.status === 'running' || syncProgress.status === 'syncing'))
                    }
                    title="Sync library"
                  >
                    <RefreshCw 
                      className={`h-4 w-4 ${
                        (syncProgress && 
                         (syncProgress as any).library_id === library.library_id &&
                         (syncProgress.status === 'running' || syncProgress.status === 'syncing')) ? 'animate-spin' : ''
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