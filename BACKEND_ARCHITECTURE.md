# NALA-Assess Chatbot - Backend Architecture & Components

## Overview

The backend is built with **Flask** and uses a layered architecture with clear separation of concerns:

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

## Architecture Layers

### 1. Routes Layer

**File:** `app/routes.py`

Defines Flask API endpoints and handles HTTP requests/responses.

#### Key Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/health` | GET | Health check - verifies backend is running |
| `/api/verify-user/<user_id>` | GET | Checks if user exists in database |
| `/api/chat` | POST | Main chat endpoint for questions and answers |

#### Request Handling Flow

```python
@main_bp.route('/api/chat', methods=['POST'])
def chat():
    """
    Main chat handler supporting two modes:
    
    1. NEW QUESTION MODE
       - Creates new conversation if needed
       - Checks for pending answers (returns None)
       - Calls orchestrator.process_question()
       - Returns question evaluation results
    
    2. ANSWER MODE
       - Finds existing conversation
       - Checks for pending answers (returns pending question)
       - Calls orchestrator.process_answer()
       - Returns answer evaluation results
    """
```

#### Request Validation

1. **User Validation**: Verify user_id exists in database
2. **Conversation Validation**: Verify conversation belongs to user
3. **Data Validation**: Ensure required fields present

#### Response Format

All responses return JSON with consistent structure:
```json
{
  "response": "string - displayed message",
  "conversation_id": "integer",
  "user_message_id": "integer",
  "chatbot_message_id": "integer",
  "evaluation_type": "QUESTION_GRADED | IRRELEVANT | ANSWER_EVALUATED",
  // Additional fields depend on evaluation_type
}
```

---

### 2. Core Services Layer

#### 2.1 Orchestrator

**File:** `app/core/orchestrator.py`

Orchestrates the complete workflow for question and answer processing.

**Responsibilities:**
- Coordinate between services
- Manage database transactions
- Implement workflow logic
- Handle errors and logging

**Question Evaluation Flow Diagram:**

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

**Answer Evaluation Flow Diagram:**

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

#### 2.2 LLM Client (NALA Gemini)

**File:** `app/core/llm_client.py`

Custom LLM wrapper implementing LangChain's LLM interface.

**Request Format:**
- Uses XML-based request format to NALA API
- Implements connection pooling for efficiency
- Automatic retry with backoff

**Response Processing:**
```xml
<!-- REQUEST -->
<llm_request>
    <model>gemini-2.5-flash</model>
    <system_prompt>Expert educator evaluating student questions...</system_prompt>
    <hyperparameters>
        <temperature>0.1</temperature>
        <top_p>0.2</top_p>
    </hyperparameters>
    <user_prompt>What is a transfer function?</user_prompt>
</llm_request>

<!-- RESPONSE -->
LLM output in JSON format
```

#### 2.3 Service Manager

**File:** `app/core/service_manager.py`

Singleton pattern implementation for managing shared service instances.

**Responsibilities:**
- Initialize services once on app startup
- Provide services to orchestrator instances
- Manage service lifecycle

#### 2.4 Model Loader

**File:** `app/core/model_loader.py`

Loads and caches ML models (embeddings, reranker) using singleton pattern.

**Models Loaded:**
- `BAAI/bge-m3` (text embedding model)
- `BAAI/bge-reranker-v2-m3` (re-ranker model)

### 3. Evaluation Services

#### 3.1 Question Evaluation Service

**File:** `app/services/question_eval.py`

Evaluates student questions using SOLO taxonomy framework.

**SOLO Taxonomy Levels:**

| Level | Name | Description |
|-------|------|-------------|
| 1 | **Unistructural** | Single idea, basic facts |
| 2 | **Multistructural** | Multiple unrelated facts |
| 3 | **Relational** | Relationships between concepts |
| 4 | **Extended Abstract** | Application beyond course scope |

