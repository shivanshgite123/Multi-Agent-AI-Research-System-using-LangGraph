import os
import uuid
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import (
    FastAPI,
    WebSocket,
    WebSocketDisconnect,
    HTTPException
)

from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from pydantic import BaseModel, Field
from dotenv import load_dotenv

from core.workflow import workflow


load_dotenv()


class ResearchRequest(BaseModel):

    query: str = Field(
        ...,
        min_length=3,
        max_length=500
    )

    depth: str = Field(
        default="standard",
        pattern="^(quick|standard|deep)$"
    )


class ResearchResponse(BaseModel):

    thread_id: str
    status: str
    message: str


class ResearchResult(BaseModel):

    query: str
    status: str
    report: str
    sources: list
    key_insights: list
    analysis: str
    report_sections: dict
    metadata: dict


active_sessions = {}


@asynccontextmanager
async def lifespan(app: FastAPI):

    print("Starting AI Research Analyst Server")

    yield

    print("Stopping Server")


app = FastAPI(
    title="AI Research Analyst",
    description="Multi-agent research system using LangGraph",
    version="1.0.0",
    lifespan=lifespan
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.get("/")
async def home():

    return {
        "status": "running",
        "service": "AI Research Analyst",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/api/agents")
async def get_agents():

    return {
        "agents": [
            {
                "name": "planner",
                "role": "Creates research strategy"
            },
            {
                "name": "researcher",
                "role": "Collects web research"
            },
            {
                "name": "analyst",
                "role": "Analyzes findings"
            },
            {
                "name": "writer",
                "role": "Generates final report"
            }
        ]
    }


@app.post(
    "/api/research",
    response_model=ResearchResponse
)
async def start_research(
    request: ResearchRequest
):

    thread_id = str(uuid.uuid4())

    try:

        result = await workflow.run(
            query=request.query,
            depth=request.depth,
            thread_id=thread_id
        )

        active_sessions[thread_id] = {
            "query": request.query,
            "depth": request.depth,
            "status": "complete",
            "result": result
        }

        return ResearchResponse(
            thread_id=thread_id,
            status="complete",
            message="Research completed"
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )


@app.get(
    "/api/research/{thread_id}",
    response_model=ResearchResult
)
async def get_research_result(
    thread_id: str
):

    session = active_sessions.get(thread_id)

    if not session:

        raise HTTPException(
            status_code=404,
            detail="Research session not found"
        )

    result = session.get("result", {})

    final_state = {}

    if isinstance(result, dict):

        for _, value in result.items():

            if isinstance(value, dict):
                final_state = value
                break

    return ResearchResult(
        query=session.get("query", ""),
        status=final_state.get("status", "unknown"),
        report=final_state.get(
            "report",
            "No report generated"
        ),
        sources=final_state.get("sources", []),
        key_insights=final_state.get(
            "key_insights",
            []
        ),
        analysis=final_state.get("analysis", ""),
        report_sections=final_state.get(
            "report_sections",
            {}
        ),
        metadata={
            "depth": session.get("depth"),
            "iteration_count": final_state.get(
                "iteration_count",
                0
            ),
            "error_count": final_state.get(
                "error_count",
                0
            ),
            "sources_found": len(
                final_state.get("sources", [])
            )
        }
    )


@app.websocket("/ws/research")
async def research_socket(
    websocket: WebSocket
):

    await websocket.accept()

    try:

        data = await websocket.receive_json()

        query = data.get("query", "")
        depth = data.get("depth", "standard")

        if len(query) < 3:

            await websocket.send_json({
                "type": "error",
                "message": "Query is too short"
            })

            return

        thread_id = str(uuid.uuid4())

        await websocket.send_json({
            "type": "started",
            "thread_id": thread_id,
            "message": f"Research started for: {query}",
            "timestamp": datetime.utcnow().isoformat()
        })

        async for update in workflow.stream_run(
            query=query,
            depth=depth,
            thread_id=thread_id
        ):

            await websocket.send_json({
                "type": "progress",
                "agent": update.get("agent"),
                "status": update.get("status"),
                "message": update.get("message"),
                "timestamp": datetime.utcnow().isoformat()
            })

        config = {
            "configurable": {
                "thread_id": thread_id
            }
        }

        state_values = {}

        try:

            state = await workflow.graph.aget_state(
                config
            )

            if state and hasattr(state, "values"):
                state_values = state.values

        except Exception:
            pass

        await websocket.send_json({
            "type": "complete",
            "message": "Research completed",
            "report": state_values.get("report", ""),
            "sources": state_values.get("sources", []),
            "key_insights": state_values.get(
                "key_insights",
                []
            ),
            "analysis": state_values.get(
                "analysis",
                ""
            ),
            "timestamp": datetime.utcnow().isoformat()
        })

    except WebSocketDisconnect:

        print("Client disconnected")

    except Exception as error:

        await websocket.send_json({
            "type": "error",
            "message": str(error),
            "timestamp": datetime.utcnow().isoformat()
        })


@app.get("/api/research/{thread_id}/status")
async def research_status(
    thread_id: str
):

    session = active_sessions.get(thread_id)

    if not session:

        return {
            "status": "not_found"
        }

    return {
        "thread_id": thread_id,
        "status": session.get("status"),
        "query": session.get("query"),
        "depth": session.get("depth")
    }


if os.path.exists("dist"):

    app.mount(
        "/",
        StaticFiles(
            directory="dist",
            html=True
        ),
        name="static"
    )


if __name__ == "__main__":

    import uvicorn

    port = int(
        os.environ.get("PORT", 8000)
    )

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True
    )