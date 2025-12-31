import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '@/components/contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Separator } from '@/components/ui/separator';
import { useToast } from '@/hooks/use-toast';
import { Loader2, Shield, User, Eye } from 'lucide-react';

export default function Login() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [demoLoading, setDemoLoading] = useState<string | null>(null);
  const { login, demoLogin } = useAuth();
  const { toast } = useToast();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      await login(username, password);
      toast({ title: 'Welcome back!', description: 'Successfully logged in.' });
    } catch (error: any) {
      toast({
        title: 'Login failed',
        description: error.response?.data?.detail || 'Invalid credentials',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleDemoLogin = async (role: 'admin' | 'manager' | 'viewer') => {
    setDemoLoading(role);
    try {
      await demoLogin(role);
      toast({ title: 'Welcome!', description: `Logged in as ${role}` });
    } catch (error: any) {
      toast({
        title: 'Demo login failed',
        description: 'Backend may be unavailable',
        variant: 'destructive',
      });
    } finally {
      setDemoLoading(null);
    }
  };

  const demoButtons = [
    { role: 'admin' as const, icon: Shield, label: 'Admin', description: 'Full access' },
    { role: 'manager' as const, icon: User, label: 'Manager', description: 'Limited write' },
    { role: 'viewer' as const, icon: Eye, label: 'Viewer', description: 'Read only' },
  ];

  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-gradient-to-br from-primary/5 via-background to-primary/10" />
      
      <Card className="w-full max-w-md relative z-10 border-border/50 bg-card/80 backdrop-blur-sm">
        <CardHeader className="text-center pb-2">
          <CardTitle className="text-3xl font-bold tracking-tight">
            ERP<span className="text-primary">Connect</span>
          </CardTitle>
          <CardDescription>
            Sign in to your account to continue
          </CardDescription>
        </CardHeader>
        
        <CardContent className="space-y-6">
          {/* Demo login buttons */}
          <div className="space-y-3">
            <Label className="text-xs uppercase tracking-wide text-muted-foreground">Quick Demo Access</Label>
            <div className="grid grid-cols-3 gap-2">
              {demoButtons.map(({ role, icon: Icon, label, description }) => (
                <Button
                  key={role}
                  variant="outline"
                  className="h-auto py-3 flex flex-col items-center gap-1 hover:bg-primary/10 hover:border-primary/50 transition-all"
                  onClick={() => handleDemoLogin(role)}
                  disabled={!!demoLoading}
                >
                  {demoLoading === role ? (
                    <Loader2 className="h-5 w-5 animate-spin" />
                  ) : (
                    <Icon className="h-5 w-5 text-primary" />
                  )}
                  <span className="font-medium text-sm">{label}</span>
                  <span className="text-[10px] text-muted-foreground">{description}</span>
                </Button>
              ))}
            </div>
          </div>

          <div className="relative">
            <Separator />
            <span className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 bg-card px-2 text-xs text-muted-foreground">
              or sign in with credentials
            </span>
          </div>

          {/* Login form */}
          <form onSubmit={handleLogin} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="username">Username</Label>
              <Input
                id="username"
                placeholder="Enter your username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="bg-muted/50"
                required
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="password">Password</Label>
              <Input
                id="password"
                type="password"
                placeholder="Enter your password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="bg-muted/50"
                required
              />
            </div>
            <Button type="submit" className="w-full" disabled={loading}>
              {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              Sign In
            </Button>
          </form>

          <div className="relative mt-4">
            <div className="absolute inset-0 flex items-center">
              <span className="w-full border-t" />
            </div>
            <div className="relative flex justify-center text-xs uppercase">
              <span className="bg-card px-2 text-muted-foreground">
                New to ERPConnect?
              </span>
            </div>
          </div>

          <Link to="/signup" className="block mt-3">
            <Button variant="outline" className="w-full" type="button">
              Create an account
            </Button>
          </Link>

          <p className="text-xs text-center text-muted-foreground">
            Use demo buttons above for quick access, or connect to your FastAPI backend.
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
