"""
Planner Agent: Decomposes the user query into a structured research plan.
"""

import json
from typing import Dict, Any
from langchain_openai import ChatOpenAI
from core.state import ResearchState


class PlannerAgent:
    """Agent responsible for creating research plans and search queries."""
    
    def __init__(self, model: str = "gpt-4o-mini"):
        self.llm = ChatOpenAI(model=model, temperature=0.3)
    
    async def run(self, state: ResearchState) -> Dict[str, Any]:
        """Create a research plan based on the user's query."""
        query = state["query"]
        depth = state.get("depth", "standard")
        
        depth_config = {
            "quick": {"num_queries": 3, "iterations": 1},
            "standard": {"num_queries": 5, "iterations": 2},
            "deep": {"num_queries": 8, "iterations": 3}
        }
        config = depth_config.get(depth, depth_config["standard"])
        
        system_prompt = f"""You are an expert research planner. Your job is to decompose a research topic into specific, actionable search queries.

Guidelines:
- Create {config['num_queries']} targeted search queries
- Each query should be specific and searchable
- Cover different angles: background, recent developments, expert opinions, data/statistics, criticism/controversy
- Queries should be optimized for web search (clear, specific, 5-10 words each)

Respond ONLY with a valid JSON object in this exact format:
{{
    "search_queries": ["query1", "query2", ...],
    "research_plan": {{
        "objective": "Main research objective",
        "key_questions": ["question1", "question2", ...],
        "approach": "Brief research methodology description",
        "expected_sections": ["section1", "section2", ...]
    }}}
}}"""

        messages = [
            ("system", system_prompt),
            ("human", f"Create a research plan for: {query}")
        ]
        
        response = await self.llm.ainvoke(messages)
        
        try:
            content = response.content
            # Extract JSON from potential markdown code blocks
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            
            result = json.loads(content.strip())
            return {
                "search_queries": result.get("search_queries", [query]),
                "research_plan": result.get("research_plan", {}),
                "status": "planning_complete",
                "current_agent": "planner",
                "stream_update": {
                    "agent": "planner",
                    "status": "complete",
                    "message": f"Created research plan with {len(result.get('search_queries', []))} search queries",
                    "queries": result.get("search_queries", [])
                }
            }
        except json.JSONDecodeError:
            # Fallback: use query as single search query
            return {
                "search_queries": [query],
                "research_plan": {"objective": query, "key_questions": [query]},
                "status": "planning_complete",
                "current_agent": "planner",
                "stream_update": {
                    "agent": "planner",
                    "status": "complete",
                    "message": "Created basic research plan"
                }
            }
