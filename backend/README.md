# Hotel Billing System — Setup Guide

## Quick Setup Commands

### 1️⃣ Clone the repository (or navigate to project)
```bash
cd hotel_billing
```

### 2️⃣ Create and activate virtual environment
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3️⃣ Install dependencies
```bash
pip install -r requirements.txt
```

### 4️⃣ Start the FastAPI server
```bash
pkill -f "uvicorn" || true
uvicorn app.main:app --reload --port 8000 --log-level info
```

### 5️⃣ Run automated backend tests
```bash
./test_all.sh
```


---

✅ Server runs at: http://127.0.0.1:8000  
✅ Health check: http://127.0.0.1:8000/health  
✅ HTML frontend (temp): http://127.0.0.1:5500/app/index.html

### Important Note:
File: invoice.json is kept test the output from the APIs.
File: output.txt is the output from running sql commands(for initial testing).
