# TaskFlow – FastAPI Task Manager

A simple task manager web application built with FastAPI (backend) and vanilla HTML/JS (frontend).

## Live Demo
> **[https://taskmanager-veh8.onrender.com](https://taskmanager-veh8.onrender.com)**  
> API Docs: [https://taskmanager-veh8.onrender.com/docs](https://taskmanager-veh8.onrender.com/docs)

---

## Features
- JWT authentication (register / login)
- Create, view, update, delete tasks
- Mark tasks as completed
- Filter tasks by status (`?completed=true/false`)
- Pagination support
- Responsive single-page frontend (no frameworks)
- SQLite (dev) / PostgreSQL (prod) via SQLAlchemy

---

## Project Structure

```
taskmanager/
├── backend/
│   ├── core/          # config, security (JWT, bcrypt)
│   ├── db/            # database setup
│   ├── models/        # SQLAlchemy models
│   ├── routers/       # auth + tasks endpoints
│   └── schemas/       # Pydantic schemas
├── frontend/
│   └── index.html     # Single-page frontend
├── tests/
│   └── test_api.py    # pytest tests
├── main.py            # FastAPI app entry point
├── requirements.txt
├── Dockerfile
├── .env.example
└── README.md
```

---

## Setup & Run Locally

### 1. Clone & install
```bash
git clone https://github.com/your-username/taskmanager.git
cd taskmanager
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure environment
```bash
cp .env.example .env
# Edit .env and set a strong SECRET_KEY
```

### 3. Run
```bash
uvicorn main:app --reload
```
Open [http://localhost:8000](http://localhost:8000) for the frontend.  
Open [http://localhost:8000/docs](http://localhost:8000/docs) for the API docs.

---


## Running Tests
```bash
pytest tests/ -v
```

---

## Docker
```bash
docker build -t taskmanager .
docker run -p 8000:8000 -e SECRET_KEY=your-secret taskmanager
```

---

## Deploy to Render

1. Push to GitHub
2. New Web Service → connect repo
3. Build command: `pip install -r requirements.txt`
4. Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables in the Render dashboard
6. For PostgreSQL: create a Render Postgres instance and set `DATABASE_URL`

---

## API Endpoints

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/register` | ❌ | Create account |
| POST | `/login` | ❌ | Get JWT token |
| POST | `/tasks` | ✅ | Create task |
| GET | `/tasks` | ✅ | List tasks (pagination + filter) |
| GET | `/tasks/{id}` | ✅ | Get single task |
| PUT | `/tasks/{id}` | ✅ | Update task |
| DELETE | `/tasks/{id}` | ✅ | Delete task |
| GET | `/docs` | ❌ | Swagger UI |
| GET | `/health` | ❌ | Health check |
