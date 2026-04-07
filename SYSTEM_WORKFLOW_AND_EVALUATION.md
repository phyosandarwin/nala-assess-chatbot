# NALA-Assess Chatbot - System Workflow & Evaluation Process


## System Overview

### What is NALA-Assess?

NALA-Assess is an **intelligent tutoring system** that uses AI to:
1. **Evaluate** student questions using the SOLO taxonomy framework
2. **Grade** questions based on cognitive complexity levels
3. **Evaluate** student answers against reference materials
4. **Provide feedback** to improve learning outcomes

### Core Technologies

| Component | Technology | Purpose |
|-----------|-----------|---------|
| LLM Client | NALA Gemini API | Evaluation and feedback generation |
| Embeddings | BAAI/bge-m3 (1024-dim) | Semantic search for materials |
| Reranker | BAAI/bge-reranker-v2-m3 | Ranking retrieved documents |
| Database | PostgreSQL + pgvector | Store conversations and vectors |
| Frontend | React + Vite | User interface |
| Backend | Flask + SQLAlchemy | REST API and business logic |

---

## Question Evaluation Workflow

### Phase 1: User Input

**Processing:**
1. Frontend sends HTTP POST to `/api/chat`
2. Backend receives and validates request
3. Creates user and conversation if needed
4. Inserts user message into database

### Phase 2: LLM-Based SOLO Evaluation

**Processing by LLM:**

```
1. Extract question intent
   ↓
2. Classify complexity level
   - Unistructural? → Basic definition question
   - Multistructural? → Multiple concepts, no relationships
   - Relational? → Relationships/comparisons between concepts
   - Extended Abstract? → Application/synthesis beyond course
   ↓
3. Assess quality/perspective
   ↓
4. Assign SOLO level and grade
   ↓
5. Identify relevant topics from question
   ↓
6. Return structured evaluation
```

### Phase 3: Topic Extraction & Matching

**LLM Output Parsing:**
```json
{
  "solo_level": "Relational",
  "grade": "A",
  "reasoning": "The question demonstrates...",
  "topics": ["Transfer Functions", "Poles and Zeros"]
}
```

**Database Lookup:**
```sql
SELECT id, subtopic_summary, subtopic_summary_embedding
FROM subtopics
JOIN topics ON subtopics.topic_id = topics.id
WHERE topics.topic_name IN ('Transfer Functions', 'Poles and Zeros')
```

**Result:**
```python
relevant_subtopic_ids = [1, 2, 5]  # IDs from database
relevant_topic_ids = [10, 11]
```

### Phase 4: Retrieval-Augmented Generation (RAG)

**Input:**
- Original question
- Relevant subtopic IDs

**Coarse-to-fine retrieval/ RAG Process:**

```
Step 1: Embed Question
┌─────────────────────────────────┐
│ Question Embedding (BGE-M3)     │
│ Input:  Question text           │
│ Output: 1024-dim vector         │
└─────────────────────────────────┘
         ↓
Step 2: Vector Search (pgvector)
┌─────────────────────────────────┐
│ PostgreSQL Vector Search        │
│ Filter: subtopic ids            │
│ Return: Top-20 document chunks  │
└─────────────────────────────────┘
         ↓
Step 3: Re-ranking (BGE-Reranker)
┌─────────────────────────────────┐
│ Re-rank Top-20                  │
│ Score(question, doc) → score    │
│ Sort by score (descending)      │
│ Return: Top-5 documents         │
└─────────────────────────────────┘
         ↓
Step 4: Format Context
┌─────────────────────────────────┐
│ E.g. Top-5 Document Chunks:     │
│ 1. "Poles are locations in..."  │
│ 2. "Zeros are values that..."   │
│ 3. "The difference affects..."  │
│ ... (formatted with metadata)   │
└─────────────────────────────────┘
```

### Phase 5: Question Classification

**Rule-based Check:**
```python
# Check if question is technical and relevant
if evaluation["solo_level"] in ["Unistructural", "Multistructural", "Relational", "Extended Abstract"]:
    evaluation_type = "QUESTION_GRADED"
else:
    evaluation_type = "IRRELEVANT"
```

### Phase 6: Response Generation

