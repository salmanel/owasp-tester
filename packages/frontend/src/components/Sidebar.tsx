import { ShieldIcon, FileTextIcon, BarChart3Icon, UserIcon, SettingsIcon } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Separator } from '@/components/ui/separator';
import { useAppStore } from '@/stores/appStore';
import { cn } from '@/lib/utils';

interface SidebarProps {
  activeView: string;
  onViewChange: (view: string) => void;
}

export function Sidebar({ activeView, onViewChange }: SidebarProps) {
  const { sidebarCollapsed, mode } = useAppStore();
  const isAdvancedMode = mode === 'advanced';

  const navItems = [
    { id: 'soft', label: 'Soft Mode', icon: ShieldIcon },
    { id: 'advanced', label: 'Advanced Mode', icon: ShieldIcon },
    { id: 'logs', label: 'Logs', icon: FileTextIcon },
    { id: 'results', label: 'Results', icon: BarChart3Icon },
  ];

  return (
    <aside
      className={cn(
        `${isAdvancedMode ? 'bg-[hsl(0,0%,5%)] border-tertiary/30' : 'bg-secondary border-border'} border-r h-[calc(100vh-4rem)] flex flex-col transition-all duration-300 ease-in-out`,
        sidebarCollapsed ? 'w-0 lg:w-20' : 'w-64',
        'fixed lg:sticky top-16 left-0 z-40 overflow-hidden'
      )}
    >
      <nav className="flex-1 p-4 space-y-2">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeView === item.id;
          return (
            <Button
              key={item.id}
              variant={isActive ? 'default' : 'ghost'}
              className={cn(
                'w-full justify-start gap-3 font-normal',
                isActive
                  ? isAdvancedMode 
                    ? 'bg-tertiary text-tertiary-foreground hover:bg-tertiary/90'
                    : 'bg-accent text-accent-foreground hover:bg-accent/90'
                  : isAdvancedMode
                    ? 'bg-transparent text-navbar-text hover:bg-tertiary/20 hover:text-gray-100'
                    : 'bg-transparent text-navbar-text hover:bg-primary hover:text-primary-foreground',
                sidebarCollapsed && 'lg:justify-center'
              )}
              onClick={() => onViewChange(item.id)}
            >
              <Icon className="w-5 h-5 flex-shrink-0" strokeWidth={1.5} />
              {!sidebarCollapsed && <span>{item.label}</span>}
            </Button>
          );
        })}
      </nav>

      <Separator className="bg-border" />

      <div className="p-4 space-y-2">
        <Button
          variant="ghost"
          className={cn(
            'w-full justify-start gap-3 font-normal bg-transparent text-navbar-text',
            isAdvancedMode 
              ? 'hover:bg-tertiary/20 hover:text-gray-100'
              : 'hover:bg-primary hover:text-primary-foreground',
            sidebarCollapsed && 'lg:justify-center'
          )}
        >
          <UserIcon className="w-5 h-5 flex-shrink-0" strokeWidth={1.5} />
          {!sidebarCollapsed && <span>Profile</span>}
        </Button>
        <Button
          variant="ghost"
          className={cn(
            'w-full justify-start gap-3 font-normal bg-transparent text-navbar-text',
            isAdvancedMode 
              ? 'hover:bg-tertiary/20 hover:text-gray-100'
              : 'hover:bg-primary hover:text-primary-foreground',
            sidebarCollapsed && 'lg:justify-center'
          )}
        >
          <SettingsIcon className="w-5 h-5 flex-shrink-0" strokeWidth={1.5} />
          {!sidebarCollapsed && <span>Settings</span>}
        </Button>
      </div>
    </aside>
  );
}
