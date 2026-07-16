# 🤖 Multiverse AI Agent Backend

A modern, production-ready **FastAPI backend** for a Multiverse AI Agent powered by **Google Gemini AI**.

The backend provides REST APIs, real-time streaming responses, environment-based configuration, and interactive API documentation.

---

# ✨ Features

- 🚀 FastAPI REST API
- 🤖 Google Gemini AI Integration
- ⚡ Real-time Streaming Responses (Server-Sent Events)
- 📖 Interactive Swagger & ReDoc Documentation
- 🔒 Environment-based Configuration
- 🌐 CORS Enabled
- ⚠️ Centralized Error Handling
- 📂 Modular & Scalable Architecture

---

# 🛠 Tech Stack

| Technology | Purpose |
|------------|---------|
| Python 3.11+ | Programming Language |
| FastAPI | Backend Framework |
| Google Gemini API | AI Model |
| Pydantic | Data Validation |
| Uvicorn | ASGI Server |

---

# 📂 Project Structure

```text
backend/
│
├── app/
│   ├── core/              # Configuration
│   ├── routers/           # API Routes
│   ├── schemas/           # Pydantic Models
│   ├── services/          # Gemini AI Service
│   ├── utils/             # Helper Functions
│   └── main.py            # FastAPI Entry Point
│
├── requirements.txt
├── .env.example
├── Dockerfile
└── README.md
```

---

# ⚙️ Installation

## 1️⃣ Clone Repository

```bash
git clone <repository-url>
cd backend
```

## 2️⃣ Create Virtual Environment

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

## 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

## 4️⃣ Configure Environment Variables

Create a `.env` file inside the backend folder.

```env
APP_NAME=Multiverse AI Agent Backend
APP_VERSION=0.1.0

HOST=0.0.0.0
PORT=8000

GEMINI_API_KEY=YOUR_API_KEY
GEMINI_MODEL=gemini-3-flash-preview

ENVIRONMENT=development
```

## 5️⃣ Run the Server

```bash
uvicorn app.main:app --reload
```

Server runs at:

```text
http://127.0.0.1:8000
```

---

# 📚 API Endpoints

| Method | Endpoint | Description |
|---------|----------|-------------|
| GET | `/` | Welcome Endpoint |
| GET | `/status` | Backend Status |
| POST | `/chat` | AI Chat Response |
| POST | `/chat/stream` | Stream AI Responses |

---

# 📖 API Documentation

After starting the server:

### Swagger UI

```text
http://127.0.0.1:8000/docs
```

### ReDoc

```text
http://127.0.0.1:8000/redoc
```

---

# 🧠 Current Features

- ✅ Google Gemini AI Integration
- ✅ REST Chat API
- ✅ Streaming Chat API (SSE)
- ✅ Interactive API Documentation
- ✅ Modular Architecture
- ✅ Environment Variables Support
- ✅ Error Handling
- ✅ CORS Configuration

---

# 🌟 Project Highlights

- 🚀 FastAPI-based REST API
- 🤖 Google Gemini AI Integration
- ⚡ Real-time Streaming Responses (SSE)
- 📖 Interactive Swagger & ReDoc Documentation
- 🔒 Environment Variable Configuration
- 📂 Modular Project Structure
- 🌐 CORS Enabled
- ⚠️ Robust Error Handling

---

# 📸 Sample Response

### POST `/chat`

### Request

```json
{
  "message": "Hello"
}
```

### Response

```json
{
  "response": "Hello! How can I assist you today?"
}
```

---

# 🚀 Run Locally

```bash
git clone <repository-url>

cd backend

python -m venv venv

venv\Scripts\activate

pip install -r requirements.txt

uvicorn app.main:app --reload
```

---

# 👩‍💻 Developer

**Deepali Verma**

Backend Developer

Built with ❤️ using **FastAPI** and **Google Gemini AI**.