**For IRRELEVANT Questions:**
```
Response: "Sorry, NALA-Assess is only designed to tackle technical course questions 
under Process Control and Dynamics. Please check with Dr Mukta Bansal for other matters.

💡 Available topics:
- Introduction to Process Control
- Laplace Transforms
- ... (other topics)

Feel free to ask technical content-related questions!"
```

**For GRADED Questions:**
```
Response: "**I have evaluated your question based on the SOLO taxonomy!**

🎯 **SOLO Taxonomy Level:** Relational
📊 **Grade:** A
💬 **Feedback:** Your question demonstrates relational-level thinking by asking for 
a comparison between two important concepts in control systems.

📚 **Relevant Reference Material:**
You may refer to [subtopic(s)] from [topic name(s)]
------------------------------------------------------------------------------
📝 **Next Step:** Try answering the question using the reference materials!"
```

### Phase 7: Data Insertion

**Database Inserts:**
```python
# 1. Insert user message
user_message = Message(
    conversation_id=conv_id,
    sender="user",
    content="Explain the difference..."
)
db.add(user_message)
db.flush()

# 2. Create question record
question = Question(
    message_id=user_message.id,
    solo_taxonomy_level="Relational",
    grade="A",
    reasoning="...",
    status="AWAITING_ANSWER"
)
db.add(question)
db.flush()

# 3. Link topics (many-to-many)
for topic_id in [10, 11]:
    topic = db.query(Topic).get(topic_id)
    question.topics.append(topic)

# 4. Link subtopics (many-to-many)
for subtopic_id in [1, 2, 5]:
    subtopic = db.query(Subtopic).get(subtopic_id)
    question.subtopics.append(subtopic)

# 5. Insert bot response message
bot_message = Message(
    conversation_id=conv_id,
    sender="bot",
    content="**I have evaluated...**"
)
db.add(bot_message)
db.commit()
```

### Phase 8: Response to Frontend

```json
{
  "response": "**I have evaluated your question...** [full response]",
  "conversation_id": "1",
  "user_message_id": 42,
  "chatbot_message_id": 43,
  "question_id": 10,
  "evaluation_type": "QUESTION_GRADED",
  "metadata": {
    "solo_level": "Relational",
    "grade": "A",
    "reasoning": "Your question demonstrates...",
    "reference_material": "[Formatted chunks]",
    "relevant_topic_ids": [10, 11],
    "relevant_subtopic_ids": [1, 2, 5]
  }
}
```

---

## Answer Evaluation Workflow

### Phase 1: Answer Reception

**Input:**
```
Student Has Pending Question: ID=10
Student Answer: "Poles determine the transient response while zeros affect the gain..."
```

**Detection:**
```python
# Check for pending questions
pending_q = db.query(Question).filter(
    Question.id == question_id,
    Question.status == "AWAITING_ANSWER"
).first()

if pending_q:
    # Route to answer processing
    await orchestrator.process_answer(...)
```

### Phase 2: Context Retrieval

**Step 1: Get Original Question**
```sql
SELECT q.*, m.content as question_text
FROM questions q
JOIN messages m ON q.message_id = m.id
WHERE q.id = 10;
```

**Step 2: Get Relevant Materials**
```sql
SELECT dc.content
FROM document_chunks dc
WHERE dc.subtopic_id IN (
    SELECT subtopic_id FROM question_subtopics
    WHERE question_id = 10
)
LIMIT 5;
```

**Result:**
```python
{
    "question": "Explain the difference between poles and zeros...",
    "reference_materials": [
        "Poles are locations where...",
        "Zeros determine the...",
        ...
    ]
}
```

### Phase 3: LLM-based Evaluation

**Prompt Design:**

```
You are an expert educator grading a student's answer.

Original Question: "Explain the difference between poles and zeros in a transfer function."

Reference Materials from Course:
1. "Poles are locations in the s-plane where the denominator equals zero. 
    They determine the transient response and stability."
2. "Zeros are locations where the numerator equals zero. They affect the 
    overall gain and response characteristics."
3. "The key difference: poles affect how fast the system responds, 
    while zeros affect the amplitude of specific frequency responses."

Student Answer: "Poles determine the transient response while zeros affect the gain..."

Evaluate this answer and respond with JSON:
{
  "accuracy_score": 85,
  "is_correct": true,
  "feedback": "Your answer correctly identifies the primary roles of poles and zeros...",
  "reasoning": "The student demonstrates understanding by...",
  "strengths": ["Correct identification of poles' role", "Mentions frequency response"],
  "improvements": ["Could elaborate more on stability implications"]
}
```

