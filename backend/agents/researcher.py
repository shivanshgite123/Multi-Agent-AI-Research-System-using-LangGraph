import asyncio
import json
from typing import Dict, Any

from langchain_openai import ChatOpenAI
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper

from core.state import ResearchState


class ResearcherAgent:

    def __init__(self, model: str = "gpt-4o-mini"):

        self.llm = ChatOpenAI(
            model=model,
            temperature=0.2
        )

        self.search = DuckDuckGoSearchAPIWrapper(
            max_results=5
        )

    async def search_query(self, query: str) -> Dict[str, Any]:

        try:
            results = await asyncio.to_thread(
                self.search.results,
                query,
                5
            )

            findings = []
            sources = []

            for index, item in enumerate(results):

                finding = {
                    "query": query,
                    "title": item.get("title", ""),
                    "snippet": item.get("snippet", ""),
                    "url": item.get("link", ""),
                    "index": index
                }

                findings.append(finding)

                sources.append({
                    "title": item.get("title", ""),
                    "url": item.get("link", "")
                })

            return {
                "success": True,
                "findings": findings,
                "sources": sources
            }

        except Exception as error:

            return {
                "success": False,
                "findings": [
                    {
                        "query": query,
                        "error": str(error)
                    }
                ],
                "sources": []
            }

    async def run(self, state: ResearchState) -> Dict[str, Any]:

        queries = state.get(
            "search_queries",
            [state["query"]]
        )

        all_findings = []
        all_sources = []

        # Run searches in small batches
        for i in range(0, len(queries), 3):

            batch = queries[i:i + 3]

            tasks = [
                self.search_query(query)
                for query in batch
            ]

            results = await asyncio.gather(
                *tasks,
                return_exceptions=True
            )

            for result in results:

                if isinstance(result, Exception):
                    continue

                if result.get("success"):

                    all_findings.extend(
                        result.get("findings", [])
                    )

                    all_sources.extend(
                        result.get("sources", [])
                    )

        findings_text = []

        for item in all_findings[:15]:

            text = (
                f"Topic: {item.get('query', '')}\n"
                f"Title: {item.get('title', '')}\n"
                f"Summary: {item.get('snippet', '')}"
            )

            findings_text.append(text)

        findings_text = "\n\n".join(findings_text)

        prompt = f"""
You are reviewing web research collected from multiple sources.

Research Topic:
{state["query"]}

Research Findings:
{findings_text}

Generate:
- short research summary
- key facts
- important statistics or data points

Return the response in JSON format.
"""

        try:

            response = await self.llm.ainvoke(prompt)

            content = response.content.strip()

            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]

            summary = json.loads(content)

        except Exception:

            summary = {
                "summary": "Research findings collected successfully.",
                "key_facts": [],
                "data_points": []
            }

        unique_sources = []
        seen_urls = set()

        for source in all_sources:

            url = source.get("url")

            if not url:
                continue

            if url in seen_urls:
                continue

            seen_urls.add(url)
            unique_sources.append(source)

        return {
            "raw_findings": all_findings,
            "sources": unique_sources[:15],
            "research_summary": summary,
            "status": "research_complete",
            "current_agent": "researcher",
            "stream_update": {
                "agent": "researcher",
                "status": "complete",
                "message": f"Collected {len(all_findings)} findings from web search",
                "sources_count": len(unique_sources),
                "findings_count": len(all_findings)
            }
        }