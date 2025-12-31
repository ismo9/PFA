# ERPConnect - Intelligent Decision Support Module

**A FastAPI-based intelligent decision support system that integrates with Odoo ERP to provide AI-powered analytics, demand forecasting, inventory optimization, and business intelligence.**

**Academic Year:** 2025/2026  
**Institution:** EMSI - École Marocaine des Sciences de l'Ingénieur  
**Program:** 5th Year Engineering - Computer Science and Networks  
**Project Type:** Final Year Project (PFA - Projet de Fin d'Année)

---

## 📋 Table of Contents

- [Project Overview](#project-overview)
- [Features](#features)
- [System Architecture](#system-architecture)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [API Documentation](#api-documentation)
- [Feature Details](#feature-details)
- [AI Algorithms Explained](#ai-algorithms-explained)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)
- [Project Structure](#project-structure)
- [Dependencies](#dependencies)
- [License](#license)

---

## 🎯 Project Overview

ERPConnect is an intelligent decision support module designed to enhance Odoo ERP systems with advanced analytics and AI-driven insights. The system addresses critical limitations in standard ERP reporting by providing:

- **Predictive Analytics**: Machine learning-based demand forecasting
- **Intelligent Alerts**: Proactive anomaly detection in sales patterns
- **Inventory Optimization**: ROP (Reorder Point) calculations and replenishment recommendations
- **Business Intelligence**: 30+ KPIs across 6 categories
- **Product Segmentation**: ABC/XYZ analysis for strategic inventory management

### Business Problem Solved

Traditional ERP systems (Odoo, Dolibarr) provide basic reporting but lack:
- Predictive capabilities for demand forecasting
- Intelligent alerts beyond simple threshold-based notifications
- Advanced analytics for inventory optimization
- Actionable recommendations for business decisions

ERPConnect fills this gap by adding an AI layer on top of existing ERP data.

---

## ✨ Features

### 1. **ERP Data Integration**
- XML-RPC connection to Odoo ERP
- Real-time data synchronization
- Support for multiple Odoo models (products, sales, purchases, inventory)
- Efficient bulk data extraction with caching (90-120s TTL)

### 2. **Demand Prediction**
- 30-day demand forecasts per product
- 7-day moving average smoothing
- Trend detection (UP/DOWN/STABLE)
- Confidence scoring based on data quality

### 3. **Machine Learning Forecasting**
- scikit-learn LinearRegression with PolynomialFeatures (degree=2)
- Automated nightly training for top 50 products
- Model persistence using joblib
- Metrics: MAE, sMAPE, MAPE
- 95% confidence intervals (±1.96σ)

### 4. **Inventory Replenishment**
- ROP (Reorder Point) calculations: `ROP = avg_daily_sales × lead_time + safety_stock`
- Suggested order quantities
- Action categories: ORDER NOW / MONITOR / OK
- Configurable lead time and safety stock parameters

### 5. **ABC/XYZ Product Segmentation**
- **ABC**: Revenue-based (A=top 20%, B=next 30%, C=rest)
- **XYZ**: Variability-based (X=low, Y=medium, Z=high)
- 3×3 matrix with strategy recommendations
- Focus on AX items (high value, stable demand)

### 6. **Sales Anomaly Detection**
- Z-score method for spike/drop detection
- Configurable threshold (default: z≥3.0)
- Severity levels: High/Medium/Low
- Daily time series analysis

### 7. **Comprehensive KPI System**
- 30+ business metrics across 6 categories:
  - Revenue & Sales (5 metrics)
  - Orders & Customers (4 metrics)
  - Inventory & Stock (6 metrics)
  - Products (4 metrics)
  - AI & Forecasting (4 metrics)
  - Efficiency & Operations (3 metrics)
- Real-time calculation from Odoo data
- Historical trend tracking
- Product comparison capabilities

### 8. **Authentication & Authorization**
- JWT token-based authentication
- 3 user roles:
  - **Admin**: Full system access, configuration
  - **Manager**: Dashboard viewing, forecasts, reports
  - **Viewer**: Read-only access
- OAuth2 password flow
- 8-hour token expiration

### 9. **Dashboard Endpoints**
- Executive overview (products, stock value, sales)
- Sales trends (daily/weekly/monthly aggregation)
- Top products by quantity/revenue
- Stock status distribution
- ABC/XYZ summary matrix

### 10. **System Health Monitoring**
- Application health checks (scheduler status)
- Odoo connection verification
- Background job monitoring

---

## 🏗️ System Architecture

### Technology Stack

**Backend Framework:**
- FastAPI (modern async web framework)
- Uvicorn (ASGI server)
- Pydantic (data validation)

**Machine Learning:**
- scikit-learn (LinearRegression, PolynomialFeatures)
- NumPy (numerical computations)
- pandas (data manipulation)
- joblib (model serialization)

**Authentication:**
- python-jose (JWT encoding/decoding)
- passlib (password hashing)
- OAuth2PasswordBearer

**Integration:**
- xmlrpc.client (Odoo connector)
- python-dotenv (environment configuration)

**Background Jobs:**
- APScheduler (cron-like scheduling)

**Caching:**
- In-memory TTL cache (custom implementation)

### Architectural Layers

```
┌─────────────────────────────────────┐
│     API Layer (FastAPI Routers)     │
│  /auth /ai /dashboard /kpi /health  │
└─────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────┐
│      Business Logic (Services)      │
│  AI Services, Auth, Cache, Odoo     │
└─────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────┐
│    Integration Layer (XML-RPC)      │
│        Odoo Connector               │
└─────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────┐
│      External Systems               │
│   Odoo ERP (PostgreSQL backend)     │
└─────────────────────────────────────┘
```

---

## 📦 Prerequisites

### Required Software

1. **Python 3.8 or higher**
   - Download: https://www.python.org/downloads/
   - Verify installation: `python --version`

2. **Odoo ERP Server (version 14.0 or higher)**
   - Running Odoo instance accessible via network
   - XML-RPC enabled (default port: 8069)
   - Valid user credentials with API access

3. **pip (Python package manager)**
   - Usually included with Python
   - Verify: `pip --version`

### Optional but Recommended

- **Virtual Environment Tool** (venv, built-in with Python 3.3+)
- **Git** (for version control)
- **Postman or similar** (for API testing)

### System Requirements

- **RAM**: Minimum 2GB, recommended 4GB
- **Storage**: 500MB for application + models
- **OS**: Windows, Linux, or macOS
- **Network**: Access to Odoo server (LAN or internet)

---

## 🚀 Installation

### Step 1: Clone or Download the Project

```bash
# If using Git
git clone <repository-url>
cd erpconnect-backend

# Or extract the ZIP file to a directory
cd erpconnect-backend
```

### Step 2: Create Virtual Environment (Recommended)

**Windows:**
```powershell
python -m venv .venv
.venv\Scripts\activate
```

**Linux/macOS:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

You should see `(.venv)` in your terminal prompt.

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

This will install all required packages:
- fastapi
- uvicorn[standard]
- python-dotenv
- requests
- pydantic
- pandas
- numpy
- scikit-learn
- joblib
- python-dateutil
- APScheduler
- python-jose[cryptography]
- passlib[bcrypt]
- python-multipart

**Installation time:** 2-5 minutes depending on internet speed.

### Step 4: Verify Installation

```bash
python -c "import fastapi, sklearn, pandas; print('All dependencies installed successfully!')"
```

If no errors appear, installation was successful.

---

## ⚙️ Configuration

### Step 1: Create Environment File

Copy the example environment file:

```bash
cp .env.example .env
```

### Step 2: Configure Odoo Connection

Edit the `.env` file with your Odoo details:

```env
ODOO_URL=http://your-odoo-server:8069
ODOO_DB=your_database_name
ODOO_USERNAME=your_odoo_email@example.com
ODOO_PASSWORD=your_odoo_password
```

**Important Notes:**
- `ODOO_URL`: Full URL including protocol (http:// or https://)
- `ODOO_DB`: Exact database name from Odoo
- `ODOO_USERNAME`: Email used to login to Odoo
- `ODOO_PASSWORD`: Odoo user password
- **Security**: Never commit `.env` to version control

### Step 3: Verify Odoo Connection

Test the connection:

```bash
python -c "from app.services.odoo_connector import OdooConnector; conn = OdooConnector(); print('Connected successfully!' if conn.uid else 'Connection failed')"
```

### Step 4: Create Models Directory (Automatic)

The application will automatically create `models/forecasts/` directory for storing ML models.

---

## ▶️ Running the Application

### Start the Server

**Development Mode (with auto-reload):**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Production Mode:**
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Verify Server is Running

Open your browser:
- **API Documentation (Swagger)**: http://localhost:8000/docs
- **Alternative Docs (ReDoc)**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health/app

### Console Output

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### Stopping the Server

Press `CTRL+C` in the terminal.

---

## 📚 API Documentation

### Interactive Documentation

FastAPI provides automatic interactive documentation:

1. **Swagger UI**: http://localhost:8000/docs
   - Try out endpoints directly
   - See request/response schemas
   - Test authentication

2. **ReDoc**: http://localhost:8000/redoc
   - Clean, three-panel design
   - Better for reference

### Authentication

Most endpoints require JWT authentication:

1. **Get Token:**
   ```bash
   curl -X POST "http://localhost:8000/auth/login" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=admin@erp.com&password=admin123"
   ```

   Response:
   ```json
   {
     "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
     "token_type": "bearer"
   }
   ```

2. **Use Token:**
   ```bash
   curl -X GET "http://localhost:8000/dashboard/overview" \
     -H "Authorization: Bearer YOUR_TOKEN_HERE"
   ```

### Demo Credentials

| Role    | Username            | Password   | Access Level |
|---------|---------------------|------------|--------------|
| Admin   | admin@erp.com       | admin123   | Full access  |
| Manager | manager@erp.com     | manager123 | Dashboards, AI |
| Viewer  | viewer@erp.com      | viewer123  | Read-only    |

**Note:** These are demo credentials. For production, use secure passwords and bcrypt hashing.

### Key API Endpoints

#### Authentication
- `POST /auth/login` - Get JWT token
- `GET /auth/me` - Get current user info

#### Dashboard
- `GET /dashboard/overview` - Executive summary
- `GET /dashboard/sales_trends?period=daily&days=30` - Sales over time
- `GET /dashboard/top_products?metric=quantity&limit=10` - Top sellers
- `GET /dashboard/stock_status` - Inventory distribution
- `GET /dashboard/abcxyz_summary` - Segmentation matrix

#### AI & Analytics
- `GET /ai/demand?lookback_days=60&limit=200` - 30-day demand forecast
- `GET /ai/forecast/{product_id}?horizon_days=30` - ML forecast for product
- `GET /ai/replenishment/with_rop?lead_time=7&safety=3` - ROP recommendations
- `GET /ai/segmentation?days=60` - ABC/XYZ analysis
- `GET /ai/anomalies?days=30&z=3.0` - Sales spike/drop detection

#### KPIs
- `GET /kpi/metrics?days=30` - All 30+ KPIs
- `GET /kpi/metric/{metric_name}?days=90` - Specific KPI with trend
- `GET /kpi/comparison?product_ids=101,102&metrics=revenue,quantity` - Compare products
- `GET /kpi/catalog` - List all available KPIs

#### System Health
- `GET /health/app` - Scheduler status
- `GET /health/odoo` - Odoo connection check

---

## 🧠 Feature Details

### 1. Demand Prediction (`/ai/demand`)

**What it does:**
Predicts 30-day demand for each product based on historical sales data.

**Parameters:**
- `lookback_days` (default: 60): How many days of history to analyze
- `limit` (default: 200): Maximum products to return

**Algorithm:**
1. Fetch sales order lines for past `lookback_days`
2. Aggregate to daily quantities
3. Apply 7-day moving average to smooth noise
4. Calculate trend slope (early vs. late window)
5. Compute confidence score (data coverage + variability + sample count)
6. Multiply current daily demand by 30

**Output:**
```json
{
  "total": 150,
  "items": [
    {
      "product_id": 101,
      "product_name": "Laptop Dell XPS",
      "predicted_30d_demand": 45.2,
      "trend": "UP",
      "confidence": 0.85
    }
  ]
}
```

**Use Cases:**
- Procurement planning
- Production scheduling
- Sales forecasting

---

### 2. ML Forecasting (`/ai/forecast/{product_id}`)

**What it does:**
Generates detailed forecast using trained machine learning model or baseline heuristic.

**Parameters:**
- `product_id` (path): Product ID from Odoo
- `horizon_days` (default: 30): How many days ahead to forecast
- `lookback_days` (default: 180): Historical data window

**Algorithm:**

**Training (nightly, automated):**
1. Fetch sales history (180 days)
2. Build daily series + apply 7-day moving average
3. Create polynomial features (degree=2): `[t, t²]`
4. Train LinearRegression: `y = β₀ + β₁t + β₂t²`
5. Calculate metrics (MAE, sMAPE, MAPE)
6. Save model to `models/forecasts/product_{id}.joblib`

**Prediction:**
1. Load trained model (or train on-the-fly if missing)
2. Extend time index to future horizon
3. Predict: `y_future = model.predict(X_future)`
4. Calculate confidence intervals: `CI = ŷ ± 1.96 × σ_residual`
5. Aggregate to 7d/30d/90d totals

**Output:**
```json
{
  "product_id": 101,
  "horizon_days": 30,
  "daily_forecast": [12.3, 12.5, 12.8, ...],
  "totals": {
    "7d": 85.4,
    "30d": 368.2,
    "90d": 1104.6
  },
  "confidence_interval": {
    "low": [10.1, 10.3, ...],
    "high": [14.5, 14.7, ...]
  },
  "model_type": "LinearRegression(poly=2)",
  "metrics": {
    "mae": 2.3,
    "smape": 0.15,
    "mape": 0.18
  }
}
```

**Use Cases:**
- Long-term demand planning
- Budget forecasting
- Capacity planning

---

### 3. Replenishment Recommendations (`/ai/replenishment/with_rop`)

**What it does:**
Calculates optimal reorder points and suggests order quantities.

**Parameters:**
- `default_lead_time_days` (default: 7): Supplier delivery time
- `safety_stock_days` (default: 3): Buffer stock in days

**Algorithm:**

**ROP Formula:**
```
ROP = avg_daily_sales × lead_time_days + avg_daily_sales × safety_stock_days
```

**Suggested Order Quantity:**
```
suggested_qty = max(0, ROP - current_stock)
```

**Action Determination:**
- `ORDER NOW`: stock < ROP and suggested_qty > 0
- `MONITOR`: stock cover between 7-14 days
- `OK`: sufficient stock

**Output:**
```json
{
  "replenishment_recommendations": [
    {
      "product_id": 101,
      "product_name": "Laptop Dell XPS",
      "current_stock": 15,
      "avg_daily_sales": 3.2,
      "rop": 32.0,
      "suggested_order_qty": 17.0,
      "action": "ORDER NOW",
      "urgency": "HIGH"
    }
  ],
  "rop_params": {
    "default_lead_time_days": 7,
    "safety_stock_days": 3
  }
}
```

**Use Cases:**
- Inventory optimization
- Stockout prevention
- Automated procurement

---

### 4. ABC/XYZ Segmentation (`/ai/segmentation`)

**What it does:**
Classifies products by value (ABC) and demand variability (XYZ) for strategic inventory management.

**Parameters:**
- `days` (default: 60): Analysis period

**Algorithm:**

**ABC Classification (Revenue):**
1. Calculate total revenue per product
2. Sort by revenue descending
3. Compute cumulative percentage
4. Assign classes:
   - **A**: Cumulative ≤ 20% (high value)
   - **B**: Cumulative ≤ 50% (medium value)
   - **C**: Cumulative > 50% (low value)

**XYZ Classification (Variability):**
1. Calculate daily demand for each product
2. Compute coefficient of variation: `CV = std / mean`
3. Assign classes:
   - **X**: CV < 0.3 (stable)
   - **Y**: 0.3 ≤ CV < 0.7 (moderate)
   - **Z**: CV ≥ 0.7 (variable)

**Output:**
```json
{
  "by_product": [
    {
      "product_id": 101,
      "product_name": "Laptop Dell XPS",
      "abc_class": "A",
      "xyz_class": "X",
      "revenue": 45000,
      "variability": 0.25
    }
  ],
  "matrix": {
    "AX": 12, "AY": 5, "AZ": 3,
    "BX": 8, "BY": 15, "BZ": 7,
    "CX": 20, "CY": 30, "CZ": 50
  },
  "recommendations": {
    "AX": "Tight control, frequent review, high service level",
    "AZ": "Close monitoring, safety stock, multi-sourcing",
    "CZ": "Monitor periodically, low safety stock"
  }
}
```

**Use Cases:**
- Inventory prioritization
- Safety stock allocation
- Supplier management

---

### 5. Anomaly Detection (`/ai/anomalies`)

**What it does:**
Detects unusual sales patterns (spikes or drops) using statistical methods.

**Parameters:**
- `days` (default: 30): Analysis window
- `z` (default: 3.0): Z-score threshold

**Algorithm:**

**Z-Score Method:**
1. Build daily sales quantity series
2. Calculate mean (μ) and standard deviation (σ)
3. For each day: `z = (x - μ) / σ`
4. Flag if `|z| ≥ threshold`
5. Classify:
   - **SPIKE**: z > 0
   - **DROP**: z < 0
6. Severity:
   - **High**: |z| ≥ 4.0
   - **Medium**: 3.0 ≤ |z| < 4.0
   - **Low**: 2.0 ≤ |z| < 3.0

**Output:**
```json
{
  "anomalies": [
    {
      "date": "2025-01-15",
      "product_id": 101,
      "product_name": "Laptop Dell XPS",
      "type": "SPIKE",
      "actual_quantity": 25,
      "expected_quantity": 12.3,
      "z_score": 4.2,
      "severity": "HIGH",
      "impact": "Potential stockout risk"
    }
  ],
  "summary": {
    "total_anomalies": 8,
    "spikes": 5,
    "drops": 3
  }
}
```

**Use Cases:**
- Operational alerts
- Demand pattern analysis
- Marketing campaign impact assessment

---

### 6. KPI System (`/kpi/metrics`)

**What it does:**
Calculates 30+ business metrics in real-time from Odoo data.

**Available KPI Categories:**

1. **Revenue & Sales (5 metrics)**
   - Total Revenue
   - Revenue Growth %
   - Gross Margin %
   - Average Order Value
   - Revenue per Product

2. **Orders & Customers (4 metrics)**
   - Total Orders
   - Order Growth %
   - Fulfillment Rate %
   - Backorder %

3. **Inventory & Stock (6 metrics)**
   - Stock Value
   - Turnover Ratio
   - Stock Cover Days
   - Low Stock Count
   - Out of Stock Count
   - Products Under ROP

4. **Products (4 metrics)**
   - Active Products
   - Total Products
   - New Products (30d)
   - Average Product Price

5. **AI & Forecasting (4 metrics)**
   - Forecast Accuracy (sMAPE)
   - Anomaly Count (7d/30d)
   - Products with ML Models
   - Last Training Date

6. **Efficiency & Operations (3 metrics)**
   - Average Lead Time
   - Order Cycle Time
   - On-Time Delivery %

**Output:**
```json
{
  "metrics": [
    {
      "name": "total_revenue",
      "value": 458320.50,
      "unit": "€",
      "change_percent": 12.5,
      "status": "good"
    },
    {
      "name": "forecast_accuracy",
      "value": 0.15,
      "unit": "sMAPE",
      "description": "Lower is better"
    }
  ],
  "generated_at": "2025-01-15T10:30:00Z"
}
```

---

## 🔬 AI Algorithms Explained

### 1. Moving Average Smoothing

**Purpose:** Reduce noise in time series data

**Formula:**
```
MA(t) = (1/k) × Σ(x[t-k+1] to x[t])
```
where k = window size (7 days)

**Why 7 days?**
- Weekly seasonality captured
- Balance between smoothing and responsiveness
- Sufficient data points for stability

---

### 2. Trend Detection

**Purpose:** Classify demand direction

**Method:**
Calculate slope between early and late smoothed windows:
```
trend_strength = (MA_late - MA_early) / n
```

**Classification:**
- `UP` if slope > 0.2
- `DOWN` if slope < -0.2
- `STABLE` otherwise

---

### 3. Polynomial Regression

**Purpose:** Capture non-linear demand patterns

**Features:**
- Time index: t (linear trend)
- Time squared: t² (acceleration/deceleration)

**Model:**
```
y = β₀ + β₁t + β₂t²
```

**Why degree 2?**
- Captures basic curvature
- Avoids overfitting
- Computationally efficient

---

### 4. Confidence Intervals

**Purpose:** Quantify forecast uncertainty

**Method:**
Residual-based standard error:
```
σ_residual = std(y_actual - y_predicted)
CI = ŷ ± 1.96 × σ_residual
```

**Interpretation:**
95% probability that actual value falls within interval

---

### 5. sMAPE (Symmetric Mean Absolute Percentage Error)

**Purpose:** Measure forecast accuracy

**Formula:**
```
sMAPE = (100%/n) × Σ(2×|y_actual - y_forecast| / (|y_actual| + |y_forecast|))
```

**Why sMAPE over MAPE?**
- Handles zero values gracefully
- Symmetric (no bias towards over/under forecasting)
- Bounded (0-200%)

**Interpretation:**
- < 10%: Excellent
- 10-20%: Good
- 20-50%: Acceptable
- > 50%: Poor

---

## 🧪 Testing

### Manual Testing via Swagger UI

1. Start the server: `uvicorn app.main:app --reload`
2. Open: http://localhost:8000/docs
3. Authenticate:
   - Click "Authorize" button
   - Enter: `admin@erp.com` / `admin123`
4. Try endpoints:
   - Expand `/dashboard/overview`
   - Click "Try it out"
   - Click "Execute"
   - View response

### Testing with cURL

```bash
# Get token
TOKEN=$(curl -s -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@erp.com&password=admin123" \
  | python -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

# Test dashboard
curl -X GET "http://localhost:8000/dashboard/overview" \
  -H "Authorization: Bearer $TOKEN"

# Test AI demand
curl -X GET "http://localhost:8000/ai/demand?lookback_days=60&limit=5" \
  -H "Authorization: Bearer $TOKEN"

# Test forecast
curl -X GET "http://localhost:8000/ai/forecast/101?horizon_days=30" \
  -H "Authorization: Bearer $TOKEN"
```

### Testing Background Jobs

Check scheduler status:
```bash
curl -X GET "http://localhost:8000/health/app"
```

Trigger manual training (if endpoint exists):
```bash
python -c "from app.tasks.scheduler import train_ml_models; train_ml_models()"
```

---

## 🔧 Troubleshooting

### Issue: Server won't start

**Error:** `ModuleNotFoundError: No module named 'fastapi'`

**Solution:**
```bash
# Activate virtual environment
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Reinstall dependencies
pip install -r requirements.txt
```

---

### Issue: Odoo connection failed

**Error:** Connection timeout or authentication error

**Solutions:**

1. **Check Odoo is running:**
   ```bash
   curl http://your-odoo-server:8069
   # Should return HTML page
   ```

2. **Verify credentials:**
   - Login to Odoo web interface with same credentials
   - Check database name exactly matches

3. **Test XML-RPC:**
   ```python
   import xmlrpc.client
   url = "http://your-odoo-server:8069"
   common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common")
   print(common.version())  # Should print Odoo version
   ```

4. **Firewall/Network:**
   - Ensure port 8069 is open
   - Check if Odoo is accessible from your network

---

### Issue: Empty forecast results

**Symptom:** API returns empty arrays or zero forecasts

**Possible Causes:**

1. **Insufficient historical data:**
   - ML requires minimum 14 days of sales
   - Check: `GET /ai/demand` for data availability

2. **No sales for product:**
   - Baseline and ML both return zeros
   - Expected behavior for inactive products

3. **Model not trained:**
   - Wait for nightly job (midnight)
   - Or train manually (see Testing section)

---

### Issue: High memory usage

**Symptom:** System slows down or crashes

**Solutions:**

1. **Limit product catalog:**
   - Reduce `limit` parameter in requests
   - Filter by active products only

2. **Adjust cache TTL:**
   - Edit `app/services/cache.py`
   - Reduce TTL from 120s to 60s

3. **Increase system RAM:**
   - Minimum 4GB recommended for production

---

### Issue: Slow API responses

**Symptom:** Requests take >5 seconds

**Solutions:**

1. **Check cache:**
   - Second request should be <10ms
   - If not, caching may not be working

2. **Optimize Odoo queries:**
   - Ensure Odoo server is performant
   - Add indexes to Odoo database

3. **Reduce lookback days:**
   - Use `lookback_days=30` instead of 180
   - Fewer data points to process

4. **Enable production mode:**
   - Use `--workers 4` for parallel processing

---

## 📁 Project Structure

```
erpconnect-backend/
├── app/
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py               # Configuration settings
│   ├── auth.py                 # JWT authentication logic
│   ├── routers/                # API route definitions
│   │   ├── auth.py             # /auth endpoints
│   │   ├── ai.py               # /ai endpoints
│   │   ├── dashboard.py        # /dashboard endpoints
│   │   ├── kpi.py              # /kpi endpoints
│   │   ├── health.py           # /health endpoints
│   │   ├── products.py         # /products CRUD
│   │   ├── sales.py            # /sales CRUD
│   │   ├── purchases.py        # /purchases CRUD
│   │   ├── invoices.py         # /invoices CRUD
│   │   └── inventory.py        # /inventory CRUD
│   ├── services/               # Business logic layer
│   │   ├── odoo_connector.py   # Odoo XML-RPC integration
│   │   ├── cache.py            # In-memory TTL cache
│   │   ├── data_service.py     # Data aggregation
│   │   ├── ai_service.py       # AI orchestration
│   │   └── ai/                 # AI algorithm modules
│   │       ├── demand.py       # Demand prediction
│   │       ├── ml_forecast.py  # ML forecasting
│   │       ├── forecast.py     # Baseline forecasting
│   │       ├── replenishment.py # ROP calculations
│   │       ├── segmentation.py  # ABC/XYZ analysis
│   │       ├── anomalies.py    # Anomaly detection
│   │       └── alerts.py       # Alert generation
│   └── tasks/                  # Background jobs
│       └── scheduler.py        # APScheduler configuration
├── models/                     # ML model storage
│   └── forecasts/              # Trained models (.joblib)
├── logs/                       # Application logs
├── .env                        # Environment variables (not in repo)
├── .env.example                # Environment template
├── requirements.txt            # Python dependencies
├── README.md                   # This file
└── PROJECT_SUMMARY.md          # Detailed feature summary
```

---

## 📦 Dependencies

### Core Framework (FastAPI)
- **fastapi**: Modern async web framework
- **uvicorn[standard]**: ASGI server with websockets and HTTP/2

### Data Processing
- **pandas**: Data manipulation and analysis
- **numpy**: Numerical computations

### Machine Learning
- **scikit-learn**: ML algorithms (LinearRegression, PolynomialFeatures)
- **joblib**: Model serialization/deserialization

### Authentication
- **python-jose[cryptography]**: JWT encoding/decoding
- **passlib[bcrypt]**: Password hashing
- **python-multipart**: Form data parsing

### Integration
- **requests**: HTTP client (Odoo REST fallback)
- **python-dateutil**: Date parsing utilities

### Background Jobs
- **APScheduler**: Cron-like task scheduling

### Configuration
- **python-dotenv**: Environment variable management
- **pydantic**: Data validation (included with FastAPI)

**Total install size:** ~200MB

---

## 📄 License

This project is part of a **Final Year Engineering Project (PFA)** at EMSI.

**Academic Use Only**

The source code is provided for educational and evaluation purposes as part of the academic requirements for the 5th-year Computer Science and Networks Engineering program.

**Restrictions:**
- Not for commercial use without proper authorization
- Odoo is licensed under LGPL v3
- Third-party libraries retain their respective licenses

---

## 👥 Authors

**Students:**
- Ismail Moustatraf
- Ibrahim Hanna

**Program:** 5th Year Engineering - Computer Science and Networks  
**Institution:** EMSI - École Marocaine des Sciences de l'Ingénieur  
**Academic Year:** 2024/2025

**Academic Supervisor:**
- Abderrahim Larhlimi

---

## 📞 Support

For questions or issues related to this project:

1. **Check Documentation:**
   - README.md (this file)
   - PROJECT_SUMMARY.md (feature details)
   - REPORT.txt (academic report)

2. **API Documentation:**
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

3. **Troubleshooting:**
   - See [Troubleshooting](#troubleshooting) section above

4. **Academic Inquiries:**
   - Contact academic supervisor

---

## 🎯 Quick Reference

### Start Development Server
```bash
.venv\Scripts\activate  # Activate virtual environment
uvicorn app.main:app --reload --port 8000
```

### Access Documentation
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Demo Credentials
- Admin: `admin@erp.com` / `admin123`
- Manager: `manager@erp.com` / `manager123`
- Viewer: `viewer@erp.com` / `viewer123`

### Key Endpoints
- Dashboard: `GET /dashboard/overview`
- Demand Forecast: `GET /ai/demand`
- ML Forecast: `GET /ai/forecast/{product_id}`
- ROP: `GET /ai/replenishment/with_rop`
- Segmentation: `GET /ai/segmentation`
- Anomalies: `GET /ai/anomalies`

### Environment Variables
```env
ODOO_URL=http://localhost:8069
ODOO_DB=your_database
ODOO_USERNAME=your_email
ODOO_PASSWORD=your_password
```

---

**Last Updated:** December 2024  
**Version:** 1.0.0  
**Status:** ✅ Production Ready