**LLM Decision Process:**

```
1. Parse student answer
   ↓
2. Compare with reference materials
   - Does it match key concepts?
   - Are definitions accurate?
   - Is reasoning sound?
   ↓
3. Assign accuracy score (0-100)
   - 90-100: Excellent, comprehensive understanding
   - 80-89: Good, mostly correct with minor gaps
   - 70-79: Satisfactory, core concepts present
   - 60-69: Acceptable, significant gaps
   - <60: Needs improvement
   ↓
4. Generate constructive feedback
   - Identify strengths
   - Suggest improvements
   - Provide additional context if needed
   ↓
5. Return evaluation
```

### Phase 4: Data Insertion

```python
# 1. Insert user message (answer)
user_msg = Message(
    conversation_id=conv_id,
    sender="user",
    content="Poles determine the transient response..."
)
db.add(user_msg)
db.flush()

# 2. Create answer record
answer = Answer(
    message_id=user_msg.id,
    question_id=10,
    accuracy_score=85,
    feedback="Your answer correctly identifies..."
)
db.add(answer)

# 3. Update question status
question = db.query(Question).get(10)
question.status = "ANSWERED"
question.updated_at = datetime.now()

# 4. Insert bot response
bot_msg = Message(
    conversation_id=conv_id,
    sender="bot",
    content="Great answer! Your response demonstrates..."
)
db.add(bot_msg)
db.commit()
```

### Phase 5: Response to Frontend

```json
{
  "response": "Great answer! Your response demonstrates good understanding of poles and zeros...",
  "conversation_id": "1",
  "user_message_id": 44,
  "chatbot_message_id": 45,
  "answer_id": 15,
  "accuracy_score": 85,
  "evaluation_type": "ANSWER_EVALUATED"
}
```

---

## SOLO Taxonomy Framework

### Understanding SOLO Levels

**SOLO = Structure of Observed Learning Outcomes**

#### Level 1: UNISTRUCTURAL
**Characteristic:** Single idea/concept

**Example Questions:**
- "What is a transfer function?"
- "Define pole and zero"
- "What does BODE stand for?"

**Evaluation:**
```
- Tests basic recall
- No comparison/analysis
- Simple definition expected
- Grade: Usually B-C (acceptable but basic)
```

**Sample Response:**
```
"Your question tests basic recall of a single concept. 
While important, consider asking how concepts relate or 
apply in practice to demonstrate deeper understanding."
```

---

#### Level 2: MULTISTRUCTURAL
**Characteristic:** Multiple unrelated ideas

**Example Questions:**
- "What are poles and zeros?"
- "List the properties of first-order systems"
- "Describe amplitude response and phase response"

**Evaluation:**
```
- Covers multiple topics
- No apparent relationships
- Collection of facts
- Grade: Usually C-B (solid but not integrated)
```

**Sample Response:**
```
"Your question addresses multiple important concepts. 
To advance, try connecting these concepts—how do 
poles affect the response types?"
```

---

#### Level 3: RELATIONAL
**Characteristic:** Relationships between concepts

**Example Questions:**
- "How do poles affect system stability?"
- "Why do zeros change the response amplitude?"
- "Compare first-order vs second-order systems"
- "Explain the difference between poles and zeros"

**Evaluation:**
```
- Shows integrating of ideas
- Demonstrates understanding
- Asks for comparisons/relationships
- Grade: Usually A-B (good understanding)
```

**Sample Response:**
```
"Excellent! Your question demonstrates relational thinking 
by asking how one concept (poles) affects another (stability). 
This shows integrated understanding at a higher level."
```

---

#### Level 4: EXTENDED ABSTRACT
**Characteristic:** Application beyond course scope

