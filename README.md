# 📊 Trading System REST API

A Django REST Framework implementation of a stock trading system that allows authenticated users to place trades, upload bulk trades via CSV, and track portfolio values.

---

## 🚀 Features

- 📈 Place buy/sell orders for stocks  
- 📁 Bulk trade upload via CSV  
- ⏱ Automated CSV processing via cron job  
- 💰 Portfolio value tracking  
- 🔐 User authentication  
- ✅ Comprehensive test coverage  

---

## 🛠 Tech Stack

- **Python** 3.9+  
- **Django** 4.2  
- **Django REST Framework** 3.14  
- **SQLite** (Development)  
- **PostgreSQL** (Production-ready)  

---

## ⚙️ Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/benjieperez/trading-system.git
   cd trading-system
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate    # Linux/Mac
   venv\Scripts\activate       # Windows
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up the database:**
   ```bash
   python manage.py migrate
   ```

5. **Create a superuser:**
   ```bash
   python manage.py createsuperuser
   ```

   > Example credentials:  
   > **Email:** root@dev.com  
   > **Password:** 9t3A6>,Dp53N

6. **Run the development server:**
   ```bash
   python manage.py runserver
   ```

---

## 📡 API Endpoints

| Endpoint                    | Method | Description                 |
|----------------------------|--------|-----------------------------|
| `/api/stocks/`             | GET    | List all stocks             |
| `/api/trades/`             | POST   | Place a new trade           |
| `/api/trades/bulk/`        | POST   | Upload CSV of trades        |
| `/api/trades/portfolio/`   | GET    | Get portfolio summary       |

---

## 🧾 CSV Format for Bulk Upload

Example `trades.csv`:

```csv
stock_id,trade_type,quantity
AAPL,BUY,10
GOOGL,SELL,5
MSFT,BUY,15
TSLA,SELL,3
AMZN,BUY,8
```

---

## 🔄 Automated CSV Processing

The system checks the ``trades_data`/` directory every **5 minutes** for new CSV files. After processing, files are moved to `trades_data/processed`.

To manually trigger processing:

```bash
python manage.py process_trades
```

---

## ✅ Testing

Run all tests with coverage:

```bash
pytest --cov
```

### Key Test Files

- `tests/test_models.py` — Model validation  
- `tests/test_views.py` — API endpoints  
- `tests/test_commands.py` — CSV processing  

---

## 🚀 Deployment

For production:

1. **Set environment variables:**

   ```bash
   export SECRET_KEY=your-secret-key
   export DEBUG=0
   export DATABASE_URL=postgres://user:pass@localhost:5432/dbname
   ```

2. **Configure WSGI** with a web server (e.g., Nginx or Apache).

---

## 📁 Environment Variables

| Variable      | Description                   | Default              |
|---------------|-------------------------------|----------------------|
| `SECRET_KEY`  | Django secret key             | -                    |
| `DEBUG`       | Debug mode                    | `1` (True)           |
| `TRADES_DIR`  | CSV processing directory      | `./trades_data`      |