# NALA-Assess Chatbot

## Overview

**NALA-Assess** is an intelligent educational chatbot that evaluates student questions and answers in the **Process Control and Dynamics** course using the **SOLO (Structure of Observed Learning Outcomes) taxonomy**. It provides real-time grading, constructive feedback, and context-aware responses grounded in course materials.

**Key Features:**
- Question evaluation using SOLO taxonomy levels
- Answer scoring with accuracy feedback
- Retrieval-Augmented Generation (RAG) for course-material-grounded responses
- Persistent multi-turn conversation history

---

## Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| Frontend | React + Vite | Single-Page Application UI |
| UI Components | Material-UI | Component library |
| HTTP Client | Axios | API communication |
| Routing | React Router | Client-side navigation |
| Backend | Flask + SQLAlchemy | REST API and business logic |
| Database | PostgreSQL + pgvector | Data and vector storage |
| LLM | NALA Gemini API (gemini-2.5-flash) | Evaluation and feedback |
| Embeddings | BAAI/bge-m3 (1024-dim) | Semantic search |
| Reranker | BAAI/bge-reranker-v2-m3 | Document ranking |

---

## System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (React)                     │
│  - Vite build tool                                      │
│  - Material-UI components                               │
│  - Axios for API calls                                  │
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
│  - LLM Client: NALA Gemini API integration              │
│  - RAG Service: Retrieval-Augmented Generation          │
│  - Service Manager: Shared service lifecycle            │
├─────────────────────────────────────────────────────────┤
│ Evaluation Services                                     │
│  - QuestionEvaluationService: SOLO-based grading        │
│  - AnswerEvaluationService: Answer accuracy scoring     │
├─────────────────────────────────────────────────────────┤
│ Database Layer (SQLAlchemy ORM)                         │
│  - Models: User, Conversation, Message, Question, Answer│
└────────────────────┬────────────────────────────────────┘
                     │ SQL
                     ▼
          ┌──────────────────────┐
          │  PostgreSQL Database │
          └──────────────────────┘
```

### Backend Layer Breakdown

```
Routes Layer (Flask Blueprints)
    ↓
Orchestrator (Business Logic)
    ↓
Service Layer (Specialized Services)
    ├─ QuestionEvaluationService
    ├─ AnswerEvaluationService
    ├─ RAGService
    └─ LLMClient
    ↓
Data Layer (SQLAlchemy ORM)
    └─ PostgreSQL Database
```

---

## Setup & Configuration

### Prerequisites

- Python 3.9+
- Node.js 18.x+, npm 9.x+
- PostgreSQL 13+

### Backend Setup

**1. Create and configure the database:**
```bash
psql -U postgres
CREATE DATABASE nala_assess_chatbot;
\q
```

**2. Create `backend/.env`:**
```env
DATABASE_URL=postgresql://username:password@localhost:5432/nala_assess_chatbot
NALA_API_KEY=your_nala_api_key_here
NALA_BASE_URL=https://nala-api.example.com
```

**3. Install and run:**
```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
python run.py
```

Expected output:
```
[INFO] Starting chatbot backend server...
[INFO] Server will be available at http://127.0.0.1:8000
[INFO] Loading embedding and reranker models...
Running on http://0.0.0.0:8000
```

> **Note:** First install downloads ~150 packages including ML models and may take 10–15 minutes.

### Frontend Setup

**1. Create `frontend/.env`:**
```env
VITE_API_URL=http://127.0.0.1:8000
```

**2. Install and run:**
```bash
cd frontend
npm install
npm run dev
```

Expected output:
```
➜  Local:   http://localhost:5173/
```


### Database Initialisation

Tables are created automatically on first Flask startup. Populate initial data (topics, subtopics, document chunks, users) manually after initialisation.

| Model | Purpose |
|---|---|
| `User` | Student information |
| `Conversation` | Chat sessions per user |
| `Message` | Individual chat messages |
| `Question` | Student questions |
| `Answer` | Student answers to their questions + Accuracy scores + Feedback |
| `Topic` | Course topics |
| `Subtopic` | Subtopics with embeddings |
| `DocumentChunk` | Subtopic Document chunks for RAG retrieval |

---

## API Reference

### Endpoints

| Endpoint | Method | Purpose |
|---|---|---|
| `/api/health` | GET | Health check |
| `/api/verify-user/<user_id>` | GET | Check if user exists |
| `/api/chat` | POST | Main question/answer handler |

### Request Format
```json
{
  "user_id": "student_123",
  "conversation_id": 1,
  "question": "What is a transfer function?"
}
```

### Response Format — Question Graded
```json
{
  "response": "**I have evaluated your question based on the SOLO taxonomy!**...",
  "conversation_id": "1",
  "user_message_id": 42,
  "chatbot_message_id": 43,
  "evaluation_type": "QUESTION_GRADED",
  "question_id": 10,
  "metadata": {
    "solo_level": "Relational",
    "grade": "A",
    "reasoning": "...",
    "reference_material": "...",
    "relevant_topic_ids": [5],
    "relevant_subtopic_ids": [1, 2]
  }
}
```

### Response Format — Answer Evaluated
```json
{
  "response": "Great answer! Your response demonstrates...",
  "conversation_id": "1",
  "user_message_id": 44,
  "chatbot_message_id": 45,
  "evaluation_type": "ANSWER_EVALUATED",
  "answer_id": 15,
  "accuracy_score": 85
}
```

---

## Workflows

### Question Processing Flow

```
Input: user_question
    ↓
