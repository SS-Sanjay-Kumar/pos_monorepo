# 🧾 POS Monorepo — Frontend + Backend Integration

A complete **Point of Sale (POS)** system built with:
- **Frontend:** React + Vite  
- **Backend:** FastAPI (Python)  
- **Database:** MySQL (via Docker Compose)

This monorepo is fully integrated — the backend APIs power all frontend functionality such as user authentication, product and invoice management, and reporting.

---

## 📁 Project Structure

```
pos_monorepo/
├── frontend/                  # React + Vite frontend
│   ├── src/                   # Components, pages, assets
│   ├── package.json
│   └── .env.local             # Frontend environment variables
│
├── backend/                   # FastAPI backend
│   ├── app/                   # FastAPI app modules (routes, schemas, db)
│   ├── venv/                  # Python virtual environment (ignored)
│   ├── requirements.txt
│   └── .env                   # Backend environment variables
│
├── docker-compose.yml          # MySQL setup and network linking
├── .gitignore                  # Ignore build, cache, env files
└── README.md                   # You're here
```

---

## 🧠 Features

✅ User authentication (JWT)  
✅ Role-based access control  
✅ Product and category management  
✅ Invoice and payment modules  
✅ Employee management  
✅ Real-time data updates via REST APIs  
✅ Persistent MySQL storage (Dockerized)

---

## ⚙️ 1. Prerequisites

Make sure you have these installed on your machine:

- **Python 3.12+**
- **Node.js 20.19+**
- **npm** (comes with Node)
- **Docker Desktop** (running)

---

## 🚀 2. Setup Instructions

### 🐍 Backend Setup (FastAPI)

```bash
# navigate to backend
cd backend

# create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# install dependencies
pip install -r requirements.txt

# run backend
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Backend runs at:  
👉 http://127.0.0.1:8000  
Swagger Docs: http://127.0.0.1:8000/docs

---

### 🐳 Database Setup (MySQL via Docker)

```bash
cd ~/Desktop/pos_monorepo
docker compose up -d --no-build mysql
```

✅ Confirm it’s running:
```bash
docker ps
```

Expected:
```
pos_monorepo-mysql-1   mysql:8.0   Up (healthy)   0.0.0.0:3306->3306/tcp
```

---

### ⚛️ Frontend Setup (React + Vite)

```bash
cd frontend

# install dependencies
npm install

# create local environment file
echo "VITE_API_URL=http://127.0.0.1:8000" > .env.local

# start the dev server
npm run dev
```

Frontend runs at:  
👉 http://localhost:5173

---

## 🧩 3. Start / Stop Guide

### ▶️ To start everything:
1. Start MySQL:
   ```bash
   docker compose up -d --no-build mysql
   ```
2. Start backend:
   ```bash
   cd backend
   source venv/bin/activate
   uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
   ```
3. Start frontend:
   ```bash
   cd frontend
   npm run dev
   ```

### 🛑 To stop everything:
```bash
# Stop frontend (in its terminal)
Ctrl + C

# Stop backend
Ctrl + C
deactivate

# Stop MySQL container
cd ~/Desktop/pos_monorepo
docker compose down
```

---

## 🧪 4. Testing Connectivity

- Backend health check:  
  ```bash
  curl http://127.0.0.1:8000/docs
  ```
- Check API in Swagger UI:  
  http://127.0.0.1:8000/docs
- Create a test user and log in via frontend.

---

## 🧑‍💻 5. For Collaborators

### Clone the repo:
```bash
git clone https://github.com/rishi-saran/pos_monorepo.git
cd pos_monorepo
```

### Switch to the integration branch:
```bash
git checkout integration
```

### Run project:
Follow the setup steps above.

### Create your own feature branch:
```bash
git checkout -b feature/<your-feature-name>
git push -u origin feature/<your-feature-name>
```

---

## 💾 6. Data Persistence

All MySQL data is stored in a Docker volume:
```
pos_monorepo_mysql_data
```
So you can safely stop and restart containers — your data will remain intact.

---

## 🧰 7. Common Issues

| Issue | Solution |
|-------|-----------|
| `ModuleNotFoundError` | Ensure venv is activated and dependencies installed |
| `Access denied for user 'myuser'` | Check MySQL credentials in backend `.env` |
| `Docker not found` | Install Docker Desktop and restart terminal |
| CORS errors in browser | Ensure backend `origins` list includes `http://localhost:5173` and `http://127.0.0.1:5173` |

---

## 🏁 8. Future Enhancements
- Containerize the backend service (`Dockerfile`)
- Add Alembic migrations for DB versioning
- Deploy to Render / Railway
- Add unit tests and CI/CD workflow

---

## 👨‍💻 Author
**Rishi Saran**  
**Sanjay Kumar S S**, 
**Srinithya M**, 
**Navin S**, 
**Shrinithi C S**

📍 Coimbatore, Tamil Nadu  
💻 Full Stack Developer | AI Enthusiast  
🔗 [GitHub](https://github.com/rishi-saran)

---

## 📜 License
This project is licensed under the MIT License — feel free to use and modify it.
