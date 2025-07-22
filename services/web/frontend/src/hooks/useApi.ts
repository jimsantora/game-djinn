import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { platformsApi, gamesApi, librariesApi } from '@/lib/api';
import { useAuth } from '@/contexts/AuthContext';

// Platforms hooks
export function usePlatforms(enabledOnly = true) {
  const { isAuthenticated } = useAuth();
  
  return useQuery({
    queryKey: ['platforms', enabledOnly],
    queryFn: () => platformsApi.list(enabledOnly),
    enabled: isAuthenticated,
    select: (response) => response.data,
  });
}

// Games hooks
export function useGames(page = 1, limit = 20) {
  const { isAuthenticated } = useAuth();
  
  return useQuery({
    queryKey: ['games', page, limit],
    queryFn: () => gamesApi.list(page, limit),
    enabled: isAuthenticated,
    select: (response) => response.data,
  });
}

export function useGameSearch(query: string, filters: Record<string, any> = {}) {
  const { isAuthenticated } = useAuth();
  
  return useQuery({
    queryKey: ['games', 'search', query, filters],
    queryFn: () => gamesApi.search(query, filters),
    enabled: isAuthenticated && query.length > 0,
    select: (response) => response.data,
  });
}

export function useGame(gameId: string, libraryId?: string) {
  const { isAuthenticated } = useAuth();
  
  return useQuery({
    queryKey: ['games', gameId, libraryId],
    queryFn: () => gamesApi.get(gameId, libraryId),
    enabled: isAuthenticated && !!gameId,
    select: (response) => response.data,
  });
}

// Libraries hooks
export function useLibraries(page = 1, limit = 20) {
  const { isAuthenticated } = useAuth();
  
  return useQuery({
    queryKey: ['libraries', page, limit],
    queryFn: () => librariesApi.list(page, limit),
    enabled: isAuthenticated,
    select: (response) => response.data,
  });
}

export function useCreateLibrary() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: librariesApi.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['libraries'] });
    },
  });
}

export function useUpdateLibrary() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ libraryId, data }: { libraryId: string; data: any }) =>
      librariesApi.update(libraryId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['libraries'] });
    },
  });
}

export function useDeleteLibrary() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: librariesApi.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['libraries'] });
    },
  });
}

export function useSyncLibrary() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: librariesApi.sync,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['libraries'] });
      queryClient.invalidateQueries({ queryKey: ['games'] });
    },
  });
}

export function useSyncStatus(libraryId: string | null) {
  return useQuery({
    queryKey: ['sync-status', libraryId],
    queryFn: () => librariesApi.syncStatus(libraryId!),
    enabled: !!libraryId,
    refetchInterval: 5000, // Check every 5 seconds
  });
}

export function useCancelSync() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: librariesApi.cancelSync,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['libraries'] });
      queryClient.invalidateQueries({ queryKey: ['sync-status'] });
    },
  });
}