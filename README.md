# RIG Query Agent 🛢️

An AI-powered query agent for offshore oil rig operators. Ask natural language questions about equipment, work packs, shifts, procedures, and maintenance checklists.

![Version](https://img.shields.io/badge/version-1.0.4-amber) ![Status](https://img.shields.io/badge/status-operational-green)

---

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Folder Structure](#folder-structure)
- [Quick Start (Local)](#quick-start-local)
- [Environment Setup](#environment-setup)
- [Running the Backend](#running-the-backend)
- [Running the Frontend](#running-the-frontend)
- [Database Initialization](#database-initialization)
- [Sample Queries](#sample-queries)
- [Deployment](#deployment)
  - [Backend → Render](#backend--render)
  - [Frontend → Vercel](#frontend--vercel)
- [AI Agent Design](#ai-agent-design)
- [Future Improvements](#future-improvements)

---

## Overview

RIG Query Agent is a demo prototype showcasing an AI assistant for offshore rig operations. It uses:

- **FastAPI** backend with a single AI agent routing queries to 6 specialized tools
- **SQLite** database with realistic sample data (15 work packs, 40 procedures, 120 operations, 20 shifts)
- **FAISS** vector database with RAG for equipment knowledge (10 equipment manuals)
- **ReportLab** PDF generation for maintenance checklists
- **React + TypeScript + Tailwind CSS** frontend with dark industrial UI

---

## Architecture

```
User (Browser)
      ↓
React + Tailwind Frontend  (Vercel)
      ↓  HTTP POST /query
FastAPI Backend             (Render)
      ↓
AI Agent (route_query)
      ↓
 ┌────────────────────────────────────────┐
 │  Intent Detection                       │
 │  ┌─────────────────────────────────┐   │
 │  │ equipment  → RAG (FAISS)        │   │
 │  │ work_pack  → SQLite query       │   │
 │  │ shift      → SQLite query       │   │
 │  │ procedure  → SQLite query       │   │
 │  │ checklist  → SQLite query       │   │
 │  │ checklist_pdf → PDF Generator   │   │
 │  └─────────────────────────────────┘   │
 └────────────────────────────────────────┘
      ↓
 LLM (OpenAI-compatible) → Natural Language Response
```

---

## Folder Structure

```
rig-query-agent/
├── backend/
│   ├── main.py             # FastAPI app + all endpoints
│   ├── router.py           # Intent routing (route_query)
│   ├── agent_tools.py      # 6 agent tools
│   ├── database.py         # SQLAlchemy models
│   ├── setup_db.py         # Database seeder
│   ├── rag.py              # FAISS RAG pipeline
│   ├── pdf_generator.py    # ReportLab PDF generation
│   ├── models.py           # Pydantic models
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/     # Layout, Sidebar
│   │   ├── pages/          # Chat, SystemStatus, RigData, ModelConfig, RecentQueries
│   │   ├── types.ts
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   └── index.css
│   ├── package.json
│   ├── tailwind.config.js
│   ├── vite.config.ts
│   └── vercel.json
└── README.md
```

---

## Quick Start (Local)

### Prerequisites

- Python 3.10+
- Node.js 18+
- Git

### Clone

```bash
git clone <your-repo-url>
cd rig-query-agent
```

---

## Environment Setup

### Backend

```bash
cd backend
cp .env.example .env
```

Edit `.env`:

```env
# Required for AI responses (uses fallback if not set)
OPENAI_API_KEY=your_openai_api_key_here

# Optional: change provider (e.g., Groq, Anthropic via compatible endpoint)
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini

# These have sensible defaults
DATABASE_URL=sqlite:///./rig_query.db
FAISS_INDEX_PATH=./faiss_index
PDF_OUTPUT_DIR=./generated_pdfs
CORS_ORIGINS=http://localhost:5173
```

### Frontend

```bash
cd frontend
cp .env.example .env
```

Edit `.env`:

```env
VITE_API_URL=http://localhost:8000
```

---

## Running the Backend

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate
# Activate (Mac/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Initialize database with sample data
python setup_db.py

# Start the server
uvicorn main:app --reload --port 8000
```

The backend will:
1. Create the SQLite database
2. Seed sample data (15 WPs, 40 procedures, 120 ops, 20 shifts, 20 checklists)
3. Build the FAISS index from equipment manuals (~30s first run, downloads ~80MB model)
4. Start serving at `http://localhost:8000`

API docs available at `http://localhost:8000/docs`

---

## Running the Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

Open `http://localhost:5173` in your browser.

---

## Database Initialization

The database is automatically seeded when you run `python setup_db.py`. To re-seed:

```bash
python setup_db.py --force
```

Sample data includes:
| Table | Count |
|-------|-------|
| Work Packs | 15 |
| Procedures | 40 |
| Operations | 120+ |
| Shifts | 20 |
| Checklists | 20 |
| Checklist Items | 100+ |
| Equipment KB | 10 |

---

## Sample Queries

Try these in the chat:

| Question | Tool Used |
|----------|-----------|
| What is a Blowout Preventer? | RAG (Equipment) |
| How many active work packs? | SQL (WorkPack) |
| Show active work packs | SQL (WorkPack) |
| Who is in the current shift? | SQL (Shift) |
| Who worked the previous shift? | SQL (Shift) |
| Show completed procedures | SQL (Procedure) |
| Show procedure P103 | SQL (Procedure) |
| Generate checklist for Pump Inspection | SQL (Checklist) + PDF |
| Download Mud Pump checklist | PDF Generator |
| What is a Top Drive? | RAG (Equipment) |
| Explain Mud Motor | RAG (Equipment) |
| How does Draw Works operate? | RAG (Equipment) |

---

## Deployment

### Backend → Render

1. Create a new **Web Service** on [render.com](https://render.com)
2. Connect your GitHub repo
3. Set:
   - **Root Directory**: `backend`
   - **Build Command**: `pip install -r requirements.txt && python setup_db.py`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Add **Environment Variables**:
   ```
   OPENAI_API_KEY=your_key
   OPENAI_MODEL=gpt-4o-mini
   CORS_ORIGINS=https://your-frontend.vercel.app
   ```
5. Note your Render URL: `https://rig-query-agent.onrender.com`

### Frontend → Vercel

1. Import your repo on [vercel.com](https://vercel.com)
2. Set:
   - **Root Directory**: `frontend`
   - **Framework**: Vite
3. Add **Environment Variables**:
   ```
   VITE_API_URL=https://rig-query-agent.onrender.com
   ```
4. Deploy!

---

## AI Agent Design

The agent uses **keyword-based intent routing** in `router.py`:

```python
route_query("How many active work packs?")  # → "work_pack"
route_query("What is a Blowout Preventer?") # → "equipment"
route_query("Download Mud Pump checklist")  # → "checklist_pdf"
```

### Tools

| Tool | File | Description |
|------|------|-------------|
| `tool_equipment_knowledge` | `agent_tools.py` | FAISS semantic search over equipment manuals |
| `tool_work_pack_query` | `agent_tools.py` | SQL queries for work pack data |
| `tool_shift_query` | `agent_tools.py` | SQL queries for shift/operator data |
| `tool_procedure_query` | `agent_tools.py` | SQL queries for procedure status |
| `tool_checklist_search` | `agent_tools.py` | SQL queries for checklist items |
| `tool_generate_checklist_pdf` | `agent_tools.py` | Generates PDF via ReportLab |

### LLM Abstraction

Swap providers by setting environment variables — no code changes needed:

```env
# OpenAI
OPENAI_API_KEY=sk-...
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini

# Groq
OPENAI_API_KEY=gsk_...
OPENAI_BASE_URL=https://api.groq.com/openai/v1
OPENAI_MODEL=llama3-70b-8192

# Ollama (local)
OPENAI_API_KEY=ollama
OPENAI_BASE_URL=http://localhost:11434/v1
OPENAI_MODEL=llama3
```

---

## Future Improvements

- [ ] Persistent chat history (PostgreSQL)
- [ ] Authentication (JWT)
- [ ] Real-time telemetry via WebSocket
- [ ] LLM function calling (tool use) for more accurate routing
- [ ] Multi-rig support
- [ ] Voice input
- [ ] Email alerts for critical events
- [ ] Mobile app (React Native)
- [ ] Integration with real SCADA systems
- [ ] Multilingual support
