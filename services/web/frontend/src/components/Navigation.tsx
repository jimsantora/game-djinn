import { Link, useLocation } from "react-router-dom";
import { Home, Library, Gamepad2, Monitor, Settings, LogOut, User } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/contexts/AuthContext";
import { ConnectionStatus } from "@/components/ConnectionStatus";

export function Navigation() {
  const location = useLocation();
  const { authEnabled, isAuthenticated, user, logout } = useAuth();

  const navItems = [
    { path: "/", label: "Dashboard", icon: Home },
    { path: "/libraries", label: "Libraries", icon: Library },
    { path: "/games", label: "Games", icon: Gamepad2 },
    { path: "/platforms", label: "Platforms", icon: Monitor },
  ];

  const handleLogout = () => {
    logout();
  };

  return (
    <nav className="bg-card shadow-sm border-b">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center space-x-8">
            <Link to="/" className="flex items-center space-x-2">
              <Gamepad2 className="h-8 w-8 text-primary" />
              <span className="text-xl font-bold">Game Djinn</span>
            </Link>
            
            <div className="hidden md:flex space-x-6">
              {navItems.map(({ path, label, icon: Icon }) => (
                <Link
                  key={path}
                  to={path}
                  className={`flex items-center space-x-1 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                    location.pathname === path
                      ? "bg-accent text-accent-foreground"
                      : "text-muted-foreground hover:text-foreground hover:bg-accent"
                  }`}
                >
                  <Icon className="h-4 w-4" />
                  <span>{label}</span>
                </Link>
              ))}
            </div>
          </div>
          
          <div className="flex items-center space-x-4">
            {/* Connection Status */}
            <ConnectionStatus showLabel={false} variant="icon" />
            
            {authEnabled && isAuthenticated && user && (
              <div className="flex items-center space-x-3">
                <div className="flex items-center space-x-2 text-sm">
                  <User className="h-4 w-4" />
                  <span className="text-muted-foreground">{user.email}</span>
                </div>
                <Button variant="ghost" size="sm" onClick={handleLogout}>
                  <LogOut className="h-4 w-4 mr-1" />
                  Logout
                </Button>
              </div>
            )}
            
            {!authEnabled && (
              <div className="text-sm text-muted-foreground">
                Auth disabled
              </div>
            )}
            
            <Button variant="ghost" size="sm">
              <Settings className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </div>
    </nav>
  );
}