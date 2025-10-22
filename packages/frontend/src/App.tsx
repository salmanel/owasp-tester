import { useState, useEffect } from 'react';
import { TopBar } from '@/components/TopBar';
import { Sidebar } from '@/components/Sidebar';
import { SoftPanel } from '@/components/SoftPanel';
import { AdvancedPanel } from '@/components/AdvancedPanel';
import { LogsView } from '@/components/LogsView';
import { ResultsView } from '@/components/ResultsView';
import { Toaster } from '@/components/ui/toaster';
import { useAppStore } from '@/stores/appStore';

function App() {
  const { mode, sidebarCollapsed, setSidebarCollapsed } = useAppStore();
  const [activeView, setActiveView] = useState<string>(mode);

  useEffect(() => {
    setActiveView(mode);
  }, [mode]);

  useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth < 1024) {
        setSidebarCollapsed(true);
      } else {
        setSidebarCollapsed(false);
      }
    };

    handleResize();
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, [setSidebarCollapsed]);

  useEffect(() => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }, [activeView]);

  const renderMainContent = () => {
    switch (activeView) {
      case 'soft':
        return <SoftPanel />;
      case 'advanced':
        return <AdvancedPanel />;
      case 'logs':
        return <LogsView />;
      case 'results':
        return <ResultsView />;
      default:
        return <SoftPanel />;
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <TopBar />
      <div className="flex">
        <Sidebar activeView={activeView} onViewChange={setActiveView} />
        <main className="flex-1 p-8 lg:p-12 min-h-[calc(100vh-4rem)]">
          <div className="max-w-7xl mx-auto">
            {renderMainContent()}
          </div>
        </main>
      </div>
      <Toaster />
      {sidebarCollapsed && (
        <div
          className="fixed inset-0 bg-black/50 lg:hidden z-30"
          onClick={() => setSidebarCollapsed(true)}
        />
      )}
    </div>
  );
}

export default App;
