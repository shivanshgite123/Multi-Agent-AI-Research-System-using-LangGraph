"""
LangGraph workflow definition for the Multi-Agent Research System.
Implements the orchestration layer connecting all agents.
"""

from typing import Dict, Any, Literal
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from core.state import ResearchState
from agents.planner import PlannerAgent
from agents.researcher import ResearcherAgent
from agents.analyst import AnalystAgent
from agents.writer import WriterAgent


class ResearchWorkflow:
    """Orchestrates the multi-agent research pipeline using LangGraph."""
    
    def __init__(self):
        self.planner = PlannerAgent()
        self.researcher = ResearcherAgent()
        self.analyst = AnalystAgent()
        self.writer = WriterAgent()
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph state machine."""
        
        # Create graph
        workflow = StateGraph(ResearchState)
        
        # Add nodes
        workflow.add_node("planner", self._planner_node)
        workflow.add_node("researcher", self._researcher_node)
        workflow.add_node("analyst", self._analyst_node)
        workflow.add_node("writer", self._writer_node)
        workflow.add_node("human_review", self._human_review_node)
        
        # Define edges
        workflow.set_entry_point("planner")
        workflow.add_edge("planner", "researcher")
        workflow.add_edge("researcher", "analyst")
        workflow.add_edge("analyst", "writer")
        workflow.add_edge("writer", "human_review")
        
        # Conditional edges from human review
        workflow.add_conditional_edges(
            "human_review",
            self._review_decision,
            {
                "approved": END,
                "revise": "planner",
                "continue": END
            }
        )
        
        # Compile with memory checkpointer
        memory = MemorySaver()
        return workflow.compile(checkpointer=memory)
    
    async def _planner_node(self, state: ResearchState) -> Dict[str, Any]:
        """Execute planner agent."""
        try:
            result = await self.planner.run(state)
            return {
                **result,
                "iteration_count": state.get("iteration_count", 0) + 1,
                "messages": state.get("messages", []) + [("assistant", f"Planner: {result.get('stream_update', {}).get('message', 'Plan created')}")]
            }
        except Exception as e:
            return {
                "search_queries": [state["query"]],
                "status": "planning_error",
                "error_count": state.get("error_count", 0) + 1,
                "stream_update": {
                    "agent": "planner",
                    "status": "error",
                    "message": f"Planning error: {str(e)}"
                }
            }
    
    async def _researcher_node(self, state: ResearchState) -> Dict[str, Any]:
        """Execute researcher agent."""
        try:
            result = await self.researcher.run(state)
            return {
                **result,
                "messages": state.get("messages", []) + [("assistant", f"Researcher: {result.get('stream_update', {}).get('message', 'Research complete')}")]
            }
        except Exception as e:
            return {
                "raw_findings": [],
                "sources": [],
                "status": "research_error",
                "error_count": state.get("error_count", 0) + 1,
                "stream_update": {
                    "agent": "researcher",
                    "status": "error",
                    "message": f"Research error: {str(e)}"
                }
            }
    
    async def _analyst_node(self, state: ResearchState) -> Dict[str, Any]:
        """Execute analyst agent."""
        try:
            result = await self.analyst.run(state)
            return {
                **result,
                "messages": state.get("messages", []) + [("assistant", f"Analyst: {result.get('stream_update', {}).get('message', 'Analysis complete')}")]
            }
        except Exception as e:
            return {
                "analysis": "Analysis could not be completed due to an error.",
                "key_insights": [],
                "status": "analysis_error",
                "error_count": state.get("error_count", 0) + 1,
                "stream_update": {
                    "agent": "analyst",
                    "status": "error",
                    "message": f"Analysis error: {str(e)}"
                }
            }
    
    async def _writer_node(self, state: ResearchState) -> Dict[str, Any]:
        """Execute writer agent."""
        try:
            result = await self.writer.run(state)
            return {
                **result,
                "messages": state.get("messages", []) + [("assistant", f"Writer: {result.get('stream_update', {}).get('message', 'Report generated')}")]
            }
        except Exception as e:
            return {
                "report": f"Report generation error: {str(e)}",
                "report_sections": {},
                "status": "writing_error",
                "error_count": state.get("error_count", 0) + 1,
                "stream_update": {
                    "agent": "writer",
                    "status": "error",
                    "message": f"Writing error: {str(e)}"
                }
            }
    
    def _human_review_node(self, state: ResearchState) -> Dict[str, Any]:
        """Human review checkpoint."""
        return {
            "status": "awaiting_review",
            "stream_update": {
                "agent": "review",
                "status": "awaiting_feedback",
                "message": "Report ready for review. Approve or request revisions."
            }
        }
    
    def _review_decision(self, state: ResearchState) -> Literal["approved", "revise", "continue"]:
        """Determine flow based on human feedback."""
        if state.get("approved", False):
            return "approved"
        elif state.get("human_feedback"):
            return "revise"
        return "continue"
    
    async def run(self, query: str, depth: str = "standard", thread_id: str = "default") -> Dict[str, Any]:
        """Execute the complete research workflow."""
        initial_state: ResearchState = {
            "query": query,
            "depth": depth,
            "messages": [],
            "search_queries": [],
            "research_plan": {},
            "raw_findings": [],
            "sources": [],
            "analysis": "",
            "key_insights": [],
            "report": "",
            "report_sections": {},
            "human_feedback": None,
            "approved": True,  # Auto-approve for demo
            "status": "started",
            "current_agent": "",
            "iteration_count": 0,
            "error_count": 0,
            "stream_update": None
        }
        
        config = {"configurable": {"thread_id": thread_id}}
        
        # Stream execution for real-time updates
        final_state = None
        async for event in self.graph.astream(initial_state, config, stream_mode="updates"):
            final_state = event
        
        return final_state
    
    async def stream_run(self, query: str, depth: str = "standard", thread_id: str = "default"):
        """Stream the workflow execution for real-time updates."""
        initial_state: ResearchState = {
            "query": query,
            "depth": depth,
            "messages": [],
            "search_queries": [],
            "research_plan": {},
            "raw_findings": [],
            "sources": [],
            "analysis": "",
            "key_insights": [],
            "report": "",
            "report_sections": {},
            "human_feedback": None,
            "approved": True,
            "status": "started",
            "current_agent": "",
            "iteration_count": 0,
            "error_count": 0,
            "stream_update": {"agent": "system", "status": "started", "message": "Starting research workflow"}
        }
        
        config = {"configurable": {"thread_id": thread_id}}
        
        async for event in self.graph.astream(initial_state, config, stream_mode="updates"):
            # Extract stream updates from each node
            for node_name, node_data in event.items():
                if isinstance(node_data, dict) and "stream_update" in node_data and node_data["stream_update"]:
                    yield node_data["stream_update"]


# Singleton instance
workflow = ResearchWorkflow()
