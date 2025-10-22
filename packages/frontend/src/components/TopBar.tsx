import { BellIcon, SettingsIcon, MenuIcon, ShieldIcon } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Avatar } from '@/components/ui/avatar';
import { useAppStore } from '@/stores/appStore';

export function TopBar() {
  const { toggleSidebar, mode, setMode } = useAppStore();

  return (
    <header className="h-16 bg-secondary border-b border-border flex items-center justify-between px-8 sticky top-0 z-50">
      <div className="flex items-center gap-6">
        <Button
          variant="ghost"
          size="icon"
          onClick={toggleSidebar}
          className="lg:hidden bg-transparent text-navbar-text hover:bg-primary hover:text-primary-foreground"
        >
          <MenuIcon className="w-6 h-6" strokeWidth={1.5} />
        </Button>
        <div className="flex items-center gap-3">
          <ShieldIcon className="w-8 h-8 text-accent" strokeWidth={1.5} />
          <h1 className="text-xl font-heading font-semibold text-navbar-text">
            OWASP Tester
          </h1>
        </div>
      </div>

      <div className="flex items-center gap-4">
        <div className="hidden md:flex items-center gap-2 bg-primary rounded-lg p-1">
          <Button
            variant={mode === 'soft' ? 'default' : 'ghost'}
            size="sm"
            onClick={() => setMode('soft')}
            className={
              mode === 'soft'
                ? 'bg-accent text-accent-foreground hover:bg-accent/90'
                : 'bg-transparent text-navbar-text hover:bg-primary hover:text-primary-foreground'
            }
          >
            Soft Mode
          </Button>
          <Button
            variant={mode === 'advanced' ? 'default' : 'ghost'}
            size="sm"
            onClick={() => setMode('advanced')}
            className={
              mode === 'advanced'
                ? 'bg-tertiary text-tertiary-foreground hover:bg-tertiary/90'
                : 'bg-transparent text-navbar-text hover:bg-primary hover:text-primary-foreground'
            }
          >
            Advanced Mode
          </Button>
        </div>

        <Button
          variant="ghost"
          size="icon"
          className="bg-transparent text-navbar-text hover:bg-primary hover:text-primary-foreground"
        >
          <BellIcon className="w-5 h-5" strokeWidth={1.5} />
        </Button>
        <Button
          variant="ghost"
          size="icon"
          className="bg-transparent text-navbar-text hover:bg-primary hover:text-primary-foreground"
        >
          <SettingsIcon className="w-5 h-5" strokeWidth={1.5} />
        </Button>
        <Avatar className="w-10 h-10 bg-accent text-accent-foreground">
          <div className="w-full h-full flex items-center justify-center text-sm font-medium">
            U
          </div>
        </Avatar>
      </div>
    </header>
  );
}
