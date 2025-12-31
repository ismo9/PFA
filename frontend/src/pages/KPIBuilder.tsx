import { useQuery } from '@tanstack/react-query';
import { MainLayout } from '@/components/layout/MainLayout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { api } from '@/lib/api';
import { Badge } from '@/components/ui/badge';
import { useIntl } from '@/components/contexts/IntlContext';

export default function KPIBuilder() {
  const { data: metrics, isLoading } = useQuery({
    queryKey: ['kpi-metrics'],
    queryFn: () => api.kpi.getMetrics(30),
  });
  const { data: catalog } = useQuery({
    queryKey: ['kpi-catalog'],
    queryFn: () => api.kpi.getCatalog(),
  });

  const { t } = useIntl();

  const rows: Array<{ label: string; value: any; category: string }> = [];
  if (metrics) {
    Object.entries(metrics).forEach(([category, values]) => {
      if (typeof values === 'object') {
        Object.entries(values as Record<string, any>).forEach(([key, val]) => {
          if (key === 'period') return;
          rows.push({ label: key, value: val, category });
        });
      }
    });
  }

  return (
    <MainLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-foreground">{t('kpi.title')}</h1>
          <p className="text-sm text-muted-foreground">{t('kpi.subtitle')}</p>
        </div>

        <Card className="border-border/60 bg-card/70">
          <CardHeader>
            <CardTitle className="text-lg">Available Metrics (30d)</CardTitle>
          </CardHeader>
          <CardContent className="overflow-auto">
            {isLoading ? (
              <p className="text-sm text-muted-foreground">Loading metrics...</p>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Metric</TableHead>
                    <TableHead>Category</TableHead>
                    <TableHead className="text-right">Value</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {rows.map((row) => (
                    <TableRow key={`${row.category}-${row.label}`} className="border-border/50">
                      <TableCell className="capitalize">{row.label.replace(/_/g, ' ')}</TableCell>
                      <TableCell className="capitalize text-muted-foreground">{row.category.replace(/_/g, ' ')}</TableCell>
                      <TableCell className="text-right font-mono">{String(row.value)}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
          </CardContent>
        </Card>

        <Card className="border-border/60 bg-card/70">
          <CardHeader>
            <CardTitle className="text-lg">Catalog</CardTitle>
          </CardHeader>
          <CardContent className="grid gap-3 md:grid-cols-2 lg:grid-cols-3">
            {(catalog?.categories ?? []).map((cat: any) => (
              <Card key={cat.name} className="border-border/60 bg-muted/30">
                <CardHeader>
                  <CardTitle className="text-base">{cat.name}</CardTitle>
                </CardHeader>
                <CardContent className="space-y-2">
                  {cat.metrics.map((m: any) => (
                    <div key={m.id} className="flex items-center justify-between text-sm">
                      <div>
                        <p className="font-medium">{m.label}</p>
                        <p className="text-xs text-muted-foreground">{m.format}</p>
                      </div>
                      <Badge variant="outline">{m.unit}</Badge>
                    </div>
                  ))}
                </CardContent>
              </Card>
            ))}
          </CardContent>
        </Card>
      </div>
    </MainLayout>
  );
}