**Example Questions:**
- "How could pole-placement improve robustness in real systems?"
- "Compare different controller design methods and their trade-offs"
- "What are the limitations of linear transfer function models?"
- "How would you design a system to minimize overshoot?"

**Evaluation:**
```
- Asks for synthesis/evaluation
- Applies to novel situations
- Requires generalization
- Grade: Usually A (exceptional thinking)
```

**Sample Response:**
```
"Outstanding! Your question demonstrates extended abstract 
thinking by applying course concepts to novel design problems. 
This shows the deepest level of understanding."
```

---

### Grading Scale

```
Grade | Description | Interpretation
------|-------------|----------------
A     | Excellent   | Question shows sophisticated understanding relevant to SOLO level
B     | Good        | Question is well-formed and relevant
C     | Satisfactory | Question is relevant but could be more focused
D     | Fair        | Question is somewhat vague or incomplete
F     | Poor        | Question is off-topic or nonsensical
```

---

## Complete User Journey

### Scenario: Student Learning Session

```
TIME 1: Student starts chatbot
┌────────────────────────────────────┐
│ 🤖 "Welcome! Ask me about Process  │
│ Control and Dynamics."             │
│                                    │
│ I'll evaluate your understanding   │
│ using the SOLO taxonomy.           │
└────────────────────────────────────┘

↓

TIME 2: Student asks first question
┌────────────────────────────────────┐
│ 👤 "What is a transfer function?"  │
└────────────────────────────────────┘

BACKEND PROCESSING:
- Evaluate: Solo_level = Unistructural
- Classify: This is basic recall
- Grade: B (acceptable but basic)
- Retrieve materials on TF basics

↓

TIME 3: Bot provides feedback
┌────────────────────────────────────┐
│ 🤖 I evaluated your question:      │
│                                    │
│ 🎯 Level: Unistructural           │
│ 📊 Grade: B                        │
│                                    │
│ Your question tests basic recall.  │
│ While important, try asking how    │
│ concepts relate.                   │
│                                    │
│ 📚 Reference Materials:            │
│ - Transfer functions relate...     │
│ - They are used when...            │
│                                    │
│ 📝 Next: Try answering this!       │
└────────────────────────────────────┘

↓ (Student reads materials)

TIME 4: Student attempts answer
┌────────────────────────────────────┐
│ 👤 "A transfer function is the ratio│
│  of output to input under zero     │
│  initial conditions."              │
└────────────────────────────────────┘

BACKEND PROCESSING:
- Compare with reference materials
- Check: Definition accuracy ✓
- Check: Appropriate level ✓
- Accuracy Score: 92/100

↓

TIME 5: Bot evaluates answer
┌────────────────────────────────────┐
│ 🤖 Great answer!                   │
│                                    │
│ 📊 Accuracy: 92/100                │
│                                    │
│ ✅ You correctly identified the key│
│ definition and the conditions.     │
│                                    │
│ 💡 Consider: Transfer functions    │
│ can be derived from differential   │
│ equations or system responses.     │
│                                    │
│ Ready for a new question?          │
└────────────────────────────────────┘

↓ (Student asks more complex question)

TIME 6: Student asks advanced question
┌────────────────────────────────────┐
│ 👤 "How do poles affect the        │
│  frequency response of a system?"  │
└────────────────────────────────────┘

BACKEND PROCESSING:
- Evaluate: Solo_level = Relational
- Classify: Asking for relationships
- Grade: A (good understanding)
- Retrieve materials on poles & response

↓

TIME 7: Bot provides advanced feedback
┌────────────────────────────────────┐
│ 🤖 Excellent question!             │
│                                    │
│ 🎯 Level: Relational              │
│ 📊 Grade: A                        │
│                                    │
│ Your question shows relational     │
│ thinking by asking how one concept │
│ (poles) affects another (response).│
│                                    │
│ 📚 Reference Materials:            │
│ - Poles determine transient...     │
│ - Real poles cause exponential...  │
│ - Complex poles cause oscillation..│
│                                    │
│ 📝 Next: Try answering this!       │
└────────────────────────────────────┘

[Learning continues...]
```

### Database Records Created

