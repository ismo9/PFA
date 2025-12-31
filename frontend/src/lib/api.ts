import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Token management
let accessToken: string | null = localStorage.getItem('access_token');

export const setAccessToken = (token: string | null) => {
  accessToken = token;
  if (token) {
    localStorage.setItem('access_token', token);
  } else {
    localStorage.removeItem('access_token');
  }
};

export const getAccessToken = () => accessToken;

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {
    if (accessToken) {
      config.headers.Authorization = `Bearer ${accessToken}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      setAccessToken(null);
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth API
export const api = {
  auth: {
    login: async (username: string, password: string) => {
      const formData = new URLSearchParams();
      formData.append('username', username);
      formData.append('password', password);
      const response = await apiClient.post('/auth/login', formData, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      });
      return response.data;
    },
    register: async (data: { username: string; email: string; password: string; full_name: string }) => {
      const response = await apiClient.post('/auth/register', data);
      return response.data;
    },
    demoLogin: async (role: 'admin' | 'manager' | 'viewer') => {
      const response = await apiClient.post(`/auth/demo/${role}`);
      return response.data;
    },
    me: async () => {
      const response = await apiClient.get('/auth/me');
      return response.data;
    },
    logout: async () => {
      const response = await apiClient.post('/auth/logout');
      return response.data;
    },
  },
  
  dashboard: {
    getOverview: async () => {
      const response = await apiClient.get('/dashboard/overview');
      return response.data;
    },
    getSalesTrends: async (period: 'daily' | 'weekly' | 'monthly' = 'daily', days = 30) => {
      const response = await apiClient.get(`/dashboard/sales_trends?period=${period}&days=${days}`);
      return response.data;
    },
    getTopProducts: async (metric: 'quantity' | 'revenue' = 'quantity', days = 30, limit = 10) => {
      const response = await apiClient.get(`/dashboard/top_products?metric=${metric}&days=${days}&limit=${limit}`);
      return response.data;
    },
    getStockStatus: async () => {
      const response = await apiClient.get('/dashboard/stock_status');
      return response.data;
    },
    getABCXYZSummary: async (days = 60) => {
      const response = await apiClient.get(`/dashboard/abcxyz_summary?days=${days}`);
      return response.data;
    },
  },
  
  inventory: {
    getProducts: async (limit = 0) => {
      const response = await apiClient.get('/products', { params: { limit } });
      return response.data;
    },
    getProduct: async (id: string | number) => {
      const response = await apiClient.get(`/products/${id}`);
      return response.data;
    },
    getStockMoves: async (limit = 0) => {
      const response = await apiClient.get('/inventory/moves', { params: { limit } });
      return response.data;
    },
  },
  
  ai: {
    getForecast: async (productId: string | number, horizon: number = 30, lookbackDays = 180) => {
      const response = await apiClient.get(`/ai/forecast/${productId}?horizon_days=${horizon}&lookback_days=${lookbackDays}`);
      return response.data;
    },
    getReplenishment: async (withRop = true, options?: { leadTime?: number; safetyStock?: number }) => {
      if (withRop) {
        const response = await apiClient.get(
          `/ai/replenishment/with_rop?default_lead_time_days=${options?.leadTime ?? 7}&safety_stock_days=${options?.safetyStock ?? 3}`
        );
        return response.data;
      }
      const response = await apiClient.get('/ai/replenishment/recommendations');
      return response.data;
    },
    getDemand: async (lookbackDays = 60, limit = 200) => {
      const response = await apiClient.get(`/ai/demand?lookback_days=${lookbackDays}&limit=${limit}`);
      return response.data;
    },
    getSegmentation: async (days = 60) => {
      const response = await apiClient.get(`/ai/segmentation?days=${days}`);
      return response.data;
    },
    getAnomalies: async (days = 30, z = 3) => {
      const response = await apiClient.get(`/ai/anomalies?days=${days}&z=${z}`);
      return response.data;
    },
    getAlerts: async () => {
      const response = await apiClient.get('/ai/alerts');
      return response.data;
    },
  },
  
  kpi: {
    getMetrics: async (days = 30) => {
      const response = await apiClient.get(`/kpi/metrics?days=${days}`);
      return response.data;
    },
    getMetric: async (metricName: string, days = 30) => {
      const response = await apiClient.get(`/kpi/metric/${metricName}?days=${days}`);
      return response.data;
    },
    compareProducts: async (productIds: number[], metrics: string[] = ['revenue', 'quantity'], days = 30) => {
      const response = await apiClient.get(
        `/kpi/comparison?product_ids=${productIds.join(',')}&metrics=${metrics.join(',')}&days=${days}`
      );
      return response.data;
    },
    getCatalog: async () => {
      const response = await apiClient.get('/kpi/catalog');
      return response.data;
    },
  },
  
  health: {
    app: async () => {
      const response = await apiClient.get('/health/app');
      return response.data;
    },
    odoo: async () => {
      const response = await apiClient.get('/health/odoo');
      return response.data;
    },
  },

  notifications: {
    getAlerts: async () => {
      const response = await apiClient.get('/ai/alerts');
      return response.data;
    },
  },
};

export default apiClient;
