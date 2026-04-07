# NALA-Assess Chatbot - Frontend Architecture & Setup Guide

## Overview

The frontend is a **React + Vite** single-page application that provides an interactive interface for students to ask questions and receive AI-powered evaluations.

**Tech Stack:**
- **React**: UI framework
- **Vite**: Build tool (ultra-fast development)
- **Material-UI**: Component library
- **Axios**: HTTP client
- **React Router**: Client-side routing
- **React Markdown**: Markdown rendering with LaTeX support

---

## Project Structure

```
frontend/
├── index.html                    # Entry HTML file
├── vite.config.js                # Vite configuration
├── eslint.config.js              # ESLint rules
├── package.json                  # Dependencies
├── .env                          # Environment variables
├── dist/                         # Build output
├── public/                       # Static assets
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
    │   ├── api_fetch.js          # HTTP request utilities
    │   ├── api_retrieval.js      # Data fetching logic
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

## Build & Deploy

### Development

```bash
npm run dev
```

### Production Build

```bash
npm run build
```

## API Response Handling

### Question Evaluation Response

```json
{
  "response": "**I have evaluated your question based on the SOLO taxonomy!**\n\n[formatted evaluation]",
  "conversation_id": "1",
  "user_message_id": 42,
  "chatbot_message_id": 43,
  "evaluation_type": "QUESTION_GRADED",
  "question_id": 10,
  "metadata": {
    "solo_level": "Relational",
    "grade": "A",
    "reasoning": "Your question demonstrates...",
    "reference_material": "Based on the course materials, [relevant excerpts]",
    "relevant_topic_ids": [5],
    "relevant_subtopic_ids": [1, 2]
  }
}
```

### Answer Evaluation Response

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