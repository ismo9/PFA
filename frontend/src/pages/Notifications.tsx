import { useEffect, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { MainLayout } from '@/components/layout/MainLayout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Bell, AlertTriangle, TrendingDown, Package, CheckCircle, Trash2, MailOpen } from 'lucide-react';
import { cn } from '@/lib/utils';
import { api } from '@/lib/api';

interface Notification {
  id: string;
  type: 'alert' | 'warning' | 'info' | 'success';
  title: string;
  message: string;
  timestamp: string;
  read: boolean;
  category: 'stock' | 'demand' | 'system' | 'forecast';
}

const typeConfig = {
  alert: { icon: AlertTriangle, color: 'text-red-500', bg: 'bg-red-500/10' },
  warning: { icon: TrendingDown, color: 'text-yellow-500', bg: 'bg-yellow-500/10' },
  info: { icon: Bell, color: 'text-blue-500', bg: 'bg-blue-500/10' },
  success: { icon: CheckCircle, color: 'text-green-500', bg: 'bg-green-500/10' },
};

export default function Notifications() {
  const { data: alerts } = useQuery({
    queryKey: ['alerts'],
    queryFn: api.notifications.getAlerts,
  });
  const { data: anomalies } = useQuery({
    queryKey: ['alerts-anomalies'],
    queryFn: () => api.ai.getAnomalies(14, 3),
  });

  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [filter, setFilter] = useState<string>('all');

  useEffect(() => {
    const fromAlerts =
      alerts?.alerts?.map((a: any, idx: number) => ({
        id: `alert-${idx}`,
        type: a.type === 'OUT_OF_STOCK' ? 'alert' : 'warning',
        title: a.type === 'OUT_OF_STOCK' ? 'Out of stock' : 'Low stock',
        message: `${a.product_name} ${a.message}`,
        timestamp: new Date().toLocaleString(),
        read: false,
        category: 'stock' as const,
      })) ?? [];
    const fromAnomalies =
      anomalies?.items?.map((a: any, idx: number) => ({
        id: `anomaly-${idx}`,
        type: 'warning' as const,
        title: `${a.direction?.toLowerCase()} detected`,
        message: `Product ${a.product_id} z=${a.z_score}`,
        timestamp: a.date,
        read: false,
        category: 'demand' as const,
      })) ?? [];
    setNotifications([...fromAlerts, ...fromAnomalies]);
  }, [alerts, anomalies]);

  const unreadCount = notifications.filter(n => !n.read).length;

  const filteredNotifications = notifications.filter(n => {
    if (filter === 'all') return true;
    if (filter === 'unread') return !n.read;
    return n.category === filter;
  });

  const markAsRead = (id: string) => {
    setNotifications(prev => prev.map(n => n.id === id ? { ...n, read: true } : n));
  };

  const markAllRead = () => {
    setNotifications(prev => prev.map(n => ({ ...n, read: true })));
  };

  const deleteNotification = (id: string) => {
    setNotifications(prev => prev.filter(n => n.id !== id));
  };

  return (
    <MainLayout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-foreground">Notifications</h1>
            <p className="text-muted-foreground text-sm">
              {unreadCount} unread notifications
            </p>
          </div>
          <Button variant="outline" size="sm" onClick={markAllRead} disabled={unreadCount === 0}>
            <MailOpen className="h-4 w-4 mr-2" />
            Mark all read
          </Button>
        </div>

        <Tabs value={filter} onValueChange={setFilter}>
          <TabsList className="bg-muted/50">
            <TabsTrigger value="all">All</TabsTrigger>
            <TabsTrigger value="unread">
              Unread
              {unreadCount > 0 && (
                <Badge variant="destructive" className="ml-2 h-5 w-5 p-0 text-xs">
                  {unreadCount}
                </Badge>
              )}
            </TabsTrigger>
            <TabsTrigger value="stock">Stock</TabsTrigger>
            <TabsTrigger value="demand">Demand</TabsTrigger>
            <TabsTrigger value="forecast">Forecast</TabsTrigger>
            <TabsTrigger value="system">System</TabsTrigger>
          </TabsList>

          <TabsContent value={filter} className="mt-4">
            <Card className="border-border/50 bg-card/50">
              <CardContent className="p-0">
                {filteredNotifications.length === 0 ? (
                  <div className="p-8 text-center text-muted-foreground">
                    <Bell className="h-12 w-12 mx-auto mb-4 opacity-50" />
                    <p>No notifications</p>
                  </div>
                ) : (
                  <div className="divide-y divide-border/50">
                    {filteredNotifications.map((notification) => {
                      const config = typeConfig[notification.type];
                      const Icon = config.icon;
                      
                      return (
                        <div
                          key={notification.id}
                          className={cn(
                            "p-4 flex items-start gap-4 hover:bg-muted/30 transition-colors cursor-pointer",
                            !notification.read && "bg-primary/5"
                          )}
                          onClick={() => markAsRead(notification.id)}
                        >
                          <div className={cn("p-2 rounded-lg", config.bg)}>
                            <Icon className={cn("h-4 w-4", config.color)} />
                          </div>
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-2">
                              <h4 className="font-medium text-foreground">{notification.title}</h4>
                              {!notification.read && (
                                <div className="h-2 w-2 rounded-full bg-primary animate-pulse" />
                              )}
                            </div>
                            <p className="text-sm text-muted-foreground mt-1">{notification.message}</p>
                            <p className="text-xs text-muted-foreground/70 mt-2">{notification.timestamp}</p>
                          </div>
                          <Button
                            variant="ghost"
                            size="icon"
                            className="h-8 w-8 text-muted-foreground hover:text-destructive"
                            onClick={(e) => {
                              e.stopPropagation();
                              deleteNotification(notification.id);
                            }}
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      );
                    })}
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </MainLayout>
  );
}
