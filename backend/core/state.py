from typing import (
    TypedDict,
    Annotated,
    List,
    Dict,
    Any,
    Optional,
    Literal
)

from langgraph.graph.message import add_messages


class ResearchState(TypedDict):

    # User input
    query: str
    depth: Literal["quick", "standard", "deep"]

    # Shared conversation history
    messages: Annotated[list, add_messages]

    # Planner output
    search_queries: List[str]
    research_plan: Dict[str, Any]

    # Researcher output
    raw_findings: List[Dict[str, Any]]
    sources: List[Dict[str, str]]

    # Analyst output
    analysis: str
    key_insights: List[str]

    # Writer output
    report: str
    report_sections: Dict[str, str]

    # Human feedback
    human_feedback: Optional[str]
    approved: bool

    # Workflow tracking
    status: str
    current_agent: str

    # Retry and iteration tracking
    iteration_count: int
    error_count: int

    # Live frontend updates
    stream_update: Optional[Dict[str, Any]]