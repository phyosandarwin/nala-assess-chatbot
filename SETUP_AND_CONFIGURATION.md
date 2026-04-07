# NALA-Assess Chatbot - Setup & Configuration Guide


## System Overview

**NALA-Assess Chatbot** is an intelligent educational chatbot designed to evaluate student questions and answers in the **Process Control and Dynamics** course using the **SOLO (Structure of Observed Learning Outcomes) taxonomy**.

### Key Features

- **Question Evaluation**: Assesses student questions using SOLO taxonomy levels (Unistructural, Multistructural, Relational, Extended Abstract)
- **Answer Evaluation**: Grades student answers with accuracy scoring and feedback
- **Context-Aware Responses**: Uses Retrieval-Augmented Generation (RAG) to retrieve relevant course materials
- **Multi-turn Conversations**: Supports persistent conversation history with user sessions
- **Flask REST API**: Backend API for all chatbot operations
- **React Frontend**: Modern, responsive UI with Material-UI components



## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (React)                     │
│  - Vite build tool                                      │
│  - Material-UI components                               │
│  - Axios for API calls                                  │
│  - React Router for navigation                          │
└────────────────────┬────────────────────────────────────┘
                     │ HTTP/REST
                     ▼
┌─────────────────────────────────────────────────────────┐
│           Backend (Flask) - Port 8000                   │
├─────────────────────────────────────────────────────────┤
│ Routes Layer                                            │
│  - /api/chat (POST) - Main chat endpoint                │
│  - /api/verify-user (GET) - User verification           │
│  - /api/health (GET) - Health check                     │
├─────────────────────────────────────────────────────────┤
│ Core Services Layer                                     │
│  - Orchestrator: Manages Q&A workflow                   │
│  - LLM Client: NALA Gemini API integration             │
│  - RAG Service: Retrieval-Augmented Generation          │
│  - Service Manager: Shared service lifecycle            │
├─────────────────────────────────────────────────────────┤
│ Evaluation Services                                     │
│  - QuestionEvaluationService: SOLO-based grading       │
│  - AnswerEvaluationService: Answer accuracy scoring    │
├─────────────────────────────────────────────────────────┤
│ Database Layer (SQLAlchemy ORM)                         │
│  - Models: User, Conversation, Message, Question, Answer│
│  - Session Management                                   │
└────────────────────┬────────────────────────────────────┘
                     │ SQL
                     ▼
          ┌──────────────────────┐
          │  PostgreSQL Database │
          └──────────────────────┘
```

### Data Flow

```
User Input (Question/Answer)
    │
    ▼
Frontend (React) - sends HTTP POST to /api/chat
    │
    ▼
Backend Routes - receives request, validates user & conversation
    │
    ▼
Orchestrator
    ├─ New Question? → QuestionEvaluationService
    │   ├─ Evaluate with LLM (SOLO taxonomy)
    │   ├─ Retrieve reference materials (RAG)
    │   └─ Store in Database (Question record)
    │
    └─ Pending Answer? → AnswerEvaluationService
        ├─ Evaluate with LLM (accuracy scoring)
        ├─ Compare against reference materials
        └─ Store in Database (Answer record)
    │
    ▼
Response sent back to Frontend
    │
    ▼
Frontend displays response to user
```


## Prerequisites

### System Requirements

- **Python**: 3.9 or higher
- **Node.js**: 18.x or higher
- **npm**: 9.x or higher
- **PostgreSQL**: 13 or higher

### Required Services

- PostgreSQL database (local or remote)
- NALA API connection (for LLM access)


## Environment Configuration

### Backend Environment Variables

Create a `.env` file in the `backend/` directory with the following variables:

```env
# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/nala_assess_chatbot

