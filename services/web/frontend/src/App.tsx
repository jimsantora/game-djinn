import { Outlet } from "react-router-dom";
import { Navigation } from "./components/Navigation";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { AuthProvider, useRequireAuth } from "./contexts/AuthContext";
import { NotificationProvider } from "./components/NotificationProvider";
import { SyncProgressIndicator } from "./components/SyncProgressIndicator";
import { useRealtimeSync } from "./hooks/useRealtimeSync";
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
  const auth = useRequireAuth();
  
  // Initialize real-time sync for cache invalidation
  useRealtimeSync();

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

  return (
    <div className="min-h-screen bg-background">
      <Navigation />
      <main className="container mx-auto px-4 py-8">
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