# NALA-Assess Chatbot - Quick Start Guide

## 1️⃣ Backend Setup (5 minutes)

### Step 1: Configure Database

```bash
# Start PostgreSQL
# Windows: search for PostgreSQL and start
# macOS: brew services start postgresql
# Linux: sudo systemctl start postgresql

# Create database
psql -U postgres
CREATE DATABASE nala_assess_chatbot;
\q
```

### Step 2: Configure Environment

```bash
cd backend

# Create .env file
# Windows (PowerShell)
echo @"
DATABASE_URL=postgresql://postgres:password@localhost:5432/nala_assess_chatbot
NALA_API_KEY=your_api_key_here
NALA_BASE_URL=https://nala-api-url.com
"@ > .env

# macOS/Linux
cat > .env << 'EOF'
DATABASE_URL=postgresql://postgres:password@localhost:5432/nala_assess_chatbot
NALA_API_KEY=your_api_key_here
NALA_BASE_URL=https://nala-api-url.com
EOF
```

### Step 3: Install & Run

```bash
# Create virtual environment
python -m venv venv

# Activate
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run server
python run.py
```

**Expected Output:**
```
[INFO] Starting chatbot backend server...
[INFO] Server will be available at http://127.0.0.1:8000
[INFO] Loading embedding and reranker models...
Running on http://0.0.0.0:8000
```


## 2️⃣ Frontend Setup (3 minutes)

### In a new terminal:

```bash
cd frontend

# Create .env file
# Windows (PowerShell)
echo "VITE_API_URL=http://127.0.0.1:8000" > .env

# macOS/Linux
echo "VITE_API_URL=http://127.0.0.1:8000" > .env

# Install dependencies
npm install

# Start dev server
npm run dev
```

**Expected Output:**
```
➜  Local:   http://localhost:5173/
➜  press h to show help
```

## 3️⃣ Access the Application

Open browser and navigate to:
```
http://localhost:5173/
```


## 🧪 Test the Chatbot

### Health Check

```bash
curl http://127.0.0.1:8000/api/health
# Expected: {"status": "Chatbot backend is running"}
```

### Test Question Evaluation

```bash
curl -X POST http://127.0.0.1:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user_123",
    "question": "What is a transfer function?",
    "conversation_id": null
  }'
```


## 📁 Project Structure at a Glance

```
nala_assess_chatbot/
├── SETUP_AND_CONFIGURATION.md      ← Full setup guide
├── BACKEND_ARCHITECTURE.md          ← Backend technical details
├── FRONTEND_ARCHITECTURE.md         ← Frontend technical details
├── SYSTEM_WORKFLOW_AND_EVALUATION.md ← How evaluation works
│
├── backend/
│   ├── run.py                       ← Start here
│   ├── requirements.txt
│   ├── .env                         ← Add credentials!
│   └── app/
│       ├── routes.py                ← API endpoints
│       ├── config.py                ← Configuration
│       ├── core/
│       │   ├── orchestrator.py      ← Main logic
│       │   ├── llm_client.py        ← LLM integration
│       │   └── model_loader.py      ← ML models
│       ├── services/
│       │   ├── question_eval.py     ← Question grading
│       │   ├── answer_eval.py       ← Answer grading
│       │   └── rag_service.py       ← Document retrieval
│       └── database/
│           ├── models.py            ← Database schema
│           └── session.py           ← DB connection
│
└── frontend/
    ├── package.json
    ├── .env                         ← Add API URL!
    ├── vite.config.js
    ├── index.html
    └── src/
        ├── main.jsx                 ← Entry point
        ├── App.jsx
        ├── pages/
        │   └── ChatbotPage.jsx      ← Main UI
        ├── components/
        │   └── chatbot/
        │       ├── ChatArea.jsx
        │       ├── ChatInput.jsx
        │       └── ChatMessage.jsx
        ├── hooks/
        │   └── useChatbotConversations.js
        └── config/
            └── api.js
```


## 🎯 Key Endpoints

```
GET  /api/health                    Health check
POST /api/chat                      Send question/answer
```

---

## 🚀 Next Steps

1. **Ask a question** in the chatbot UI
2. **View the evaluation** (SOLO level, grade, feedback)
3. **Review reference materials** provided
4. **Submit an answer** to that question
5. **See the answer evaluation** with accuracy score