# NALA API Configuration
NALA_API_KEY=your_nala_api_key_here
NALA_BASE_URL=https://nala-api.example.com
```

### Frontend Environment Variables

Create a `.env` file in the `frontend/` directory:

```env
# API Configuration
VITE_API_URL=http://127.0.0.1:8000
```

## Backend Setup

### Step 1: Create Python Virtual Environment

```bash
cd backend

# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 2: Install Python Dependencies

```bash
pip install -r requirements.txt
```

**Installation Notes:**
- This installs ~150 packages including Flask, SQLAlchemy, LangChain, and ML models
- First installation may take 10-15 minutes
- If you encounter model download issues, see [Troubleshooting](#troubleshooting)

### Step 3: Configure Environment Variables

1. Create `.env` file in the `backend/` directory (see [Environment Configuration](#environment-configuration))
2. Add your database URL and NALA API credentials

### Step 4: Verify Backend Configuration

```bash
python -c "from app.config import Config; print(f'Database: {Config.DATABASE_URL}'); print(f'NALA API: {Config.NALA_BASE_URL}')"
```

Expected output:
```
Database: postgresql://...
NALA API: https://...
```

### Step 5: Key Backend Files

| File | Purpose |
|------|---------|
| `run.py` | Entry point - Flask app startup |
| `app/__init__.py` | Flask app factory and initialization |
| `app/config.py` | Configuration and environment variables |
| `app/routes.py` | API endpoints definition |
| `app/core/orchestrator.py` | Main workflow orchestration |
| `app/core/llm_client.py` | LLM API client (NALA Gemini) |
| `app/core/model_loader.py` | ML model loading (embeddings, reranker) |
| `app/services/question_eval.py` | Question evaluation logic |
| `app/services/answer_eval.py` | Answer evaluation logic |
| `app/services/rag_service.py` | RAG retrieval and ranking |
| `app/database/models.py` | SQLAlchemy database models |
| `app/database/session.py` | Database session management |

---

## Frontend Setup

### Step 1: Install Node Dependencies

```bash
cd frontend
npm install
```

### Step 2: Configure Environment Variables

Create `.env` in `frontend/` directory:

```env
VITE_API_URL=http://127.0.0.1:8000
```

### Step 3: Verify Installation

```bash
npm -v
node -v
```

### Step 4: Key Frontend Files & Components

| Path | Purpose |
|------|---------|
| `src/main.jsx` | React app entry point |
| `src/App.jsx` | Root component |
| `src/pages/ChatbotPage.jsx` | Main chatbot interface |
| `src/pages/ChatbotAssessPage.jsx` | Assessment-specific page |
| `src/components/chatbot/ChatArea.jsx` | Message display area |
| `src/components/chatbot/ChatInput.jsx` | User input component |
| `src/config/api.js` | API configuration and endpoints |
| `src/hooks/api_fetch.js` | API fetch utilities |
| `vite.config.js` | Vite build configuration |

---

## Running the Application

#### Terminal 1 - Backend

```bash
cd backend

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Run Flask server
python run.py
```

Expected output:
```
[INFO] Starting chatbot backend server...
[INFO] Server will be available at http://127.0.0.1:8000
[INFO] Loading embedding and reranker models...
[INFO] Models loaded successfully.
Running on http://0.0.0.0:8000
```

#### Terminal 2 - Frontend

```bash
cd frontend

# Start development server with Vite
npm run dev
```

Expected output:
```
  VITE v8.0.0  ready in 300 ms

  ➜  Local:   http://localhost:5173/
  ➜  press h to show help
```

**Access the application:**
- Frontend: http://localhost:5173/
- Backend API: http://127.0.0.1:8000

## Database Setup

### Step 1: Create PostgreSQL Database

### Step 2: Initialize Database Tables

The database tables are created automatically when the Flask app starts. If you need to recreate them, use `app.database.models` file for reference.

| Model | Purpose |
|-------|---------|
| `User` | Stores student information |
| `Conversation` | Chat session per user |
| `Message` | Individual chat messages (user or bot) |
| `Question` | Evaluated student questions |
| `Answer` | Student answers to questions |
| `Topic` | Course topics (e.g., "Transfer Functions") |
| `Subtopic` | Topic subdivisions with embeddings |
| `DocumentChunk` | Course material chunks for retrieval |

### Step 3: Populate Initial Data

Insert data such as topics, subtopics, document chunks and users (if you already have the pseudomised user data)

---

## API Endpoints

### Health Check

```
GET /api/health
```

Response:
```json
{
  "status": "Chatbot backend is running"
}
```

### Chat Endpoint

**Endpoint:**
```
POST /api/chat
```

**Request Body:**
```json
{
  "question": "What is a transfer function?",
  "user_id": "user_123",
  "conversation_id": 1
}
```

**Response (New Question):**
```json
{
  "response": "**I have evaluated your question based on the SOLO taxonomy!**...",
  "conversation_id": "1",
  "user_message_id": 42,
  "chatbot_message_id": 43,
  "question_id": 10,
  "evaluation_type": "QUESTION_GRADED",
  "metadata": {
    "solo_level": "Relational",
    "grade": "A",
    "reasoning": "...",
    "reference_material": "...",
    "relevant_subtopic_ids": [1, 2],
    "relevant_topic_ids": [5]
  }
}
```

**Response (Answering a Question):**
```json
{
  "response": "Great answer! Your response demonstrates...",
  "conversation_id": "1",
  "user_message_id": 44,
  "chatbot_message_id": 45,
  "answer_id": 15,
  "accuracy_score": 85,
  "evaluation_type": "ANSWER_EVALUATED"
}
```

## Workflow

### Question Processing Flow

1. **User submits a question** → Frontend sends to `/api/chat`
2. **Backend validates user** → Checks if user exists in database
3. **Create conversation** → If no conversation, creates new one
4. **Check for pending questions** → If none, process as new question
5. **Question Evaluation Service**:
   - Sends question to NALA LLM with SOLO taxonomy prompts
   - Receives: taxonomy level, grade, reasoning
   - Retrieves relevant course materials via RAG
6. **Store in database**:
   - Creates Message (user question)
   - Creates Question record with evaluation results
   - Links to relevant Topics/Subtopics
   - Creates Message (bot response)
7. **Return response** → Frontend displays evaluation and next steps

### Answer Processing Flow

1. **User submits an answer** → Frontend sends to `/api/chat` (with same question_id)
2. **Backend detects pending question** → Routes to answer processing
3. **Answer Evaluation Service**:
   - Retrieves question text and relevant materials
   - Sends to LLM for evaluation
   - Receives: accuracy_score, feedback
4. **Store in database**:
   - Creates Message (user answer)
   - Creates Answer record with evaluation
   - Updates Question status to "ANSWERED"
5. **Return response** → Frontend displays feedback and score


## Configuration Details

### LLM Integration (NALA Gemini)

The system uses NALA's Gemini API for evaluations:

```python
# Backend uses XML-formatted requests
class NalaGemini(LLM):
    api_key: str = Config.NALA_API_KEY
    base_url: str = Config.NALA_BASE_URL
    model_name: str = "gemini-2.5-flash"
```

**Temperature & Parameters:**
- Temperature: 0.1 (Low - for consistent grading)
- Top-p: 0.2 (Low - focused responses)

### Embedding Models

The system uses BGE (BAAI General Embedding) models:

```python
EMBEDDING_MODEL_LOCAL = '/models/bge-m3'           # Docker
EMBEDDING_MODEL_HF = 'BAAI/bge-m3'                 # HuggingFace

RERANKER_MODEL_LOCAL = '/models/bge-reranker-v2-m3'
RERANKER_MODEL_HF = 'BAAI/bge-reranker-v2-m3'
```

**Automatic Model Selection:**
- Docker environment → Uses local model paths
- Local development → Auto-downloads from HuggingFace