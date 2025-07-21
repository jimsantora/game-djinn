import { useState } from 'react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { usePlatforms, useCreateLibrary } from '@/hooks/useApi';
import { Plus } from 'lucide-react';

interface LibraryCreateDialogProps {
  children?: React.ReactNode;
  onSuccess?: () => void;
}

export function LibraryCreateDialog({ children, onSuccess }: LibraryCreateDialogProps) {
  const [open, setOpen] = useState(false);
  const [formData, setFormData] = useState({
    platform_id: '',
    user_identifier: '',
    display_name: '',
  });

  const { data: platforms, isLoading: platformsLoading } = usePlatforms(true);
  const createLibrary = useCreateLibrary();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      await createLibrary.mutateAsync(formData);
      setOpen(false);
      setFormData({
        platform_id: '',
        user_identifier: '',
        display_name: '',
      });
      onSuccess?.();
    } catch (error) {
      console.error('Failed to create library:', error);
    }
  };

  const handleChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const selectedPlatform = platforms?.find(p => p.platform_id === formData.platform_id);

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        {children || (
          <Button>
            <Plus className="h-4 w-4 mr-2" />
            Add Library
          </Button>
        )}
      </DialogTrigger>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Add New Library</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="platform">Platform</Label>
            <Select
              value={formData.platform_id}
              onValueChange={(value) => handleChange('platform_id', value)}
              disabled={platformsLoading}
            >
              <SelectTrigger>
                <SelectValue placeholder="Select a platform" />
              </SelectTrigger>
              <SelectContent>
                {platforms?.map((platform) => (
                  <SelectItem key={platform.platform_id} value={platform.platform_id}>
                    {platform.platform_name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label htmlFor="user_identifier">
              {selectedPlatform?.platform_code === 'steam' ? 'Steam ID' : 'User Identifier'}
            </Label>
            <Input
              id="user_identifier"
              value={formData.user_identifier}
              onChange={(e) => handleChange('user_identifier', e.target.value)}
              placeholder={
                selectedPlatform?.platform_code === 'steam'
                  ? 'Your Steam ID (e.g., 76561198000000000)'
                  : 'Your platform username or ID'
              }
              required
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="display_name">Display Name</Label>
            <Input
              id="display_name"
              value={formData.display_name}
              onChange={(e) => handleChange('display_name', e.target.value)}
              placeholder="Friendly name for this library"
              required
            />
          </div>

          <div className="flex justify-end space-x-2 pt-4">
            <Button
              type="button"
              variant="outline"
              onClick={() => setOpen(false)}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              disabled={createLibrary.isPending || !formData.platform_id}
            >
              {createLibrary.isPending ? 'Creating...' : 'Create Library'}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}