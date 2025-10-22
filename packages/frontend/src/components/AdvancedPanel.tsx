import { useState } from 'react';
import { PlayIcon, ShieldAlertIcon, SettingsIcon } from 'lucide-react';
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
  const { addResults, setTestRunning, isTestRunning, setMode } = useAppStore();
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

      <Card className="bg-card border-border">
        <CardHeader>
          <CardTitle className="text-card-foreground flex items-center gap-2">
            <SettingsIcon className="w-5 h-5" strokeWidth={1.5} />
            Advanced Configuration
          </CardTitle>
          <CardDescription className="text-gray-300">
            Fine-tune your security assessment parameters
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="space-y-2">
            <Label htmlFor="adv-target-url" className="text-primary-foreground">
              Target URL
            </Label>
            <Input
              id="adv-target-url"
              type="url"
              placeholder="https://example.com"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              className="bg-primary border-border text-primary-foreground placeholder:text-gray-500"
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="adv-attack-type" className="text-primary-foreground">
              Attack Vector
            </Label>
            <Select value={attackType} onValueChange={setAttackType}>
              <SelectTrigger
                id="adv-attack-type"
                className="bg-primary border-border text-primary-foreground"
              >
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
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
            <Label htmlFor="custom-payloads" className="text-primary-foreground">
              Custom Payloads (one per line)
            </Label>
            <Textarea
              id="custom-payloads"
              placeholder="<script>alert(document.cookie)</script>&#10;' OR '1'='1&#10;{{7*7}}"
              value={customPayloads}
              onChange={(e) => setCustomPayloads(e.target.value)}
              className="bg-primary border-border text-primary-foreground placeholder:text-gray-500 font-mono text-sm min-h-32"
            />
          </div>

          <Separator className="bg-border" />

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-2">
              <Label htmlFor="crawl-depth" className="text-primary-foreground">
                Crawl Depth
              </Label>
              <Select value={crawlDepth} onValueChange={setCrawlDepth}>
                <SelectTrigger
                  id="crawl-depth"
                  className="bg-primary border-border text-primary-foreground"
                >
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="1">1 Level</SelectItem>
                  <SelectItem value="2">2 Levels</SelectItem>
                  <SelectItem value="3">3 Levels</SelectItem>
                  <SelectItem value="5">5 Levels</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="timeout" className="text-primary-foreground">
                Timeout (seconds)
              </Label>
              <Input
                id="timeout"
                type="number"
                value={timeout}
                onChange={(e) => setTimeout(e.target.value)}
                className="bg-primary border-border text-primary-foreground"
              />
            </div>
          </div>

          <div className="flex items-center justify-between p-4 bg-primary rounded-lg border border-border">
            <div className="space-y-1">
              <Label htmlFor="follow-redirects" className="text-primary-foreground font-medium">
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

          <Button
            onClick={handleRunTest}
            disabled={isTestRunning}
            className="w-full bg-tertiary text-tertiary-foreground hover:bg-tertiary/90 font-medium"
          >
            <PlayIcon className="w-5 h-5 mr-2" strokeWidth={1.5} />
            {isTestRunning ? 'Running Advanced Test...' : 'Run Advanced Test'}
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}
