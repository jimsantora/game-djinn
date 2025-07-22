import { Progress } from '@/components/ui/progress';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { useSocket } from '@/hooks/useSocket';
import { 
  Loader2, 
  CheckCircle, 
  XCircle, 
  Download,
  Gamepad2
} from 'lucide-react';

export function SyncProgressIndicator() {
  const { syncProgress } = useSocket();

  // Debug: Always show component state
  console.log('SyncProgressIndicator - syncProgress:', syncProgress);

  if (!syncProgress) {
    // Debug element to verify component is mounted
    return (
      <div className="hidden">
        {/* This div verifies the component is mounted but no sync is active */}
      </div>
    );
  }

  const getStatusIcon = () => {
    switch (syncProgress.status) {
      case 'starting':
      case 'running':
      case 'syncing':
        return <Loader2 className="h-4 w-4 animate-spin text-blue-500" />;
      case 'completed':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'failed':
        return <XCircle className="h-4 w-4 text-red-500" />;
      default:
        return <Download className="h-4 w-4 text-gray-500" />;
    }
  };

  const getStatusColor = () => {
    switch (syncProgress.status) {
      case 'starting':
      case 'running':
      case 'syncing':
        return 'bg-blue-50 border-blue-200';
      case 'completed':
        return 'bg-green-50 border-green-200';
      case 'failed':
        return 'bg-red-50 border-red-200';
      default:
        return 'bg-gray-50 border-gray-200';
    }
  };

  const getStatusText = () => {
    const message = (syncProgress as any).message;
    switch (syncProgress.status) {
      case 'starting':
        return message || 'Starting sync...';
      case 'running':
      case 'syncing':
        return message || 'Syncing library...';
      case 'completed':
        return message || 'Sync completed!';
      case 'failed':
        return message || 'Sync failed';
      default:
        return message || 'Syncing...';
    }
  };

  return (
    <Card className={`${getStatusColor()} transition-all duration-300`}>
      <CardContent className="p-4">
        <div className="space-y-3">
          {/* Header */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              {getStatusIcon()}
              <span className="font-medium text-sm">{getStatusText()}</span>
            </div>
            {syncProgress.platform && (
              <Badge variant="outline" className="text-xs">
                {syncProgress.platform.toUpperCase()}
              </Badge>
            )}
          </div>

          {/* Progress Bar */}
          {(syncProgress.status === 'running' || syncProgress.status === 'syncing') && (
            <div className="space-y-2">
              <div className="flex justify-between text-xs text-muted-foreground">
                <span>
                  {syncProgress.processedGames || 0} / {syncProgress.totalGames || 0} games
                </span>
                <span>{Math.round(syncProgress.progress)}%</span>
              </div>
              <Progress value={syncProgress.progress} className="h-2" />
            </div>
          )}

          {/* Current Game */}
          {syncProgress.currentGame && (syncProgress.status === 'running' || syncProgress.status === 'syncing') && (
            <div className="flex items-center gap-2 text-xs text-muted-foreground">
              <Gamepad2 className="h-3 w-3" />
              <span>Processing: {syncProgress.currentGame}</span>
            </div>
          )}

          {/* Error Message */}
          {syncProgress.error && syncProgress.status === 'failed' && (
            <div className="text-xs text-red-600 bg-red-50 p-2 rounded border">
              {syncProgress.error}
            </div>
          )}

          {/* Completion Summary */}
          {syncProgress.status === 'completed' && syncProgress.totalGames && (
            <div className="text-xs text-green-600">
              Successfully synced {syncProgress.totalGames} games
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}