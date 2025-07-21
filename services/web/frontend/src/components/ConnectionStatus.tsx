import { Badge } from '@/components/ui/badge';
import { useSocket } from '@/hooks/useSocket';
import { Wifi, WifiOff } from 'lucide-react';

interface ConnectionStatusProps {
  showLabel?: boolean;
  variant?: 'badge' | 'icon';
}

export function ConnectionStatus({ 
  showLabel = true, 
  variant = 'badge' 
}: ConnectionStatusProps) {
  const { connected } = useSocket();

  if (variant === 'icon') {
    return (
      <div className="flex items-center gap-1">
        {connected ? (
          <Wifi className="h-4 w-4 text-green-500" />
        ) : (
          <WifiOff className="h-4 w-4 text-red-500" />
        )}
        {showLabel && (
          <span className={`text-xs ${connected ? 'text-green-600' : 'text-red-600'}`}>
            {connected ? 'Connected' : 'Disconnected'}
          </span>
        )}
      </div>
    );
  }

  return (
    <Badge 
      variant={connected ? 'default' : 'destructive'}
      className="flex items-center gap-1"
    >
      {connected ? (
        <Wifi className="h-3 w-3" />
      ) : (
        <WifiOff className="h-3 w-3" />
      )}
      {showLabel && (connected ? 'Live' : 'Offline')}
    </Badge>
  );
}