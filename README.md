AI Research Analyst – Multi-Agent Research System

A production-ready AI research system built using LangGraph, LangChain, FastAPI, and React. The system uses multiple AI agents to research any topic, analyze information from the web, and generate structured research reports with citations and real-time updates.

Overview

This project automates the research workflow using four specialized AI agents:

Planner Agent – Breaks down the research topic into focused search queries
Researcher Agent – Performs web searches and collects information from multiple sources
Analyst Agent – Extracts insights, trends, and key findings from collected data
Writer Agent – Generates a detailed research report with citations

The system supports real-time streaming updates, human approval checkpoints, persistent memory, and parallel research execution.

Features
Multi-agent workflow using LangGraph
Real-time research progress with WebSockets
Human-in-the-loop approval flow
Persistent memory and state management
Parallel web search execution
Automatic citation tracking
Multiple research depth levels
Error handling with retry mechanisms
Architecture
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
Tech Stack
Backend
Python
LangGraph
LangChain
FastAPI
WebSockets
DuckDuckGo Search API
Frontend
React
TypeScript
Tailwind CSS
shadcn/ui
AI Models
OpenAI GPT Models
Ollama (Optional Local Models)
Project Structure
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
Installation
Clone the Repository
git clone <repository-url>
cd ai-research-analyst
Backend Setup
cd backend

python -m venv venv

source venv/bin/activate
# Windows:
# venv\Scripts\activate

pip install -r requirements.txt

Set your OpenAI API key:

export OPENAI_API_KEY="your-api-key"

Run the backend server:

python main.py

Backend runs on:

http://localhost:8000
Frontend Setup
cd frontend

npm install
npm run build

npx serve dist

Frontend runs on:

http://localhost:3000
API Endpoints
REST API
Method	Endpoint	Description
GET	/	Health check
GET	/api/agents	Agent details
POST	/api/research	Start research
GET	/api/research/{thread_id}	Get result
GET	/api/research/{thread_id}/status	Check status
WebSocket Endpoint
ws://localhost:8000/ws/research
Example Request
{
  "query": "AI agent startups 2025",
  "depth": "standard"
}
Example Progress Response
{
  "type": "progress",
  "agent": "researcher",
  "status": "complete",
  "message": "Found research findings from multiple sources"
}
LangGraph Workflow
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

Optional human approval flow can redirect the process back to the planner for revisions.

State Management

The system uses a shared state object throughout the workflow.

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
Customization
Add New Agents

Create a new file inside:

backend/agents/

Register the agent inside the workflow configuration.

Deployment
Docker Example
FROM python:3.11-slim

WORKDIR /app

COPY backend/requirements.txt .

RUN pip install -r requirements.txt

COPY backend/ .

CMD ["python", "main.py"]
Skills Demonstrated
Multi-Agent AI Systems
LangGraph Workflows
LangChain Integration
FastAPI Development
Real-Time Streaming with WebSockets
AI Agent Orchestration
State Management
Error Handling and Retry Logic
React and TypeScript Frontend Development
Future Improvements
Add vector database integration for RAG
Support additional search providers
Add authentication and user sessions
Improve report visualization
Add export options for PDF and Markdown


