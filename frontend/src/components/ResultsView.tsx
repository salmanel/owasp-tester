import { BarChart3Icon, DownloadIcon, FilterIcon } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { useAppStore } from '@/stores/appStore';

export function ResultsView() {
  const { results } = useAppStore();

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical':
        return 'bg-error text-white';
      case 'high':
        return 'bg-tertiary text-tertiary-foreground';
      case 'medium':
        return 'bg-warning text-gray-900';
      case 'low':
        return 'bg-success text-white';
      default:
        return 'bg-muted text-muted-foreground';
    }
  };

  const severityCounts = results.reduce((acc, result) => {
    acc[result.severity] = (acc[result.severity] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div className="space-y-2">
          <h2 className="text-3xl font-heading font-semibold text-hero-text flex items-center gap-3">
            <BarChart3Icon className="w-8 h-8" strokeWidth={1.5} />
            Test Results
          </h2>
          <p className="text-lg text-gray-300">
            Comprehensive vulnerability analysis and statistics
          </p>
        </div>
        <div className="flex gap-2">
          <Button
            variant="outline"
            className="bg-transparent border-border text-foreground hover:bg-primary hover:text-primary-foreground font-normal"
          >
            <FilterIcon className="w-5 h-5 mr-2" strokeWidth={1.5} />
            FilterIcon
          </Button>
          <Button
            variant="outline"
            className="bg-transparent border-border text-foreground hover:bg-primary hover:text-primary-foreground font-normal"
          >
            <DownloadIcon className="w-5 h-5 mr-2" strokeWidth={1.5} />
            Export
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card className="bg-card border-border">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-normal text-gray-300">Total Vulnerabilities</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-heading font-semibold text-card-foreground">{results.length}</p>
          </CardContent>
        </Card>

        <Card className="bg-card border-border">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-normal text-gray-300">Critical</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-heading font-semibold text-error">{severityCounts.critical || 0}</p>
          </CardContent>
        </Card>

        <Card className="bg-card border-border">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-normal text-gray-300">High</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-heading font-semibold text-tertiary">{severityCounts.high || 0}</p>
          </CardContent>
        </Card>

        <Card className="bg-card border-border">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-normal text-gray-300">Medium & Low</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-heading font-semibold text-warning">
              {(severityCounts.medium || 0) + (severityCounts.low || 0)}
            </p>
          </CardContent>
        </Card>
      </div>

      <Card className="bg-card border-border">
        <CardHeader>
          <CardTitle className="text-card-foreground">All Vulnerabilities</CardTitle>
          <CardDescription className="text-gray-300">
            Complete list of detected security issues
          </CardDescription>
        </CardHeader>
        <CardContent>
          {results.length > 0 ? (
            <div className="space-y-4">
              {results.map((result) => (
                <div
                  key={result.id}
                  className="p-4 bg-primary rounded-lg border border-border space-y-3"
                >
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1 space-y-2">
                      <div className="flex items-center gap-3">
                        <p className="font-medium text-primary-foreground">
                          {result.vulnerability}
                        </p>
                        <Badge className={getSeverityColor(result.severity)}>
                          {result.severity}
                        </Badge>
                      </div>
                      <p className="text-sm text-gray-300 font-mono">{result.url}</p>
                      {result.payload && (
                        <p className="text-sm text-gray-400 font-mono">
                          Payload: {result.payload}
                        </p>
                      )}
                    </div>
                  </div>
                  <p className="text-xs text-gray-500">
                    Detected: {new Date(result.timestamp).toLocaleString()}
                  </p>
                </div>
              ))}
            </div>
          ) : (
            <div className="py-12 text-center">
              <p className="text-gray-400">No vulnerabilities recorded yet. Run tests to populate results.</p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
