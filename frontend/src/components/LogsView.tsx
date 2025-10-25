import { FileTextIcon, DownloadIcon } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

export function LogsView() {
  const mockLogs = [
    { id: 1, timestamp: new Date().toISOString(), level: 'info', message: 'Test initiated for https://example.com' },
    { id: 2, timestamp: new Date().toISOString(), level: 'warning', message: 'Potential XSS vulnerability detected' },
    { id: 3, timestamp: new Date().toISOString(), level: 'error', message: 'Connection timeout on endpoint /api/users' },
    { id: 4, timestamp: new Date().toISOString(), level: 'info', message: 'Scan completed successfully' },
  ];

  const getLevelColor = (level: string) => {
    switch (level) {
      case 'error':
        return 'text-error';
      case 'warning':
        return 'text-warning';
      case 'info':
        return 'text-accent';
      default:
        return 'text-gray-400';
    }
  };

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div className="space-y-2">
          <h2 className="text-3xl font-heading font-semibold text-hero-text flex items-center gap-3">
            <FileTextIcon className="w-8 h-8" strokeWidth={1.5} />
            Test Logs
          </h2>
          <p className="text-lg text-gray-300">
            Detailed execution logs and system messages
          </p>
        </div>
        <Button
          variant="outline"
          className="bg-transparent border-border text-foreground hover:bg-primary hover:text-primary-foreground font-normal"
        >
          <DownloadIcon className="w-5 h-5 mr-2" strokeWidth={1.5} />
          Export Logs
        </Button>
      </div>

      <Card className="bg-card border-border">
        <CardHeader>
          <CardTitle className="text-card-foreground">Recent Activity</CardTitle>
          <CardDescription className="text-gray-300">
            System logs from recent test executions
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3 font-mono text-sm">
            {mockLogs.map((log) => (
              <div
                key={log.id}
                className="p-4 bg-primary rounded-lg border border-border flex items-start gap-4"
              >
                <span className="text-gray-400 whitespace-nowrap">
                  {new Date(log.timestamp).toLocaleTimeString()}
                </span>
                <span className={`uppercase font-semibold ${getLevelColor(log.level)} min-w-20`}>
                  [{log.level}]
                </span>
                <span className="text-primary-foreground flex-1">{log.message}</span>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
