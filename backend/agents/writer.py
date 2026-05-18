import json
import re
from typing import Dict, Any

from langchain_openai import ChatOpenAI

from core.state import ResearchState


class WriterAgent:

    def __init__(self, model: str = "gpt-4o-mini"):

        self.llm = ChatOpenAI(
            model=model,
            temperature=0.4
        )

    async def run(self, state: ResearchState) -> Dict[str, Any]:

        query = state["query"]

        analysis = state.get("analysis", "")
        key_insights = state.get("key_insights", [])
        sources = state.get("sources", [])
        research_plan = state.get("research_plan", {})

        formatted_sources = []

        for index, source in enumerate(sources):

            source_text = (
                f"[{index + 1}] "
                f"{source.get('title', 'Untitled')} "
                f"- {source.get('url', '')}"
            )

            formatted_sources.append(source_text)

        sources_text = "\n".join(formatted_sources)

        insights_text = "\n".join([
            f"- {insight}"
            for insight in key_insights
        ])

        prompt = f"""
Write a detailed research report.

Topic:
{query}

Research Objective:
{research_plan.get('objective', query)}

Analysis:
{analysis}

Key Insights:
{insights_text}

Sources:
{sources_text}

Structure the report with:
- Executive Summary
- Introduction
- Key Findings
- Trends and Future Outlook
- Challenges
- Conclusion
- Sources

Use markdown formatting and cite sources where needed.
"""

        response = await self.llm.ainvoke(prompt)

        report = response.content

        sections = self.parse_sections(report)

        return {
            "report": report,
            "report_sections": sections,
            "status": "report_complete",
            "current_agent": "writer",
            "stream_update": {
                "agent": "writer",
                "status": "complete",
                "message": f"Research report generated with {len(sections)} sections",
                "report_length": len(report),
                "sources_cited": len(sources)
            }
        }

    def parse_sections(self, report: str) -> Dict[str, str]:

        sections = {}

        current_section = "Introduction"
        current_content = []

        for line in report.split("\n"):

            if line.startswith("#"):

                if current_content:

                    sections[current_section] = "\n".join(
                        current_content
                    ).strip()

                current_section = line.lstrip("# ").strip()

                current_content = []

            else:
                current_content.append(line)

        if current_content:

            sections[current_section] = "\n".join(
                current_content
            ).strip()

        return sections