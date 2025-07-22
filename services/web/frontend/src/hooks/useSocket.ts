import { useEffect, useRef, useState } from 'react';
import { io, Socket } from 'socket.io-client';
import { useAuth } from '@/contexts/AuthContext';

interface SyncProgress {
  library_id?: string;
  platform?: string;
  status: 'starting' | 'running' | 'syncing' | 'completed' | 'failed';
  progress: number;
  message?: string;
  totalGames?: number;
  processedGames?: number;
  currentGame?: string;
  error?: string;
  games_processed?: number;
  new_games?: number;
  updated_games?: number;
}

interface UseSocketReturn {
  socket: Socket | null;
  connected: boolean;
  syncProgress: SyncProgress | null;
  emit: (event: string, data?: any) => void;
  joinLibrary: (libraryId: string) => void;
  leaveLibrary: (libraryId: string) => void;
}

export function useSocket(): UseSocketReturn {
  const { user, token } = useAuth();
  const socketRef = useRef<Socket | null>(null);
  const [connected, setConnected] = useState(false);
  const [syncProgress, setSyncProgress] = useState<SyncProgress | null>(null);

  useEffect(() => {
    // Only connect if user exists (authenticated or auth disabled)
    if (!user) return;

    const socketUrl = import.meta.env.VITE_SOCKET_URL || import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
    console.log('Connecting to Socket.IO at:', socketUrl);
    
    const socket = io(socketUrl, {
      auth: {
        token: token || 'anonymous'
      },
      transports: ['websocket', 'polling'],
      autoConnect: true,
    });

    socketRef.current = socket;

    socket.on('connect', () => {
      console.log('Socket connected:', socket.id);
      setConnected(true);
      
      // If we had sync progress before disconnect, clear it
      // New progress will come from the server if sync is still running
      setSyncProgress(null);
    });

    socket.on('disconnect', () => {
      console.log('Socket disconnected');
      setConnected(false);
      setSyncProgress(null);
    });

    socket.on('sync:progress', (data: SyncProgress) => {
      console.log('=== SYNC PROGRESS EVENT ===');
      console.log('Raw data:', data);
      console.log('Status:', data.status);
      console.log('Progress:', data.progress);
      console.log('Message:', (data as any).message);
      console.log('Library ID:', (data as any).library_id);
      setSyncProgress(data);
    });

    socket.on('sync:complete', (data: any) => {
      console.log('Sync complete:', data);
      setSyncProgress({ ...data, status: 'completed' });
      setTimeout(() => setSyncProgress(null), 5000);
    });

    socket.on('sync:error', (data: any) => {
      console.log('Sync error:', data);
      setSyncProgress({ ...data, status: 'failed' });
      setTimeout(() => setSyncProgress(null), 5000);
    });

    socket.on('joined_library', (data: any) => {
      console.log('Successfully joined library room:', data);
    });

    socket.on('left_library', (data: any) => {
      console.log('Successfully left library room:', data);
    });

    socket.on('library_updated', (data: { libraryId: string; action: string }) => {
      console.log('Library updated:', data);
      // This event can be used to trigger React Query cache invalidation
      // The consuming components should listen for this via the useSocket hook
    });

    socket.on('connect_error', (error) => {
      console.error('Socket connection error:', error);
      console.error('Socket URL was:', socketUrl);
      console.error('Auth token:', token || 'anonymous');
      setConnected(false);
    });

    return () => {
      socket.disconnect();
      socketRef.current = null;
      setConnected(false);
      setSyncProgress(null);
    };
  }, [token, user]);

  const emit = (event: string, data?: any) => {
    if (socketRef.current && connected) {
      socketRef.current.emit(event, data);
    }
  };

  const joinLibrary = (libraryId: string) => {
    if (socketRef.current && connected) {
      console.log('Joining library room:', libraryId);
      socketRef.current.emit('join_library', { library_id: libraryId });
    }
  };

  const leaveLibrary = (libraryId: string) => {
    if (socketRef.current && connected) {
      console.log('Leaving library room:', libraryId);
      socketRef.current.emit('leave_library', { library_id: libraryId });
    }
  };

  return {
    socket: socketRef.current,
    connected,
    syncProgress,
    emit,
    joinLibrary,
    leaveLibrary,
  };
}

// Hook for components that need to listen to specific socket events
export function useSocketEvent(event: string, handler: (data: any) => void) {
  const { socket } = useSocket();

  useEffect(() => {
    if (!socket) return;

    socket.on(event, handler);

    return () => {
      socket.off(event, handler);
    };
  }, [socket, event, handler]);
}

// Hook specifically for sync progress tracking
export function useSyncProgress(libraryIds: string[] = []) {
  const { connected, syncProgress, joinLibrary } = useSocket();

  useEffect(() => {
    if (connected && libraryIds.length > 0) {
      libraryIds.forEach(libraryId => {
        joinLibrary(libraryId);
      });
    }
  }, [connected, libraryIds, joinLibrary]);

  return syncProgress;
}