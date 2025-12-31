import { useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { MainLayout } from '@/components/layout/MainLayout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { api } from '@/lib/api';
import { useIntl } from '@/components/contexts/IntlContext';
import { TrendingUp, TrendingDown, Package, AlertTriangle, LineChart } from 'lucide-react';

const StatCard = ({ title, value, description }: { title: string; value: string | number; description?: string }) => (
  <Card className="border-border/60 bg-card/70">
    <CardHeader className="pb-3">
      <CardTitle className="text-sm text-muted-foreground">{title}</CardTitle>
    </CardHeader>
    <CardContent>
      <p className="text-2xl font-semibold text-foreground">{value}</p>
      {description && <p className="text-xs text-muted-foreground mt-1">{description}</p>}
    </CardContent>
  </Card>
);

export default function Dashboard() {
  const { t } = useIntl();
  const { data: overview, isLoading: loadingOverview } = useQuery({
    queryKey: ['dashboard-overview'],
    queryFn: api.dashboard.getOverview,
  });
  const { data: salesTrends, isLoading: loadingTrends } = useQuery({
    queryKey: ['dashboard-trends'],
    queryFn: () => api.dashboard.getSalesTrends('daily', 14),
  });
  const { data: topProducts, isLoading: loadingTop } = useQuery({
    queryKey: ['dashboard-top'],
    queryFn: () => api.dashboard.getTopProducts('revenue', 30, 5),
  });
  const { data: stockStatus, isLoading: loadingStock } = useQuery({
    queryKey: ['dashboard-stock'],
    queryFn: api.dashboard.getStockStatus,
  });
  const { data: abcxyz, isLoading: loadingSeg } = useQuery({
    queryKey: ['dashboard-abcxyz'],
    queryFn: () => api.dashboard.getABCXYZSummary(),
  });

  const lastTrend = useMemo(() => salesTrends?.trends?.slice(-1)[0], [salesTrends]);

  return (
    <MainLayout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-foreground">{t('dashboard.title')}</h1>
            <p className="text-sm text-muted-foreground">{t('dashboard.subtitle')}</p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard
            title="Total Products"
            value={loadingOverview ? '...' : overview?.total_products ?? '—'}
            description="Fetched from Odoo catalog"
          />
          <StatCard
            title="Stock Value"
            value={loadingOverview ? '...' : `${overview?.total_stock_value?.toLocaleString() ?? '—'} MAD`}
            description="Qty available × standard price (MAD)"
          />
          <StatCard
            title="Low Stock"
            value={loadingOverview ? '...' : overview?.low_stock_alerts ?? '—'}
            description="Below 10 units"
          />
          <StatCard
            title="Recent Revenue (7d)"
            value={
              loadingOverview
                ? '...'
                : `${overview?.recent_sales_7d?.revenue?.toLocaleString(undefined, { maximumFractionDigits: 0 }) ?? '—'} MAD`
            }
            description={`Qty: ${overview?.recent_sales_7d?.quantity_sold ?? '—'}`}
          />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          <Card className="col-span-2 border-border/60 bg-card/70">
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle className="text-lg flex items-center gap-2">
                <LineChart className="h-4 w-4" /> Sales Trends (14d)
              </CardTitle>
              {lastTrend && (
                <div className="text-xs text-muted-foreground">
                  Last period: {lastTrend.period} — ${lastTrend.revenue?.toFixed(0)}
                </div>
              )}
            </CardHeader>
            <CardContent>
              {loadingTrends ? (
                <p className="text-muted-foreground text-sm">Loading trends...</p>
              ) : (
                <div className="space-y-3">
                  {(salesTrends?.trends ?? []).slice(-7).map((t: any) => (
                    <div key={t.period} className="flex items-center justify-between text-sm">
                      <span className="text-muted-foreground">{t.period}</span>
                      <div className="flex items-center gap-3">
                        <span className="font-mono text-foreground">{t.revenue?.toFixed(0)} MAD</span>
                        <span className="font-mono text-xs text-muted-foreground">{t.quantity_sold?.toFixed(1)} qty</span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>

          <Card className="border-border/60 bg-card/70">
            <CardHeader>
              <CardTitle className="text-lg flex items-center gap-2">
                <TrendingUp className="h-4 w-4 text-primary" /> Top Products (30d)
              </CardTitle>
            </CardHeader>
            <CardContent>
              {loadingTop ? (
                <p className="text-muted-foreground text-sm">Loading top products...</p>
              ) : (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Product</TableHead>
                      <TableHead className="text-right">Qty</TableHead>
                      <TableHead className="text-right">Revenue</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {(topProducts?.products ?? []).map((p: any) => (
                      <TableRow key={p.product_id} className="border-border/50">
                        <TableCell className="font-medium">{p.product_name}</TableCell>
                        <TableCell className="text-right font-mono">{p.quantity_sold?.toFixed(1)}</TableCell>
                        <TableCell className="text-right font-mono">{p.revenue?.toFixed(0)} MAD</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              )}
            </CardContent>
          </Card>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          <Card className="border-border/60 bg-card/70">
            <CardHeader>
              <CardTitle className="text-lg flex items-center gap-2">
                <Package className="h-4 w-4" /> Stock Status
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              {loadingStock ? (
                <p className="text-muted-foreground text-sm">Loading stock...</p>
              ) : (
                ['out_of_stock', 'low_stock', 'adequate', 'overstock'].map((key) => {
                  const entry = stockStatus?.[key];
                  return (
                    <div key={key} className="flex items-center justify-between text-sm">
                      <span className="capitalize text-muted-foreground">{key.replace('_', ' ')}</span>
                      <span className="font-semibold text-foreground">{entry?.count ?? 0}</span>
                    </div>
                  );
                })
              )}
            </CardContent>
          </Card>

          <Card className="border-border/60 bg-card/70">
            <CardHeader>
              <CardTitle className="text-lg flex items-center gap-2">
                <AlertTriangle className="h-4 w-4 text-amber-500" /> ABC / XYZ Snapshot
              </CardTitle>
            </CardHeader>
            <CardContent className="grid grid-cols-2 gap-3 text-sm">
              {loadingSeg ? (
                <p className="text-muted-foreground">Loading segmentation...</p>
              ) : (
                <>
                  <div>
                    <p className="text-xs text-muted-foreground mb-1">ABC (value)</p>
                    <div className="space-y-1">
                      {['A', 'B', 'C'].map((k) => (
                        <div key={k} className="flex items-center justify-between">
                          <span>{k}</span>
                          <span className="font-mono">{abcxyz?.abc?.[k] ?? 0}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                  <div>
                    <p className="text-xs text-muted-foreground mb-1">XYZ (variability)</p>
                    <div className="space-y-1">
                      {['X', 'Y', 'Z'].map((k) => (
                        <div key={k} className="flex items-center justify-between">
                          <span>{k}</span>
                          <span className="font-mono">{abcxyz?.xyz?.[k] ?? 0}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </>
              )}
            </CardContent>
          </Card>

          <Card className="border-border/60 bg-card/70">
            <CardHeader>
              <CardTitle className="text-lg flex items-center gap-2">
                <TrendingDown className="h-4 w-4 text-rose-500" /> Out of Stock Samples
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-2 text-sm">
              {loadingStock ? (
                <p className="text-muted-foreground">Loading...</p>
              ) : (
                (stockStatus?.out_of_stock?.samples ?? []).slice(0, 5).map((s: any) => (
                  <div key={s.product_id} className="flex items-center justify-between">
                    <span className="truncate">{s.product_name}</span>
                    <span className="font-mono text-muted-foreground">{s.quantity}</span>
                  </div>
                ))
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </MainLayout>
  );
}
