import json
from typing import Dict, Any
from langchain_openai import ChatOpenAI
from core.state import ResearchState


class AnalystAgent:

    def __init__(self, model: str = "gpt-4o-mini"):
        self.llm = ChatOpenAI(
            model=model,
            temperature=0.3
        )

    async def run(self, state: ResearchState) -> Dict[str, Any]:

        query = state["query"]
        raw_findings = state.get("raw_findings", [])
        research_plan = state.get("research_plan", {})

        if not raw_findings:
            return {
                "analysis": "No research findings available.",
                "key_insights": [],
                "status": "analysis_complete",
                "current_agent": "analyst"
            }

        findings = []

        for item in raw_findings[:20]:
            text = (
                f"Topic: {item.get('query', '')}\n"
                f"Title: {item.get('title', '')}\n"
                f"Summary: {item.get('snippet', '')}"
            )
            findings.append(text)

        findings_text = "\n\n".join(findings)

        sources = []

        for source in state.get("sources", [])[:10]:
            sources.append(
                f"{source.get('title', '')} - {source.get('url', '')}"
            )

        sources_text = "\n".join(sources)

        prompt = f"""
You are helping analyze research collected from multiple web sources.

Research Topic:
{query}

Objective:
{research_plan.get('objective', query)}

Questions:
{', '.join(research_plan.get('key_questions', [query]))}

Research Findings:
{findings_text}

Sources:
{sources_text}

Analyze the findings and return:
- overall analysis
- important insights
- major trends
- research gaps
- confidence score
- recommendations

Return the response in JSON format.
"""

        response = await self.llm.ainvoke(prompt)

        try:
            content = response.content.strip()

            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]

            result = json.loads(content)

            insights = result.get("key_insights", [])

            return {
                "analysis": result.get("analysis", ""),
                "key_insights": insights,
                "status": "analysis_complete",
                "current_agent": "analyst",
                "stream_update": {
                    "agent": "analyst",
                    "status": "complete",
                    "message": f"Generated {len(insights)} insights",
                    "insights_count": len(insights),
                    "confidence": result.get("confidence_score", 0.75)
                }
            }

        except json.JSONDecodeError:

            return {
                "analysis": response.content,
                "key_insights": ["Could not parse structured insights"],
                "status": "analysis_complete",
                "current_agent": "analyst",
                "stream_update": {
                    "agent": "analyst",
                    "status": "complete",
                    "message": "Analysis finished"
                }
            }