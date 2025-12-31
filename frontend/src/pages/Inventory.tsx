import { useQuery } from '@tanstack/react-query';
import { MainLayout } from '@/components/layout/MainLayout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { api } from '@/lib/api';
import { Badge } from '@/components/ui/badge';
import { Download } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useIntl } from '@/components/contexts/IntlContext';

export default function Inventory() {
  const { data: products, isLoading: loadingProducts } = useQuery({
    queryKey: ['inventory-products'],
    queryFn: () => api.inventory.getProducts(200),
  });
  const { data: moves, isLoading: loadingMoves } = useQuery({
    queryKey: ['inventory-moves'],
    queryFn: () => api.inventory.getStockMoves(20),
  });

  const { t } = useIntl();

  return (
    <MainLayout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-foreground">{t('inventory.title')}</h1>
            <p className="text-sm text-muted-foreground">{t('inventory.subtitle')}</p>
          </div>
          <Button variant="outline" size="sm">
            <Download className="h-4 w-4 mr-2" />
            Export CSV
          </Button>
        </div>

        <Card className="border-border/60 bg-card/70">
          <CardHeader>
            <CardTitle className="text-lg">Products</CardTitle>
          </CardHeader>
          <CardContent className="overflow-auto">
            {loadingProducts ? (
              <p className="text-sm text-muted-foreground">Loading products...</p>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>SKU</TableHead>
                    <TableHead>Name</TableHead>
                    <TableHead className="text-right">Price</TableHead>
                    <TableHead className="text-right">On Hand</TableHead>
                    <TableHead className="text-right">Forecasted</TableHead>
                    <TableHead>Category</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {(products ?? []).map((p: any) => (
                    <TableRow key={p.id} className="border-border/50">
                      <TableCell className="font-mono text-xs text-muted-foreground">{p.internal_ref || p.id}</TableCell>
                      <TableCell className="font-medium">{p.name}</TableCell>
                      <TableCell className="text-right font-mono">{(p.price ?? 0).toFixed(2)} MAD</TableCell>
                      <TableCell className="text-right font-mono">{p.qty_on_hand ?? 0}</TableCell>
                      <TableCell className="text-right font-mono text-muted-foreground">
                        {p.forecasted ?? 0}
                      </TableCell>
                      <TableCell>
                        <Badge variant="outline">{p.category || '—'}</Badge>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
          </CardContent>
        </Card>

        <Card className="border-border/60 bg-card/70">
          <CardHeader>
            <CardTitle className="text-lg">Recent Stock Moves</CardTitle>
          </CardHeader>
          <CardContent className="overflow-auto">
            {loadingMoves ? (
              <p className="text-sm text-muted-foreground">Loading moves...</p>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Reference</TableHead>
                    <TableHead>Product</TableHead>
                    <TableHead>Source</TableHead>
                    <TableHead>Destination</TableHead>
                    <TableHead className="text-right">Qty</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Date</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {(moves ?? []).map((m: any) => (
                    <TableRow key={m.id} className="border-border/50">
                      <TableCell className="font-mono text-xs text-muted-foreground">{m.name}</TableCell>
                      <TableCell className="font-medium">{m.product}</TableCell>
                      <TableCell>{m.source_location}</TableCell>
                      <TableCell>{m.dest_location}</TableCell>
                      <TableCell className="text-right font-mono">{m.quantity}</TableCell>
                      <TableCell>
                        <Badge variant={m.state === 'done' ? 'default' : 'secondary'} className="capitalize">
                          {m.state || 'unknown'}
                        </Badge>
                      </TableCell>
                      <TableCell className="text-muted-foreground text-xs">{m.date?.slice(0, 10)}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
          </CardContent>
        </Card>
      </div>
    </MainLayout>
  );
}
