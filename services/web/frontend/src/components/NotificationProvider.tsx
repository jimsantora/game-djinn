import { useEffect } from 'react';
import { toast } from 'sonner';
import { useSocket } from '@/hooks/useSocket';
import { CheckCircle, XCircle, Download } from 'lucide-react';

export function NotificationProvider({ children }: { children: React.ReactNode }) {
  const { socket, connected } = useSocket();

  useEffect(() => {
    if (!socket) return;

    // Sync completion notifications
    const handleSyncComplete = (data: { platform: string; totalGames: number }) => {
      toast.success(`${data.platform} sync completed!`, {
        description: `Successfully synced ${data.totalGames} games`,
        icon: <CheckCircle className="h-4 w-4" />,
        duration: 5000,
      });
    };

    // Sync failure notifications
    const handleSyncError = (data: { platform: string; error: string }) => {
      toast.error(`${data.platform} sync failed`, {
        description: data.error,
        icon: <XCircle className="h-4 w-4" />,
        duration: 10000,
      });
    };

    // Sync start notifications
    const handleSyncStart = (data: { platform: string }) => {
      toast.info(`Starting ${data.platform} sync...`, {
        description: 'This may take a few minutes',
        icon: <Download className="h-4 w-4" />,
        duration: 3000,
      });
    };

    // Library update notifications
    const handleLibraryUpdate = (data: { libraryId: string; action: string; gameName?: string }) => {
      switch (data.action) {
        case 'game_added':
          toast.success('New game added!', {
            description: data.gameName ? `${data.gameName} was added to your library` : 'A new game was added to your library',
            duration: 4000,
          });
          break;
        case 'game_updated':
          toast.info('Game updated', {
            description: data.gameName ? `${data.gameName} information was updated` : 'Game information was updated',
            duration: 3000,
          });
          break;
        case 'achievement_unlocked':
          toast.success('Achievement unlocked!', {
            description: data.gameName ? `New achievement in ${data.gameName}` : 'You unlocked a new achievement',
            duration: 5000,
          });
          break;
      }
    };

    // Connection status notifications
    const handleConnect = () => {
      toast.success('Connected to server', {
        description: 'Real-time updates are now active',
        duration: 2000,
      });
    };

    const handleDisconnect = () => {
      toast.warning('Connection lost', {
        description: 'Attempting to reconnect...',
        duration: 3000,
      });
    };

    // Register event listeners
    socket.on('sync_complete', handleSyncComplete);
    socket.on('sync_error', handleSyncError);
    socket.on('sync_start', handleSyncStart);
    socket.on('library_updated', handleLibraryUpdate);
    socket.on('connect', handleConnect);
    socket.on('disconnect', handleDisconnect);

    return () => {
      socket.off('sync_complete', handleSyncComplete);
      socket.off('sync_error', handleSyncError);
      socket.off('sync_start', handleSyncStart);
      socket.off('library_updated', handleLibraryUpdate);
      socket.off('connect', handleConnect);
      socket.off('disconnect', handleDisconnect);
    };
  }, [socket]);

  // Show initial connection status
  useEffect(() => {
    if (connected) {
      toast.success('Connected', {
        description: 'Real-time updates are active',
        duration: 2000,
      });
    }
  }, [connected]);

  return <>{children}</>;
}