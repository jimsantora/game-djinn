import { useEffect, useRef, useState } from 'react';
import { io, Socket } from 'socket.io-client';
import { useAuth } from '@/contexts/AuthContext';

interface SyncProgress {
  platform: string;
  status: 'starting' | 'running' | 'completed' | 'failed';
  progress: number;
  totalGames?: number;
  processedGames?: number;
  currentGame?: string;
  error?: string;
}

interface UseSocketReturn {
  socket: Socket | null;
  connected: boolean;
  syncProgress: SyncProgress | null;
  emit: (event: string, data?: any) => void;
}

export function useSocket(): UseSocketReturn {
  const { user, token } = useAuth();
  const socketRef = useRef<Socket | null>(null);
  const [connected, setConnected] = useState(false);
  const [syncProgress, setSyncProgress] = useState<SyncProgress | null>(null);

  useEffect(() => {
    // Only connect if user is authenticated (in auth-enabled mode)
    if (!token && user) return;

    const socket = io(import.meta.env.VITE_SOCKET_URL || import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000', {
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
    });

    socket.on('disconnect', () => {
      console.log('Socket disconnected');
      setConnected(false);
      setSyncProgress(null);
    });

    socket.on('sync_progress', (data: SyncProgress) => {
      console.log('Sync progress:', data);
      setSyncProgress(data);
      
      // Clear progress after completion/failure
      if (data.status === 'completed' || data.status === 'failed') {
        setTimeout(() => setSyncProgress(null), 5000);
      }
    });

    socket.on('library_updated', (data: { libraryId: string; action: string }) => {
      console.log('Library updated:', data);
      // This event can be used to trigger React Query cache invalidation
      // The consuming components should listen for this via the useSocket hook
    });

    socket.on('connect_error', (error) => {
      console.error('Socket connection error:', error);
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

  return {
    socket: socketRef.current,
    connected,
    syncProgress,
    emit,
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