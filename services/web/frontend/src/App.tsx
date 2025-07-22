import React from "react";
import { Outlet, useLocation } from "react-router-dom";
import { Navigation } from "./components/Navigation";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { AuthProvider, useAuth } from "./contexts/AuthContext";
import { NotificationProvider } from "./components/NotificationProvider";
import { SyncProgressIndicator } from "./components/SyncProgressIndicator";
import { useRealtimeSync } from "./hooks/useRealtimeSync";
import { useSocket } from "./hooks/useSocket";
import { Toaster } from "sonner";
import { Gamepad2 } from "lucide-react";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

function AppContent() {
  const location = useLocation();
  const isLoginPage = location.pathname === '/login';
  
  // Always call ALL hooks at the top level - before any returns
  const basicAuth = useAuth();
  const { syncProgress, connected } = useSocket();
  
  // Initialize real-time sync for cache invalidation
  useRealtimeSync();
  
  // For login page, use basic auth; for other pages, check authentication
  const auth = basicAuth;
  
  // Handle redirect logic manually for non-login pages
  React.useEffect(() => {
    if (!isLoginPage && auth.authEnabled === true && !auth.isLoading && !auth.isAuthenticated) {
      window.location.href = '/login';
    }
  }, [isLoginPage, auth.authEnabled, auth.isLoading, auth.isAuthenticated]);

  if (auth.isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="text-center">
          <Gamepad2 className="h-12 w-12 text-primary mx-auto mb-4 animate-pulse" />
          <p className="text-muted-foreground">Loading Game Djinn...</p>
        </div>
      </div>
    );
  }

  // For login page, render without navigation
  if (isLoginPage) {
    return (
      <div className="min-h-screen bg-background">
        <Outlet />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <Navigation />
      <main className="container mx-auto px-4 py-8">
        {/* Debug info */}
        <div className="mb-4 p-2 bg-gray-100 rounded text-xs">
          Socket: {connected ? '✅ Connected' : '❌ Disconnected'} | 
          Sync: {syncProgress ? `Active (${syncProgress.status})` : 'None'}
        </div>
        
        {/* Sync Progress Indicator */}
        <div className="mb-6">
          <SyncProgressIndicator />
        </div>
        <Outlet />
      </main>
    </div>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <NotificationProvider>
          <AppContent />
          <Toaster 
            position="top-right" 
            expand={false} 
            richColors 
            closeButton
          />
        </NotificationProvider>
      </AuthProvider>
    </QueryClientProvider>
  );
}

export default App;