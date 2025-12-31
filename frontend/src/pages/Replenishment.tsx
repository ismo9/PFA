import { useQuery } from '@tanstack/react-query';
import { MainLayout } from '@/components/layout/MainLayout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { api } from '@/lib/api';
import { Badge } from '@/components/ui/badge';
import { AlertTriangle, CheckCircle, Clock } from 'lucide-react';
import { useIntl } from '@/components/contexts/IntlContext';

const statusIcon = {
  ORDER: AlertTriangle,
  ORDER_NOW: AlertTriangle,
  MONITOR: Clock,
  OK: CheckCircle,
};

export default function Replenishment() {
  const { data, isLoading } = useQuery({
    queryKey: ['replenishment'],
    queryFn: () => api.ai.getReplenishment(true),
  });

  const recommendations = data?.replenishment_recommendations ?? [];
  const { t } = useIntl();

  return (
    <MainLayout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-foreground">{t('replenishment.title')}</h1>
            <p className="text-sm text-muted-foreground">
              {t('replenishment.subtitle')}
            </p>
          </div>
        </div>

        <Card className="border-border/60 bg-card/70">
          <CardHeader>
            <CardTitle className="text-lg">Recommendations</CardTitle>
          </CardHeader>
          <CardContent className="overflow-auto">
            {isLoading ? (
              <p className="text-sm text-muted-foreground">Loading recommendations...</p>
            ) : recommendations.length === 0 ? (
              <p className="text-sm text-muted-foreground">No recommendations right now.</p>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Product</TableHead>
                    <TableHead className="text-right">On Hand</TableHead>
                    <TableHead className="text-right">Avg Daily Sales</TableHead>
                    <TableHead className="text-right">ROP</TableHead>
                    <TableHead className="text-right">Suggested Qty</TableHead>
                    <TableHead>Action</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {recommendations.map((r: any) => {
                    const Icon = statusIcon[(r.action || '').toUpperCase() as keyof typeof statusIcon] || Clock;
                    return (
                      <TableRow key={r.product_id} className="border-border/50">
                        <TableCell className="font-medium">{r.product_name}</TableCell>
                        <TableCell className="text-right font-mono">{r.current_stock ?? 0}</TableCell>
                        <TableCell className="text-right font-mono">{r.avg_daily_sales?.toFixed(2) ?? 0}</TableCell>
                        <TableCell className="text-right font-mono">{r.rop ?? 0}</TableCell>
                        <TableCell className="text-right font-mono">{r.suggested_order_qty ?? 0}</TableCell>
                        <TableCell>
                          <Badge
                            variant={r.action?.includes('ORDER') ? 'destructive' : r.action === 'MONITOR' ? 'secondary' : 'default'}
                            className="gap-1"
                          >
                            <Icon className="h-3 w-3" />
                            {r.action || 'monitor'}
                          </Badge>
                        </TableCell>
                      </TableRow>
                    );
                  })}
                </TableBody>
              </Table>
            )}
          </CardContent>
        </Card>
      </div>
    </MainLayout>
  );
}
