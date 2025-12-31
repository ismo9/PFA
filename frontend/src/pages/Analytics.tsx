import { useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { MainLayout } from '@/components/layout/MainLayout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { AlertTriangle, TrendingUp, TrendingDown, Grid3X3 } from 'lucide-react';
import { api } from '@/lib/api';
import { useIntl } from '@/components/contexts/IntlContext';

export default function Analytics() {
  const { data: anomalies, isLoading: loadingAnomalies } = useQuery({
    queryKey: ['anomalies'],
    queryFn: () => api.ai.getAnomalies(30, 3),
  });
  const { data: segmentation, isLoading: loadingSegmentation } = useQuery({
    queryKey: ['segmentation'],
    queryFn: () => api.ai.getSegmentation(60),
  });

  const segmentationCounts = useMemo(() => {
    const items = segmentation?.items ?? [];
    const abc: Record<string, number> = { A: 0, B: 0, C: 0 };
    const xyz: Record<string, number> = { X: 0, Y: 0, Z: 0 };
    items.forEach((i: any) => {
      abc[i.abc] = (abc[i.abc] || 0) + 1;
      xyz[i.xyz] = (xyz[i.xyz] || 0) + 1;
    });
    return { abc, xyz };
  }, [segmentation]);

  const { t } = useIntl();

  return (
    <MainLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-foreground">{t('analytics.title')}</h1>
          <p className="text-muted-foreground text-sm">{t('analytics.subtitle')}</p>
        </div>

        <Tabs defaultValue="anomalies">
          <TabsList className="bg-muted/50">
            <TabsTrigger value="anomalies" className="gap-2">
              <AlertTriangle className="h-4 w-4" />
              Anomalies
            </TabsTrigger>
            <TabsTrigger value="segmentation" className="gap-2">
              <Grid3X3 className="h-4 w-4" />
              ABC/XYZ
            </TabsTrigger>
          </TabsList>

          <TabsContent value="anomalies" className="mt-6 space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <Card className="border-border/60 bg-card/70">
                <CardContent className="p-4">
                  <p className="text-xs text-muted-foreground uppercase">Total anomalies (30d)</p>
                  <p className="text-2xl font-semibold text-foreground mt-1">
                    {loadingAnomalies ? '...' : anomalies?.total ?? 0}
                  </p>
                </CardContent>
              </Card>
              <Card className="border-border/60 bg-card/70">
                <CardContent className="p-4">
                  <p className="text-xs text-muted-foreground uppercase">Spikes</p>
                  <p className="text-2xl font-semibold text-green-500 mt-1">
                    {loadingAnomalies
                      ? '...'
                      : (anomalies?.items ?? []).filter((a: any) => a.direction === 'SPIKE').length}
                  </p>
                </CardContent>
              </Card>
              <Card className="border-border/60 bg-card/70">
                <CardContent className="p-4">
                  <p className="text-xs text-muted-foreground uppercase">Drops</p>
                  <p className="text-2xl font-semibold text-amber-500 mt-1">
                    {loadingAnomalies
                      ? '...'
                      : (anomalies?.items ?? []).filter((a: any) => a.direction === 'DROP').length}
                  </p>
                </CardContent>
              </Card>
              <Card className="border-border/60 bg-card/70">
                <CardContent className="p-4">
                  <p className="text-xs text-muted-foreground uppercase">Severity HIGH</p>
                  <p className="text-2xl font-semibold text-rose-500 mt-1">
                    {loadingAnomalies
                      ? '...'
                      : (anomalies?.items ?? []).filter((a: any) => a.severity === 'HIGH').length}
                  </p>
                </CardContent>
              </Card>
            </div>

            <Card className="border-border/60 bg-card/70">
              <CardHeader>
                <CardTitle className="text-lg">Detected Anomalies</CardTitle>
              </CardHeader>
              <CardContent className="overflow-auto">
                {loadingAnomalies ? (
                  <p className="text-sm text-muted-foreground">Loading anomalies...</p>
                ) : (
                  <Table>
                    <TableHeader>
                      <TableRow className="border-border/50">
                        <TableHead>Product</TableHead>
                        <TableHead>Date</TableHead>
                        <TableHead>Direction</TableHead>
                        <TableHead className="text-right">Qty</TableHead>
                        <TableHead className="text-right">z-score</TableHead>
                        <TableHead>Severity</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {(anomalies?.items ?? []).map((a: any, idx: number) => (
                        <TableRow key={`${a.product_id}-${idx}`} className="border-border/50">
                          <TableCell>
                            <div className="font-medium">Product {a.product_id}</div>
                            <div className="text-xs text-muted-foreground">#{a.product_id}</div>
                          </TableCell>
                          <TableCell className="text-sm text-muted-foreground">{a.date}</TableCell>
                          <TableCell className="capitalize flex items-center gap-2">
                            {a.direction === 'SPIKE' ? (
                              <TrendingUp className="h-4 w-4 text-green-500" />
                            ) : (
                              <TrendingDown className="h-4 w-4 text-amber-500" />
                            )}
                            {a.direction?.toLowerCase()}
                          </TableCell>
                          <TableCell className="text-right font-mono">{a.quantity}</TableCell>
                          <TableCell className="text-right font-mono">{a.z_score}</TableCell>
                          <TableCell>
                            <Badge variant={a.severity === 'HIGH' ? 'destructive' : 'secondary'} className="capitalize">
                              {a.severity?.toLowerCase()}
                            </Badge>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="segmentation" className="mt-6 space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <Card className="border-border/60 bg-card/70">
                <CardContent className="p-4">
                  <p className="text-xs text-muted-foreground uppercase">Total Items</p>
                  <p className="text-2xl font-semibold text-foreground mt-1">{segmentation?.total ?? 0}</p>
                  <p className="text-xs text-muted-foreground mt-1">Lookback {segmentation?.days_lookback ?? 60} days</p>
                </CardContent>
              </Card>
              <Card className="border-border/60 bg-card/70">
                <CardContent className="p-4">
                  <p className="text-xs text-muted-foreground uppercase">ABC</p>
                  <div className="flex items-center gap-3 mt-2">
                    {['A', 'B', 'C'].map((k) => (
                      <Badge key={k} variant="outline" className="gap-1">
                        {k}
                        <span className="font-mono">{segmentationCounts.abc[k] ?? 0}</span>
                      </Badge>
                    ))}
                  </div>
                </CardContent>
              </Card>
              <Card className="border-border/60 bg-card/70">
                <CardContent className="p-4">
                  <p className="text-xs text-muted-foreground uppercase">XYZ</p>
                  <div className="flex items-center gap-3 mt-2">
                    {['X', 'Y', 'Z'].map((k) => (
                      <Badge key={k} variant="outline" className="gap-1">
                        {k}
                        <span className="font-mono">{segmentationCounts.xyz[k] ?? 0}</span>
                      </Badge>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>

            <Card className="border-border/60 bg-card/70">
              <CardHeader>
                <CardTitle className="text-lg">Segmented Products</CardTitle>
              </CardHeader>
              <CardContent className="overflow-auto">
                {loadingSegmentation ? (
                  <p className="text-sm text-muted-foreground">Loading segmentation...</p>
                ) : (
                  <Table>
                    <TableHeader>
                      <TableRow className="border-border/50">
                        <TableHead>Product</TableHead>
                        <TableHead>ABC</TableHead>
                        <TableHead>XYZ</TableHead>
                        <TableHead className="text-right">Revenue</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {(segmentation?.items ?? []).slice(0, 50).map((i: any) => (
                        <TableRow key={i.product_id} className="border-border/50">
                          <TableCell>
                            <div className="font-medium">{i.product_name}</div>
                            <div className="text-xs text-muted-foreground">ID {i.product_id}</div>
                          </TableCell>
                          <TableCell>
                            <Badge variant={i.abc === 'A' ? 'default' : i.abc === 'B' ? 'secondary' : 'outline'}>
                              {i.abc}
                            </Badge>
                          </TableCell>
                          <TableCell>
                            <Badge variant={i.xyz === 'X' ? 'default' : i.xyz === 'Y' ? 'secondary' : 'outline'}>
                              {i.xyz}
                            </Badge>
                          </TableCell>
                          <TableCell className="text-right font-mono">{i.revenue?.toFixed(2) ?? 0} MAD</TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </MainLayout>
  );
}
