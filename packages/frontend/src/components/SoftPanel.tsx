import { useState } from 'react';
import { PlayIcon, ShieldIcon } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { useAppStore, VulnerabilityResult } from '@/stores/appStore';
import { useToast } from '@/hooks/use-toast';

export function SoftPanel() {
  const [url, setUrl] = useState('');
  const [attackType, setAttackType] = useState('all');
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
    setMode('soft');

    // Simulate test execution
    setTimeout(() => {
      const mockResults: VulnerabilityResult[] = [
        {
          id: Math.random().toString(),
          url,
          vulnerability: attackType === 'xss' || attackType === 'all' ? 'Cross-Site Scripting (XSS)' : 'SQL Injection',
          payload: attackType === 'xss' || attackType === 'all' ? '<script>alert("XSS")</script>' : "' OR '1'='1",
          severity: 'high',
          timestamp: new Date().toISOString(),
        },
      ];

      addResults(mockResults);
      setTestRunning(false);

      toast({
        title: 'Test Complete',
        description: `Found ${mockResults.length} potential vulnerabilities`,
      });
    }, 3000);
  };

  return (
    <div className="space-y-8">
      <div className="space-y-2">
        <h2 className="text-3xl font-heading font-semibold text-hero-text flex items-center gap-3">
          <ShieldIcon className="w-8 h-8 text-accent" strokeWidth={1.5} />
          Soft Mode
        </h2>
        <p className="text-lg text-gray-300">
          Simple and user-friendly vulnerability testing with essential attack vectors
        </p>
      </div>

      <Card className="bg-card border-border">
        <CardHeader>
          <CardTitle className="text-card-foreground">Test Configuration</CardTitle>
          <CardDescription className="text-gray-300">
            Configure your security test parameters
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="space-y-2">
            <Label htmlFor="target-url" className="text-primary-foreground">
              Target URL
            </Label>
            <Input
              id="target-url"
              type="url"
              placeholder="https://example.com"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              className="bg-primary border-border text-primary-foreground placeholder:text-gray-500"
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="attack-type" className="text-primary-foreground">
              Attack Type
            </Label>
            <Select value={attackType} onValueChange={setAttackType}>
              <SelectTrigger
                id="attack-type"
                className="bg-primary border-border text-primary-foreground"
              >
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All (XSS + SQLi)</SelectItem>
                <SelectItem value="xss">XSS Only</SelectItem>
                <SelectItem value="sqli">SQL Injection Only</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <Button
            onClick={handleRunTest}
            disabled={isTestRunning}
            className="w-full bg-accent text-accent-foreground hover:bg-accent/90 font-medium"
          >
            <PlayIcon className="w-5 h-5 mr-2" strokeWidth={1.5} />
            {isTestRunning ? 'Running Test...' : 'Run Test'}
          </Button>
        </CardContent>
      </Card>

      {results.length > 0 && (
        <Card className="bg-card border-border">
          <CardHeader>
            <CardTitle className="text-card-foreground">Recent Results</CardTitle>
            <CardDescription className="text-gray-300">
              Latest vulnerability findings
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {results.slice(0, 3).map((result) => (
                <div
                  key={result.id}
                  className="p-4 bg-primary rounded-lg border border-border"
                >
                  <p className="font-medium text-primary-foreground">{result.vulnerability}</p>
                  <p className="text-sm text-gray-400 mt-1">{result.url}</p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