QuestionEvaluationService.evaluate_question()
    ├─ Send to LLM (SOLO taxonomy prompts)
    ├─ Get: solo_level, grade, reasoning, topics
    └─ Retrieve reference materials via RAG
    ↓
Decision: Is question relevant?
    ├─ YES → Create Question record
    │       ├─ Insert user message
    │       ├─ Insert question with evaluation
    │       ├─ Link topics/subtopics
    │       └─ Return QUESTION_GRADED response
    │
    └─ NO  → Return IRRELEVANT response
                (with topic suggestions)
```

**Detailed step-by-step:**

1. Frontend sends `POST /api/chat`
2. Backend validates user and finds/creates conversation
3. QuestionEvaluationService sends question to LLM with SOLO taxonomy prompts
4. LLM returns: `solo_level`, `grade`, `reasoning`, and identified `topics`
5. Topics are matched against the database to get `topic_ids` and `subtopic_ids`
6. RAG service retrieves reference materials for those subtopics
7. Question record is stored; topics/subtopics linked
8. Response returned to frontend with evaluation and reference materials

### Answer Processing Flow

```
Input: user_answer, question_id
    ↓
Retrieve Question from DB
    ├─ Get question text
    ├─ Get relevant materials
    └─ Get subtopic IDs
    ↓
AnswerEvaluationService.evaluate_answer()
    ├─ Send answer + reference to LLM
    ├─ Get: accuracy_score (0-100), feedback
    └─ Generate formatted response
    ↓
Store Answer Record
    ├─ Insert user message
    ├─ Insert answer with evaluation
    ├─ Update question status → "ANSWERED"
    └─ Return ANSWER_EVALUATED response
```

### RAG Retrieval Pipeline
A coarse-to-fine retrieval process to provide evaluation on student's question response and answer response respectively.
```
User Question
    ↓
Embedding (BGE-M3)  →  1024-dim vector
    ↓
Vector Search (pgvector)
    →  Filter by subtopic IDs
    →  Return Top-20 candidates
    ↓
Re-ranking (BGE-Reranker)
    →  Score each (question, doc) pair
    →  Sort descending
    →  Return Top-5 documents
    ↓
Format & return context
```

---

## SOLO Taxonomy Framework

SOLO (Structure of Observed Learning Outcomes) classifies the cognitive complexity of student questions across four levels:

| Level | Name | Characteristics | Grade |
|---|---|---|---|
| 1 | **Unistructural** | Single concept, basic recall | A+ |
| 2 | **Multistructural** | Multiple unrelated facts | A |
| 3 | **Relational** | Relationships between concepts | B |
| 4 | **Extended Abstract** | Application beyond course scope | C |

### LLM Configuration
Requests use XML-formatted payloads to the NALA API:

```xml
<llm_request>
    <model>gemini-2.5-flash</model>
    <system_prompt>Expert educator evaluating student questions...</system_prompt>
    <hyperparameters>
        <temperature>0.1</temperature>
        <top_p>0.2</top_p>
    </hyperparameters>
    <user_prompt>What is a transfer function?</user_prompt>
</llm_request>
```

---

## Project Structure

```
nala_assess_chatbot/
├── backend/
│   ├── run.py                       ← Entry point
│   ├── requirements.txt
│   ├── .env                         ← Add credentials
│   └── app/
│       ├── __init__.py              ← Flask app, initializes models, services, and routes
│       ├── routes.py                ← API endpoints
│       ├── config.py                ← Configuration for the .env credentials
│       ├── core/
│       │   ├── orchestrator.py      ← Main workflow logic
│       │   ├── llm_client.py        ← NALA Gemini client
│       │   ├── model_loader.py      ← BGE model loader
│       │   └── service_manager.py   ← Service lifecycle
│       ├── services/
│       │   ├── question_eval.py     ← SOLO-based question grading
│       │   ├── answer_eval.py       ← Answer accuracy scoring
│       │   └── rag_service.py       ← Vector retrieval & reranking
│       └── database/
│           ├── models.py            ← SQLAlchemy models
│           └── session.py           ← DB session management
│
└── frontend/
    ├── package.json
    ├── .env                         ← Add API URL
    ├── vite.config.js
└── src/
    ├── main.jsx                  # React entry point
    ├── App.jsx                   # Root component
    ├── App.css                   # Global styles
    ├── index.css                 # Global CSS
    │
    ├── components/
    │   ├── Navbar.jsx            # Top navigation
    │   └── chatbot/
    │       ├── index.js          # Chatbot exports
    │       ├── ChatArea.jsx       # Message display area
    │       ├── ChatInput.jsx      # User input box
    │       ├── ChatMessage.jsx    # Individual message component
    │       ├── ChatHeader.jsx     # Chat header/title
    │       ├── ChatbotSidebar.jsx # Conversation sidebar
    │       ├── TypingIndicator.jsx# Loading animation
    │       ├── HeroSection.jsx    # Welcome section
    │       ├── SectionHeader.jsx  # Section titles
    │       ├── CTASection.jsx     # Call-to-action
    │       ├── SoloTaxonomySection.jsx  # Info section
    │       └── AssessmentFlowSection.jsx# Process flow
    │
    ├── pages/
    │   ├── ChatbotPage.jsx       # Main chatbot page
    │   └── ChatbotAssessPage.jsx # Assessment page variant
    │
    ├── hooks/
    │   └── useChatbotConversations.js # Conversation state
    │
    ├── config/
    │   └── api.js                # API endpoint definitions
    │
    ├── data/
    │   └── defaultMessages.js    # Initial messages
    │
    ├── styles/
    │   └── useStyles.js          # Material-UI theme & styles
    │
    └── assets/                   # Images, icons
```