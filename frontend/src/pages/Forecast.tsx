import { useEffect, useMemo, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { MainLayout } from '@/components/layout/MainLayout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { api } from '@/lib/api';
import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { Badge } from '@/components/ui/badge';

export default function Forecast() {
  const [selectedProduct, setSelectedProduct] = useState<number | null>(null);
  const [horizon, setHorizon] = useState(30);

  const { data: products } = useQuery({
    queryKey: ['forecast-products'],
    queryFn: () => api.inventory.getProducts(100),
  });

  const { data: forecast, isFetching } = useQuery({
    queryKey: ['forecast', selectedProduct, horizon],
    queryFn: () => api.ai.getForecast(selectedProduct!, horizon, 180),
    enabled: !!selectedProduct,
  });

  useEffect(() => {
    if (!selectedProduct && products?.length) {
      setSelectedProduct(products[0].id);
    }
  }, [products, selectedProduct]);

  const chartData = useMemo(() => {
    if (!forecast?.daily_forecast) return [];
    return forecast.daily_forecast.map((value: number, idx: number) => ({
      day: `D${idx + 1}`,
      value,
    }));
  }, [forecast]);

  return (
    <MainLayout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-foreground">Forecast</h1>
            <p className="text-sm text-muted-foreground">30-day ML forecast per product</p>
          </div>
        </div>

        <Card className="border-border/60 bg-card/70">
          <CardHeader>
            <CardTitle className="text-lg">Configuration</CardTitle>
          </CardHeader>
          <CardContent className="grid gap-4 md:grid-cols-3">
            <div className="space-y-2">
              <Label>Product</Label>
              <Select
                value={selectedProduct?.toString()}
                onValueChange={(v) => setSelectedProduct(Number(v))}
              >
                <SelectTrigger className="bg-muted/50">
                  <SelectValue placeholder="Select product" />
                </SelectTrigger>
                <SelectContent>
                  {(products ?? []).map((p: any) => (
                    <SelectItem key={p.id} value={p.id.toString()}>
                      {p.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label>Horizon (days)</Label>
              <Input
                type="number"
                min={7}
                max={60}
                value={horizon}
                onChange={(e) => setHorizon(Number(e.target.value))}
                className="bg-muted/50"
              />
            </div>

            <div className="space-y-2">
              <Label>Model</Label>
              <Badge variant="outline" className="h-10 inline-flex items-center justify-center">
                ML first, baseline fallback
              </Badge>
            </div>
          </CardContent>
        </Card>

        <Card className="border-border/60 bg-card/70">
          <CardHeader>
            <CardTitle className="text-lg">Forecast Output</CardTitle>
          </CardHeader>
          <CardContent>
            {!selectedProduct ? (
              <p className="text-sm text-muted-foreground">Select a product to forecast.</p>
            ) : isFetching ? (
              <p className="text-sm text-muted-foreground">Computing forecast...</p>
            ) : forecast ? (
              <div className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                  <div>
                    <p className="text-muted-foreground">Total forecast</p>
                    <p className="text-xl font-semibold">{forecast.total_forecast?.toFixed(2) ?? 0}</p>
                  </div>
                  <div>
                    <p className="text-muted-foreground">Model used</p>
                    <p className="text-xl font-semibold capitalize">{forecast.model_used || 'baseline'}</p>
                  </div>
                  <div>
                    <p className="text-muted-foreground">Status</p>
                    <p className="text-xl font-semibold">{forecast.status || 'ok'}</p>
                  </div>
                </div>

                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={chartData}>
                      <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" opacity={0.3} />
                      <XAxis dataKey="day" stroke="hsl(var(--muted-foreground))" />
                      <YAxis stroke="hsl(var(--muted-foreground))" />
                      <Tooltip
                        contentStyle={{
                          backgroundColor: 'hsl(var(--card))',
                          border: '1px solid hsl(var(--border))',
                          borderRadius: 8,
                        }}
                      />
                      <Area
                        type="monotone"
                        dataKey="value"
                        stroke="hsl(var(--primary))"
                        fill="hsl(var(--primary))"
                        fillOpacity={0.25}
                      />
                    </AreaChart>
                  </ResponsiveContainer>
                </div>
              </div>
            ) : (
              <p className="text-sm text-muted-foreground">No forecast available.</p>
            )}
          </CardContent>
        </Card>
      </div>
    </MainLayout>
  );
}