**Evaluation Output:**
```json
{
    "type": "QUESTION_GRADED" or "IRRELEVANT",
    "solo_level": "Unistructural|Multistructural|Relational|Extended Abstract",
    "grade": "A|B|C|D|F",
    "reasoning": "Detailed explanation of why...",
    "reference_material": "Relevant course material excerpts",
    "relevant_topic_ids": [1, 2, 3],
    "relevant_subtopic_ids": [10, 11, 12],
    "topics_list": "Formatted list of available topics"
}
```

**Evaluation Logic:**
1. Send question to LLM with SOLO prompts
2. Parse response (SOLO level, grade, reasoning)
3. Extract mentioned topics/subtopics from response
4. Validate topics against database
5. If valid topics found → retrieve reference materials
6. Return evaluation package

#### 3.2 Answer Evaluation Service

**File:** `app/services/answer_eval.py`

Evaluates answer accuracy against reference materials and original question.

**Evaluation Output:**
```json
{
    "accuracy_score": 75,  // 0-100
    "feedback": "Good understanding of transfer functions, but...",
    "is_correct": true,
    "reasoning": "Student correctly identified..."
}
```

**Evaluation Logic:**
1. Retrieve question text and reference materials
2. Send (question, answer, reference) to LLM
3. LLM scores accuracy on scale 0-100
4. Generate constructive feedback
5. Identify strengths and areas for improvement
6. Return evaluation package

---

### 4. RAG (Retrieval-Augmented Generation) Service

**File:** `app/services/rag_service.py`

Core retrieval system for finding relevant course materials.

**Architecture:**
```
User Question
    ↓
Embedding (BGE-M3)
    ↓
Vector Search (Similarity)
    ↓
Top-K Candidates
    ↓
Re-ranking (BGE-Reranker)
    ↓
Top-5 Refined Results
    ↓
Format & Return
```

**Process:**

1. **Query Embedding:** Convert question to vector (1024-dim)
2. **Similarity Search:** Find top-K similar documents in pgvector index
3. **Re-ranking:** Use reranker to refine top results
4. **Context Assembly:** Combine relevant chunks with metadata
5. **Response Format:** Return formatted materials with source info

**Database Queries:**

```python
# Step 1: Vector similarity search
similar_docs = db.query(DocumentChunk).order_by(
    DocumentChunk.embedding.l2_distance(query_vector)
).limit(top_k).all()

# Step 2: Re-ranking with BGE
scores = reranker.compute_score(
    [question],
    [doc.content for doc in similar_docs]
)

# Step 3: Sort by score and return top-5
top_5 = sorted(zip(similar_docs, scores), 
               key=lambda x: x[1], reverse=True)[:5]
```

**Benefits:**
- Provides factual grounding
- Prevents hallucinations
- Ensures answers align with course content
- Improves evaluation consistency


## Request/Response Cycle

### Complete Flow: Question Processing

```
1. USER INTERACTION
   Frontend: POST /api/chat
   {
     "user_id": "user_123",
     "question": "What is a transfer function?",
     "conversation_id": 1
   }

2. ROUTE HANDLER (routes.py)
   ✓ Validate JSON
   ✓ Extract fields
   ✓ Verify user exists
   ✓ Find/create conversation

3. ORCHESTRATOR (orchestrator.py)
   → process_question()
   ├─ Create user message in DB
   └─ Call question_eval_service

4. QUESTION EVAL SERVICE (question_eval.py)
   ├─ Create prompt with SOLO taxonomy
   ├─ Call LLM client
   ├─ Parse response
   ├─ Extract topics
   ├─ Call RAG service
   └─ Return evaluation package

5. RAG SERVICE (rag_service.py)
   ├─ Embed question
   ├─ Vector search in DB
   ├─ Re-rank results
   └─ Return top-5 materials

6. ORCHESTRATOR (continued)
   ├─ Create Question record in DB
   ├─ Link Topics/Subtopics
   ├─ Create bot response message
   └─ Format JSON response

7. RESPONSE
   Frontend receives:
   {
     "response": "I have evaluated your question...",
     "evaluation_type": "QUESTION_GRADED",
     "question_id": 42,
     "metadata": {...}
   }

8. FRONTEND DISPLAY
   ✓ Show evaluation results
   ✓ Show reference materials
   ✓ Prompt for answer
```