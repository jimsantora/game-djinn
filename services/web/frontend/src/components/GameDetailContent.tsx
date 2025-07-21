import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { GameListItem } from '@/lib/api';
import { 
  Clock, 
  Trophy, 
  Image, 
  Video, 
  Monitor, 
  HardDrive,
  Cpu,
  MemoryStick,
  Star,
  ChevronRight
} from 'lucide-react';

interface GameDetailContentProps {
  game: GameListItem;
  showUserData?: boolean;
}

export function GameDetailContent({ game, showUserData = false }: GameDetailContentProps) {
  const formatPlaytime = (hours: number) => {
    if (hours < 1) return `${Math.round(hours * 60)} minutes`;
    if (hours < 100) return `${Math.round(hours)} hours`;
    return `${Math.round(hours)} hours`;
  };

  const mockSystemRequirements = {
    minimum: {
      os: "Windows 10 64-bit",
      processor: "Intel Core i5-8400 / AMD Ryzen 5 2600",
      memory: "8 GB RAM",
      graphics: "NVIDIA GTX 1060 6GB / AMD RX 580 8GB",
      directx: "Version 12",
      storage: "50 GB available space"
    },
    recommended: {
      os: "Windows 11 64-bit",
      processor: "Intel Core i7-10700K / AMD Ryzen 7 3700X",
      memory: "16 GB RAM",
      graphics: "NVIDIA RTX 3070 / AMD RX 6700 XT",
      directx: "Version 12",
      storage: "50 GB available space (SSD recommended)"
    }
  };

  const mockScreenshots = [
    { id: '1', url: '/api/placeholder/800/450', caption: 'Main gameplay' },
    { id: '2', url: '/api/placeholder/800/450', caption: 'Character customization' },
    { id: '3', url: '/api/placeholder/800/450', caption: 'Combat system' },
    { id: '4', url: '/api/placeholder/800/450', caption: 'World exploration' },
  ];

  const mockAchievements = [
    { id: '1', name: 'First Steps', description: 'Complete the tutorial', unlocked: true, rarity: 95 },
    { id: '2', name: 'Explorer', description: 'Visit 10 different locations', unlocked: true, rarity: 78 },
    { id: '3', name: 'Master Fighter', description: 'Win 100 battles', unlocked: false, rarity: 23 },
    { id: '4', name: 'Completionist', description: 'Complete all side quests', unlocked: false, rarity: 8 },
    { id: '5', name: 'Speed Runner', description: 'Complete the game in under 10 hours', unlocked: false, rarity: 2 },
  ];

  return (
    <div className="space-y-6">
      <Tabs defaultValue="overview" className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="media">Media</TabsTrigger>
          <TabsTrigger value="achievements">Achievements</TabsTrigger>
          <TabsTrigger value="system">System</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-6">
          {/* Game Stats */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {/* Playtime Info */}
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Playtime</CardTitle>
                <Clock className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {showUserData && game.user_data?.playtime_minutes ? (
                    <div className="text-2xl font-bold">
                      {formatPlaytime(game.user_data.playtime_minutes / 60)}
                    </div>
                  ) : (
                    <div className="text-2xl font-bold text-muted-foreground">Not played</div>
                  )}
                  <div className="text-xs text-muted-foreground space-y-1">
                    <div>Main Story: ~25 hours</div>
                    <div>Main + Extras: ~45 hours</div>
                    <div>Completionist: ~80 hours</div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Achievement Progress */}
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Achievements</CardTitle>
                <Trophy className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className="text-2xl font-bold">
                    {showUserData ? `${mockAchievements.filter(a => a.unlocked).length}/${mockAchievements.length}` : `${mockAchievements.length} total`}
                  </div>
                  {showUserData && (
                    <>
                      <Progress 
                        value={(mockAchievements.filter(a => a.unlocked).length / mockAchievements.length) * 100} 
                        className="w-full" 
                      />
                      <div className="text-xs text-muted-foreground">
                        {Math.round((mockAchievements.filter(a => a.unlocked).length / mockAchievements.length) * 100)}% complete
                      </div>
                    </>
                  )}
                </div>
              </CardContent>
            </Card>

            {/* Content Rating */}
            {game.esrb_rating && (
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Content Rating</CardTitle>
                  <Star className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    <div className="text-2xl font-bold">{game.esrb_rating}</div>
                    {game.esrb_descriptors && game.esrb_descriptors.length > 0 && (
                      <div className="space-y-1">
                        {game.esrb_descriptors.slice(0, 3).map((descriptor) => (
                          <Badge key={descriptor} variant="outline" className="text-xs">
                            {descriptor}
                          </Badge>
                        ))}
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            )}
          </div>

          {/* Detailed Description */}
          <Card>
            <CardHeader>
              <CardTitle>About This Game</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <p className="text-muted-foreground leading-relaxed">
                  {game.description || "No detailed description available for this game."}
                </p>
                
                {/* Key Features - Mock data */}
                <div>
                  <h4 className="font-semibold mb-2">Key Features:</h4>
                  <ul className="space-y-1 text-sm text-muted-foreground">
                    <li className="flex items-center gap-2">
                      <ChevronRight className="h-3 w-3" />
                      Immersive single-player campaign
                    </li>
                    <li className="flex items-center gap-2">
                      <ChevronRight className="h-3 w-3" />
                      Advanced character customization
                    </li>
                    <li className="flex items-center gap-2">
                      <ChevronRight className="h-3 w-3" />
                      Dynamic weather and day/night cycle
                    </li>
                    <li className="flex items-center gap-2">
                      <ChevronRight className="h-3 w-3" />
                      Extensive skill progression system
                    </li>
                  </ul>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="media" className="space-y-6">
          {/* Screenshots */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Image className="h-5 w-5" />
                Screenshots
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {mockScreenshots.map((screenshot) => (
                  <div key={screenshot.id} className="space-y-2">
                    <div className="aspect-video bg-gradient-to-br from-gray-100 to-gray-200 rounded-lg overflow-hidden">
                      <div className="w-full h-full flex items-center justify-center">
                        <Image className="h-12 w-12 text-gray-400" />
                      </div>
                    </div>
                    <p className="text-sm text-muted-foreground">{screenshot.caption}</p>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Videos */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Video className="h-5 w-5" />
                Videos
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <div className="aspect-video bg-gradient-to-br from-gray-100 to-gray-200 rounded-lg overflow-hidden">
                    <div className="w-full h-full flex items-center justify-center">
                      <Video className="h-12 w-12 text-gray-400" />
                    </div>
                  </div>
                  <p className="text-sm text-muted-foreground">Launch Trailer</p>
                </div>
                <div className="space-y-2">
                  <div className="aspect-video bg-gradient-to-br from-gray-100 to-gray-200 rounded-lg overflow-hidden">
                    <div className="w-full h-full flex items-center justify-center">
                      <Video className="h-12 w-12 text-gray-400" />
                    </div>
                  </div>
                  <p className="text-sm text-muted-foreground">Gameplay Overview</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="achievements" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Trophy className="h-5 w-5" />
                Achievements
                <Badge variant="secondary">{mockAchievements.length}</Badge>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {mockAchievements.map((achievement) => (
                  <div
                    key={achievement.id}
                    className={`flex items-center gap-4 p-4 rounded-lg border ${
                      achievement.unlocked ? 'bg-green-50 border-green-200' : 'bg-gray-50'
                    }`}
                  >
                    <div className={`p-2 rounded-full ${
                      achievement.unlocked ? 'bg-green-100 text-green-600' : 'bg-gray-200 text-gray-400'
                    }`}>
                      <Trophy className="h-5 w-5" />
                    </div>
                    <div className="flex-1">
                      <h4 className="font-semibold">{achievement.name}</h4>
                      <p className="text-sm text-muted-foreground">{achievement.description}</p>
                    </div>
                    <div className="text-right">
                      <div className="text-sm font-medium">
                        {achievement.rarity}% of players
                      </div>
                      <div className="text-xs text-muted-foreground">
                        {achievement.unlocked ? 'Unlocked' : 'Locked'}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="system" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Minimum Requirements */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Monitor className="h-5 w-5" />
                  Minimum Requirements
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex items-center gap-3">
                    <Monitor className="h-4 w-4 text-muted-foreground" />
                    <div>
                      <div className="text-sm font-medium">OS</div>
                      <div className="text-sm text-muted-foreground">{mockSystemRequirements.minimum.os}</div>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <Cpu className="h-4 w-4 text-muted-foreground" />
                    <div>
                      <div className="text-sm font-medium">Processor</div>
                      <div className="text-sm text-muted-foreground">{mockSystemRequirements.minimum.processor}</div>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <MemoryStick className="h-4 w-4 text-muted-foreground" />
                    <div>
                      <div className="text-sm font-medium">Memory</div>
                      <div className="text-sm text-muted-foreground">{mockSystemRequirements.minimum.memory}</div>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <Monitor className="h-4 w-4 text-muted-foreground" />
                    <div>
                      <div className="text-sm font-medium">Graphics</div>
                      <div className="text-sm text-muted-foreground">{mockSystemRequirements.minimum.graphics}</div>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <HardDrive className="h-4 w-4 text-muted-foreground" />
                    <div>
                      <div className="text-sm font-medium">Storage</div>
                      <div className="text-sm text-muted-foreground">{mockSystemRequirements.minimum.storage}</div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Recommended Requirements */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Monitor className="h-5 w-5" />
                  Recommended Requirements
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex items-center gap-3">
                    <Monitor className="h-4 w-4 text-muted-foreground" />
                    <div>
                      <div className="text-sm font-medium">OS</div>
                      <div className="text-sm text-muted-foreground">{mockSystemRequirements.recommended.os}</div>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <Cpu className="h-4 w-4 text-muted-foreground" />
                    <div>
                      <div className="text-sm font-medium">Processor</div>
                      <div className="text-sm text-muted-foreground">{mockSystemRequirements.recommended.processor}</div>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <MemoryStick className="h-4 w-4 text-muted-foreground" />
                    <div>
                      <div className="text-sm font-medium">Memory</div>
                      <div className="text-sm text-muted-foreground">{mockSystemRequirements.recommended.memory}</div>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <Monitor className="h-4 w-4 text-muted-foreground" />
                    <div>
                      <div className="text-sm font-medium">Graphics</div>
                      <div className="text-sm text-muted-foreground">{mockSystemRequirements.recommended.graphics}</div>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <HardDrive className="h-4 w-4 text-muted-foreground" />
                    <div>
                      <div className="text-sm font-medium">Storage</div>
                      <div className="text-sm text-muted-foreground">{mockSystemRequirements.recommended.storage}</div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}