```
Session Data:
│
├─ Conversation
│  ├─ title: "Poles and Transfer Functions"
│  ├─ user_id: "student_123"
│  └─ last_accessed: 2024-04-07 14:30:00
│
├─ Message 1 (user)
│  ├─ content: "What is a transfer function?"
│  ├─ sender: "user"
│  └─ timestamp: 2024-04-07 14:30:05
│
├─ Message 2 (bot)
│  ├─ content: "I evaluated your question..."
│  ├─ sender: "bot"
│  └─ timestamp: 2024-04-07 14:30:08
│
├─ Question 1
│  ├─ message_id: 1
│  ├─ solo_level: "Unistructural"
│  ├─ grade: "B"
│  ├─ status: "AWAITING_ANSWER"
│  ├─ topics: [Transfer Functions]
│  └─ subtopics: [TF Basics, TF Derivation]
│
├─ Message 3 (user)
│  ├─ content: "A transfer function is the ratio..."
│  ├─ sender: "user"
│  └─ timestamp: 2024-04-07 14:31:00
│
├─ Answer 1
│  ├─ message_id: 3
│  ├─ question_id: 1
│  ├─ accuracy_score: 92
│  └─ feedback: "Great answer..."
│
└─ [And so on for subsequent questions/answers]
```

---

## Data Storage & Retrieval

### Database Schema

```sql
-- Users and Conversations
users (id PK)
conversations (id PK, user_id FK)
messages (id PK, conversation_id FK, question_id FK, answer_id FK)

-- Q&A Storage
questions (id PK, message_id FK, status, solo_level, grade)
answers (id PK, message_id FK, question_id FK, accuracy_score)

-- Topic Mapping
topics (id PK, topic_name)
subtopics (id PK, topic_id FK, subtopic_name, subtopic_summary_embedding VECTOR)
question_topics (question_id FK, topic_id FK) -- many-to-many
question_subtopics (question_id FK, subtopic_id FK) -- many-to-many

-- Course Materials
document_chunks (id PK, subtopic_id FK, content, embedding VECTOR)
```

### Key Queries

**Find relevant materials for a question:**
```sql
SELECT DISTINCT dc.content, s.subtopic_name
FROM document_chunks dc
JOIN subtopics s ON dc.subtopic_id = s.id
WHERE s.id IN (
    SELECT subtopic_id FROM question_subtopics
    WHERE question_id = :question_id
)
ORDER BY dc.embedding <-> :question_embedding
LIMIT 5;
```

**Get student's learning progression:**
```sql
SELECT q.id, q.solo_level, q.grade, q.created_at,
       COALESCE(a.accuracy_score, NULL) as answer_score
FROM questions q
LEFT JOIN answers a ON q.id = a.question_id
WHERE q.message_id IN (
    SELECT id FROM messages
    WHERE conversation_id IN (
        SELECT id FROM conversations
        WHERE user_id = :user_id
    )
)
ORDER BY q.created_at DESC;
```

---

## Integration Points

### 1. Frontend ↔ Backend

**Communication:** HTTP REST API over JSON

```
Frontend Request:
POST /api/chat
{
  "user_id": "student_123",
  "conversation_id": 1,
  "question": "What is a pole?"
}

Backend Response:
{
  "response": "I evaluated your question...",
  "question_id": 42,
  "metadata": {...}
}
```

### 2. Backend ↔ LLM API (NALA)

**Communication:** XML-formatted HTTP requests

```
Backend Request:
POST https://nala-api.example.com/api/llm/
<llm_request>
  <model>gemini-2.5-flash</model>
  <system_prompt>You are an expert educator...</system_prompt>
  <user_prompt>Evaluate this question: ...</user_prompt>
</llm_request>

LLM Response:
{
  "solo_level": "Relational",
  "grade": "A",
  "reasoning": "..."
}
```

### 3. Backend ↔ Database (PostgreSQL)

**Communication:** SQLAlchemy ORM + psycopg2

```python
# Insert example
question = Question(
    message_id=42,
    solo_taxonomy_level="Relational",
    grade="A",
    reasoning="..."
)
db.session.add(question)
db.session.commit()

# Query example
result = db.query(Question).filter(
    Question.id == 42
).first()
```