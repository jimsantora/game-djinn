import { useQueryClient } from '@tanstack/react-query';
import { useSocketEvent } from './useSocket';

/**
 * Hook to manage real-time cache invalidation based on Socket.IO events
 * This ensures the UI stays in sync with server-side changes
 */
export function useRealtimeSync() {
  const queryClient = useQueryClient();

  // Library updates - invalidate library-related queries
  useSocketEvent('library_updated', (data: { libraryId: string; action: string }) => {
    console.log('Invalidating library queries due to update:', data);
    
    // Invalidate all library queries
    queryClient.invalidateQueries({ queryKey: ['libraries'] });
    
    // Invalidate specific library if ID is provided
    if (data.libraryId) {
      queryClient.invalidateQueries({ queryKey: ['library', data.libraryId] });
    }
    
    // If games were affected, invalidate game queries
    if (data.action === 'game_added' || data.action === 'game_updated' || data.action === 'sync_complete') {
      queryClient.invalidateQueries({ queryKey: ['games'] });
    }
  });

  // Sync completion - refresh all relevant data
  useSocketEvent('sync_complete', (data: { platform: string; libraryId?: string }) => {
    console.log('Invalidating queries due to sync completion:', data);
    
    // Invalidate all library and game queries after sync
    queryClient.invalidateQueries({ queryKey: ['libraries'] });
    queryClient.invalidateQueries({ queryKey: ['games'] });
    queryClient.invalidateQueries({ queryKey: ['platforms'] });
    
    if (data.libraryId) {
      queryClient.invalidateQueries({ queryKey: ['library', data.libraryId] });
    }
  });

  // Game updates - invalidate game-related queries
  useSocketEvent('game_updated', (data: { gameId: string; libraryId?: string }) => {
    console.log('Invalidating game queries due to update:', data);
    
    queryClient.invalidateQueries({ queryKey: ['games'] });
    
    if (data.gameId) {
      queryClient.invalidateQueries({ queryKey: ['game', data.gameId] });
    }
    
    if (data.libraryId) {
      queryClient.invalidateQueries({ queryKey: ['library', data.libraryId] });
    }
  });

  // Achievement unlocked - refresh game and user data
  useSocketEvent('achievement_unlocked', (data: { gameId: string; libraryId: string }) => {
    console.log('Invalidating queries due to achievement unlock:', data);
    
    queryClient.invalidateQueries({ queryKey: ['game', data.gameId] });
    queryClient.invalidateQueries({ queryKey: ['library', data.libraryId] });
  });

  // Platform changes - refresh platform data
  useSocketEvent('platform_updated', () => {
    console.log('Invalidating platform queries due to update');
    queryClient.invalidateQueries({ queryKey: ['platforms'] });
  });
}