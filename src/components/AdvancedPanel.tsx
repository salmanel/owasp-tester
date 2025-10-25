import { useState } from 'react';
import { PlayIcon, ShieldAlertIcon, SettingsIcon, FileTextIcon, DownloadIcon } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Switch } from '@/components/ui/switch';
import { Textarea } from '@/components/ui/textarea';
import { Separator } from '@/components/ui/separator';
import { useAppStore, VulnerabilityResult } from '@/stores/appStore';
import { useToast } from '@/hooks/use-toast';

export function AdvancedPanel() {
  const [url, setUrl] = useState('');
  const [attackType, setAttackType] = useState('all');
  const [customPayloads, setCustomPayloads] = useState('');
  const [followRedirects, setFollowRedirects] = useState(true);
  const [crawlDepth, setCrawlDepth] = useState('1');
  const [timeout, setTimeout] = useState('30');
  const { results, addResults, setTestRunning, isTestRunning, setMode } = useAppStore();
  const { toast } = useToast();

  const handleRunTest = () => {
    if (!url) {
      toast({
        title: 'Error',
        description: 'Please enter a target URL',
        variant: 'destructive',
      });
      return;
    }

    setTestRunning(true);
    setMode('advanced');

    // Simulate advanced test execution
    setTimeout(() => {
      const mockResults: VulnerabilityResult[] = [
        {
          id: Math.random().toString(),
          url,
          vulnerability: 'Advanced XSS Detection',
          payload: customPayloads || '<img src=x onerror=alert(1)>',
          severity: 'critical',
          timestamp: new Date().toISOString(),
        },
        {
          id: Math.random().toString(),
          url: `${url}/api/users`,
          vulnerability: 'SQL Injection (Time-based)',
          payload: "' AND SLEEP(5)--",
          severity: 'high',
          timestamp: new Date().toISOString(),
        },
      ];

      addResults(mockResults);
      setTestRunning(false);

      toast({
        title: 'Advanced Test Complete',
        description: `Discovered ${mockResults.length} vulnerabilities with custom configuration`,
      });
    }, 5000);
  };

  return (
    <div className="space-y-8">
      <div className="space-y-2">
        <h2 className="text-3xl font-heading font-semibold text-hero-text flex items-center gap-3">
          <ShieldAlertIcon className="w-8 h-8 text-tertiary" strokeWidth={1.5} />
          Advanced Mode
        </h2>
        <p className="text-lg text-gray-300">
          Professional-grade testing with custom payloads and advanced configuration
        </p>
      </div>

      <Card className="bg-[hsl(0,0%,8%)] border-tertiary/30">
        <CardHeader>
          <CardTitle className="text-gray-100 flex items-center gap-2">
            <SettingsIcon className="w-5 h-5" strokeWidth={1.5} />
            Advanced Configuration
          </CardTitle>
          <CardDescription className="text-gray-300">
            Fine-tune your security assessment parameters
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="space-y-2">
            <Label htmlFor="adv-target-url" className="text-gray-100">
              Target URL
            </Label>
            <Input
              id="adv-target-url"
              type="url"
              placeholder="https://example.com"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              className="bg-[hsl(0,0%,12%)] border-tertiary/30 text-gray-100 placeholder:text-gray-500 focus-visible:ring-tertiary"
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="adv-attack-type" className="text-gray-100">
              Attack Vector
            </Label>
            <Select value={attackType} onValueChange={setAttackType}>
              <SelectTrigger
                id="adv-attack-type"
                className="bg-[hsl(0,0%,12%)] border-tertiary/30 text-gray-100 focus:ring-tertiary"
              >
                <SelectValue />
              </SelectTrigger>
              <SelectContent className="bg-[hsl(0,0%,8%)] border-tertiary/30">
                <SelectItem value="all">All Vectors</SelectItem>
                <SelectItem value="xss">XSS (All Variants)</SelectItem>
                <SelectItem value="sqli">SQL Injection (All Types)</SelectItem>
                <SelectItem value="xxe">XXE</SelectItem>
                <SelectItem value="ssrf">SSRF</SelectItem>
                <SelectItem value="rce">RCE</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <Separator className="bg-border" />

          <div className="space-y-2">
            <Label htmlFor="custom-payloads" className="text-gray-100">
              Custom Payloads (one per line)
            </Label>
            <Textarea
              id="custom-payloads"
              placeholder="<script>alert(document.cookie)</script>&#10;' OR '1'='1&#10;{{7*7}}"
              value={customPayloads}
              onChange={(e) => setCustomPayloads(e.target.value)}
              className="bg-[hsl(0,0%,12%)] border-tertiary/30 text-gray-100 placeholder:text-gray-500 font-mono text-sm min-h-32 focus-visible:ring-tertiary"
            />
          </div>

          <Separator className="bg-border" />

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-2">
              <Label htmlFor="crawl-depth" className="text-gray-100">
                Crawl Depth
              </Label>
              <Select value={crawlDepth} onValueChange={setCrawlDepth}>
                <SelectTrigger
                  id="crawl-depth"
                  className="bg-[hsl(0,0%,12%)] border-tertiary/30 text-gray-100 focus:ring-tertiary"
                >
                  <SelectValue />
                </SelectTrigger>
                <SelectContent className="bg-[hsl(0,0%,8%)] border-tertiary/30">
                  <SelectItem value="1">1 Level</SelectItem>
                  <SelectItem value="2">2 Levels</SelectItem>
                  <SelectItem value="3">3 Levels</SelectItem>
                  <SelectItem value="5">5 Levels</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="timeout" className="text-gray-100">
                Timeout (seconds)
              </Label>
              <Input
                id="timeout"
                type="number"
                value={timeout}
                onChange={(e) => setTimeout(e.target.value)}
                className="bg-[hsl(0,0%,12%)] border-tertiary/30 text-gray-100 focus-visible:ring-tertiary"
              />
            </div>
          </div>

          <div className="flex items-center justify-between p-4 bg-[hsl(0,0%,12%)] rounded-lg border border-tertiary/30">
            <div className="space-y-1">
              <Label htmlFor="follow-redirects" className="text-gray-100 font-medium">
                Follow Redirects
              </Label>
              <p className="text-sm text-gray-400">
                Automatically follow HTTP redirects during testing
              </p>
            </div>
            <Switch
              id="follow-redirects"
              checked={followRedirects}
              onCheckedChange={setFollowRedirects}
            />
          </div>

          <div className="space-y-3">
            <Button
              onClick={handleRunTest}
              disabled={isTestRunning}
              className="w-full bg-tertiary text-tertiary-foreground hover:bg-tertiary/90 font-medium"
            >
              <PlayIcon className="w-5 h-5 mr-2" strokeWidth={1.5} />
              {isTestRunning ? 'Running Advanced Test...' : 'Run Advanced Test'}
            </Button>

            {!isTestRunning && results.length > 0 && (
              <div className="grid grid-cols-2 gap-3">
                <Button
                  variant="outline"
                  onClick={() => {
                    // Generate HTML report
                    const htmlContent = `
                      <!DOCTYPE html>
                      <html>
                        <head>
                          <title>OWASP Advanced Test Report</title>
                          <style>
                            body { font-family: Arial, sans-serif; padding: 20px; background: #0a0a0a; color: #fff; }
                            h1 { color: #dc2626; }
                            .vulnerability { background: #1a1a1a; padding: 15px; margin: 10px 0; border-radius: 8px; border-left: 4px solid #dc2626; }
                            .severity { display: inline-block; padding: 4px 12px; border-radius: 4px; font-size: 12px; font-weight: bold; }
                            .critical { background: #dc2626; }
                            .high { background: #ef4444; }
                            .medium { background: #f59e0b; }
                            .low { background: #10b981; }
                            .config { background: #1a1a1a; padding: 15px; margin: 20px 0; border-radius: 8px; }
                          </style>
                        </head>
                        <body>
                          <h1>OWASP Advanced Security Test Report</h1>
                          <p>Generated: ${new Date().toLocaleString()}</p>
                          <div class="config">
                            <h3>Test Configuration</h3>
                            <p><strong>Attack Type:</strong> ${attackType}</p>
                            <p><strong>Crawl Depth:</strong> ${crawlDepth} levels</p>
                            <p><strong>Timeout:</strong> ${timeout}s</p>
                            <p><strong>Follow Redirects:</strong> ${followRedirects ? 'Yes' : 'No'}</p>
                            ${customPayloads ? `<p><strong>Custom Payloads:</strong> ${customPayloads.split('\n').length} payloads</p>` : ''}
                          </div>
                          <p>Total Vulnerabilities: ${results.length}</p>
                          <hr>
                          ${results.map(r => `
                            <div class="vulnerability">
                              <h3>${r.vulnerability} <span class="severity ${r.severity}">${r.severity.toUpperCase()}</span></h3>
                              <p><strong>URL:</strong> ${r.url}</p>
                              ${r.payload ? `<p><strong>Payload:</strong> <code>${r.payload}</code></p>` : ''}
                              <p><strong>Detected:</strong> ${new Date(r.timestamp).toLocaleString()}</p>
                            </div>
                          `).join('')}
                        </body>
                      </html>
                    `;
                    const blob = new Blob([htmlContent], { type: 'text/html' });
                    const url = URL.createObjectURL(blob);
                    window.open(url, '_blank');
                  }}
                  className="bg-transparent border-tertiary text-tertiary hover:bg-tertiary hover:text-tertiary-foreground"
                >
                  <FileTextIcon className="w-4 h-4 mr-2" strokeWidth={1.5} />
                  View HTML Report
                </Button>

                <Button
                  variant="outline"
                  onClick={() => {
                    // Download JSON report
                    const jsonReport = {
                      generatedAt: new Date().toISOString(),
                      mode: 'advanced',
                      configuration: {
                        attackType,
                        crawlDepth: parseInt(crawlDepth),
                        timeout: parseInt(timeout),
                        followRedirects,
                        customPayloads: customPayloads ? customPayloads.split('\n') : []
                      },
                      totalVulnerabilities: results.length,
                      vulnerabilities: results
                    };
                    const blob = new Blob([JSON.stringify(jsonReport, null, 2)], { type: 'application/json' });
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = `owasp-advanced-report-${Date.now()}.json`;
                    a.click();
                    URL.revokeObjectURL(url);
                  }}
                  className="bg-transparent border-tertiary text-tertiary hover:bg-tertiary hover:text-tertiary-foreground"
                >
                  <DownloadIcon className="w-4 h-4 mr-2" strokeWidth={1.5} />
                  Download JSON
                </Button>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
