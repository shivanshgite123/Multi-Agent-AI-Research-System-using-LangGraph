# AI Research Analyst – Multi-Agent Research System

A production-ready AI research system built using LangGraph, LangChain, FastAPI, and React.

The system uses multiple AI agents to research any topic, analyze web information, and generate detailed research reports with citations and real-time updates.

---

# Overview

This project automates the research workflow using four specialized AI agents:

- **Planner Agent** – Breaks down the topic into focused search queries
- **Researcher Agent** – Performs web searches and gathers information
- **Analyst Agent** – Extracts insights and trends from collected data
- **Writer Agent** – Generates a structured research report with citations

The system also supports:

- Real-time streaming updates
- Human approval checkpoints
- Persistent memory
- Parallel search execution

---

# Features

- Multi-agent workflow using LangGraph
- Real-time research updates with WebSockets
- Human-in-the-loop approval flow
- Persistent memory and state management
- Parallel web search execution
- Automatic citation tracking
- Multiple research depth levels
- Error handling and retry logic

---

# Architecture

```text
User Query
    |
    v
Frontend (React)
    |
WebSocket / REST API
    |
Backend (FastAPI)
    |
LangGraph Workflow
    |
Planner -> Researcher -> Analyst -> Writer
    |
Final Research Report
```

---

# Tech Stack

## Backend

- Python
- LangGraph
- LangChain
- FastAPI
- WebSockets
- DuckDuckGo Search API

## Frontend

- React
- TypeScript
- Tailwind CSS
- shadcn/ui

## AI Models

- OpenAI GPT Models
- Ollama (Optional Local Models)

---

# Project Structure

```text
ai-research-analyst/
│
├── backend/
│   ├── agents/
│   ├── core/
│   ├── main.py
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   └── dist/
│
└── README.md
```

---

# Installation

## Clone Repository

```bash
git clone <repository-url>
cd ai-research-analyst
```

---

# Backend Setup

```bash
cd backend

python -m venv venv

source venv/bin/activate
```

### Windows

```bash
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Set OpenAI API key:

```bash
export OPENAI_API_KEY="your-api-key"
```

Run backend server:

```bash
python main.py
```

Backend runs on:

```text
http://localhost:8000
```

---

# Frontend Setup

```bash
cd frontend

npm install
npm run build

npx serve dist
```

Frontend runs on:

```text
http://localhost:3000
```

---

# API Endpoints

## REST API

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| GET | `/api/agents` | Agent details |
| POST | `/api/research` | Start research |
| GET | `/api/research/{thread_id}` | Get result |
| GET | `/api/research/{thread_id}/status` | Check status |

---

# WebSocket Endpoint

```text
ws://localhost:8000/ws/research
```

## Example Request

```json
{
  "query": "AI agent startups 2025",
  "depth": "standard"
}
```

## Example Progress Response

```json
{
  "type": "progress",
  "agent": "researcher",
  "status": "complete",
  "message": "Found research findings from multiple sources"
}
```

---

# LangGraph Workflow

```text
START
  |
Planner
  |
Researcher
  |
Analyst
  |
Writer
  |
END
```

Optional human approval flow can redirect the process back to the planner for revisions.

---

# State Management

```python
class ResearchState(TypedDict):
    query: str
    depth: str
    search_queries: List[str]
    raw_findings: List[Dict]
    analysis: str
    report: str
    sources: List[Dict]
    approved: bool
    status: str
```

---

# Customization

## Add New Agents

Create a new file inside:

```text
backend/agents/
```

Then register the agent inside the workflow configuration.

---

# Deployment

## Docker Example

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY backend/requirements.txt .

RUN pip install -r requirements.txt

COPY backend/ .

CMD ["python", "main.py"]
```

---

# Skills Demonstrated

- Multi-Agent AI Systems
- LangGraph Workflows
- LangChain Integration
- FastAPI Development
- Real-Time Streaming with WebSockets
- AI Agent Orchestration
- State Management
- Error Handling and Retry Logic
- React and TypeScript Frontend Development

---

# Future Improvements

- Add vector database integration for RAG
- Support additional search providers
- Add authentication and user sessions
- Improve report visualization
- Add PDF and Markdown export support
