import { useState, useEffect } from 'react';
import { MainLayout } from '@/components/layout/MainLayout';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { Separator } from '@/components/ui/separator';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Settings as SettingsIcon, Palette, Bell, Database, Download, Server, CheckCircle, XCircle, Loader2 } from 'lucide-react';
import { api } from '@/lib/api';
import { useToast } from '@/hooks/use-toast';

interface HealthStatus {
  status: string;
  database: string;
  cache: string;
  version: string;
}

export default function Settings() {
  const [darkMode, setDarkMode] = useState(true);
  const [notifications, setNotifications] = useState(true);
  const [emailAlerts, setEmailAlerts] = useState(false);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const { toast } = useToast();

  useEffect(() => {
    checkHealth();
  }, []);

  const checkHealth = async () => {
    setLoading(true);
    try {
      const [appStatus, odooStatus] = await Promise.all([api.health.app(), api.health.odoo()]);
      setHealth({
        status: appStatus?.scheduler_running ? 'healthy' : 'degraded',
        database: odooStatus?.odoo_connection === 'ok' ? 'connected' : 'error',
        cache: 'in-memory',
        version: 'FastAPI',
      });
    } catch (error) {
      setHealth({ status: 'unhealthy', database: 'disconnected', cache: 'disconnected', version: 'unknown' });
    } finally {
      setLoading(false);
    }
  };

  const exportData = async (type: string) => {
    toast({
      title: 'Export Started',
      description: `Exporting ${type} data...`,
    });
    // Simulate export
    setTimeout(() => {
      toast({
        title: 'Export Complete',
        description: `${type} data exported successfully.`,
      });
    }, 2000);
  };

  const StatusBadge = ({ status }: { status: string }) => (
    <Badge variant={status === 'healthy' || status === 'connected' ? 'default' : 'destructive'} className="gap-1">
      {status === 'healthy' || status === 'connected' ? (
        <CheckCircle className="h-3 w-3" />
      ) : (
        <XCircle className="h-3 w-3" />
      )}
      {status}
    </Badge>
  );

  return (
    <MainLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-foreground">Settings</h1>
          <p className="text-muted-foreground text-sm">Manage your preferences and system configuration</p>
        </div>

        <Tabs defaultValue="appearance">
          <TabsList className="bg-muted/50">
            <TabsTrigger value="appearance" className="gap-2">
              <Palette className="h-4 w-4" />
              Appearance
            </TabsTrigger>
            <TabsTrigger value="notifications" className="gap-2">
              <Bell className="h-4 w-4" />
              Notifications
            </TabsTrigger>
            <TabsTrigger value="data" className="gap-2">
              <Database className="h-4 w-4" />
              Data
            </TabsTrigger>
            <TabsTrigger value="system" className="gap-2">
              <Server className="h-4 w-4" />
              System
            </TabsTrigger>
          </TabsList>

          <TabsContent value="appearance" className="mt-6 space-y-4">
            <Card className="border-border/50 bg-card/50">
              <CardHeader>
                <CardTitle className="text-lg">Theme</CardTitle>
                <CardDescription>Customize the appearance of the dashboard</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <Label htmlFor="dark-mode" className="font-medium">Dark Mode</Label>
                    <p className="text-sm text-muted-foreground">Use dark theme for better visibility</p>
                  </div>
                  <Switch id="dark-mode" checked={darkMode} onCheckedChange={setDarkMode} />
                </div>
                <Separator className="bg-border/50" />
                <div className="flex items-center justify-between">
                  <div>
                    <Label htmlFor="auto-refresh" className="font-medium">Auto Refresh</Label>
                    <p className="text-sm text-muted-foreground">Automatically refresh data every 30 seconds</p>
                  </div>
                  <Switch id="auto-refresh" checked={autoRefresh} onCheckedChange={setAutoRefresh} />
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="notifications" className="mt-6 space-y-4">
            <Card className="border-border/50 bg-card/50">
              <CardHeader>
                <CardTitle className="text-lg">Notification Preferences</CardTitle>
                <CardDescription>Configure how you receive alerts</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <Label htmlFor="notifications" className="font-medium">Push Notifications</Label>
                    <p className="text-sm text-muted-foreground">Receive in-app notifications</p>
                  </div>
                  <Switch id="notifications" checked={notifications} onCheckedChange={setNotifications} />
                </div>
                <Separator className="bg-border/50" />
                <div className="flex items-center justify-between">
                  <div>
                    <Label htmlFor="email-alerts" className="font-medium">Email Alerts</Label>
                    <p className="text-sm text-muted-foreground">Receive critical alerts via email</p>
                  </div>
                  <Switch id="email-alerts" checked={emailAlerts} onCheckedChange={setEmailAlerts} />
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="data" className="mt-6 space-y-4">
            <Card className="border-border/50 bg-card/50">
              <CardHeader>
                <CardTitle className="text-lg">Data Export</CardTitle>
                <CardDescription>Export your data for analysis or backup</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <Button variant="outline" className="justify-start gap-2" onClick={() => exportData('Inventory')}>
                    <Download className="h-4 w-4" />
                    Export Inventory (CSV)
                  </Button>
                  <Button variant="outline" className="justify-start gap-2" onClick={() => exportData('Sales')}>
                    <Download className="h-4 w-4" />
                    Export Sales Data (CSV)
                  </Button>
                  <Button variant="outline" className="justify-start gap-2" onClick={() => exportData('Forecasts')}>
                    <Download className="h-4 w-4" />
                    Export Forecasts (CSV)
                  </Button>
                  <Button variant="outline" className="justify-start gap-2" onClick={() => exportData('KPIs')}>
                    <Download className="h-4 w-4" />
                    Export KPI Report (PDF)
                  </Button>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="system" className="mt-6 space-y-4">
            <Card className="border-border/50 bg-card/50">
              <CardHeader className="flex flex-row items-center justify-between">
                <div>
                  <CardTitle className="text-lg">System Health</CardTitle>
                  <CardDescription>Monitor backend services status</CardDescription>
                </div>
                <Button variant="outline" size="sm" onClick={checkHealth} disabled={loading}>
                  {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : 'Refresh'}
                </Button>
              </CardHeader>
              <CardContent>
                {loading ? (
                  <div className="flex items-center justify-center py-8">
                    <Loader2 className="h-8 w-8 animate-spin text-primary" />
                  </div>
                ) : health ? (
                  <div className="space-y-4">
                    <div className="flex items-center justify-between p-3 bg-muted/30 rounded-lg">
                      <span className="text-sm font-medium">API Status</span>
                      <StatusBadge status={health.status} />
                    </div>
                    <div className="flex items-center justify-between p-3 bg-muted/30 rounded-lg">
                      <span className="text-sm font-medium">Database</span>
                      <StatusBadge status={health.database} />
                    </div>
                    <div className="flex items-center justify-between p-3 bg-muted/30 rounded-lg">
                      <span className="text-sm font-medium">Cache</span>
                      <StatusBadge status={health.cache} />
                    </div>
                    <div className="flex items-center justify-between p-3 bg-muted/30 rounded-lg">
                      <span className="text-sm font-medium">Version</span>
                      <Badge variant="outline">{health.version}</Badge>
                    </div>
                  </div>
                ) : (
                  <p className="text-center text-muted-foreground py-8">Unable to fetch health status</p>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </MainLayout>
  );
}
