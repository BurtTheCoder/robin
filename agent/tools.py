"""Custom tools for the Robin OSINT agent."""
import asyncio
import re
from datetime import datetime
from typing import Any

from claude_code_sdk import tool

# Import core functionality
from core.search import get_search_results
from core.scrape import scrape_multiple

# Import sub-agent orchestration
from .subagents import run_subagent, run_subagents_parallel, get_available_subagents


@tool(
    "darkweb_search",
    "Search multiple dark web search engines simultaneously via Tor. Returns deduplicated results with titles and .onion links. Use this to gather initial intelligence on a topic.",
    {
        "query": str,
        "max_workers": int,
    }
)
async def darkweb_search(args: dict[str, Any]) -> dict[str, Any]:
    """
    Search 17 dark web search engines concurrently via Tor.
    Returns unique results with title and link.
    """
    query = args["query"]
    max_workers = args.get("max_workers", 5)

    # Run synchronous search in executor
    loop = asyncio.get_running_loop()
    try:
        results = await loop.run_in_executor(
            None,
            lambda: get_search_results(query.replace(" ", "+"), max_workers=max_workers)
        )
    except Exception as e:
        return {
            "content": [{
                "type": "text",
                "text": f"Search failed: {str(e)}. Make sure Tor is running on port 9050."
            }]
        }

    if not results:
        return {
            "content": [{
                "type": "text",
                "text": "No results found. Try refining your search query or check Tor connectivity."
            }]
        }

    # Format results for agent consumption - include full URLs so agent can pass to scrape
    formatted = []
    for i, res in enumerate(results, 1):
        title = res["title"][:80] + "..." if len(res["title"]) > 80 else res["title"]
        link = res["link"]
        formatted.append(f"{i}. **{title}**\n   URL: {link}")

    # Limit display to first 50 results to avoid context overflow
    display_results = formatted[:50]
    total_count = len(results)

    result_text = f"Found **{total_count}** unique results from dark web search engines.\n\n"
    result_text += "\n\n".join(display_results)

    if total_count > 50:
        result_text += f"\n\n... and {total_count - 50} more results."

    result_text += "\n\n**Next step**: Select the most relevant results and use `darkweb_scrape` with a list of targets containing title and link for each."

    return {
        "content": [{
            "type": "text",
            "text": result_text
        }]
    }


@tool(
    "darkweb_scrape",
    "Scrape and extract text content from .onion URLs via Tor. Pass a list of target objects, each with 'title' and 'link' keys. Returns cleaned text content from each page.",
    {
        "targets": list,
        "max_workers": int,
    }
)
async def darkweb_scrape(args: dict[str, Any]) -> dict[str, Any]:
    """
    Scrape multiple .onion URLs concurrently via Tor.
    Returns cleaned text content for each URL.

    Args:
        targets: List of dicts with 'title' and 'link' keys
        max_workers: Number of concurrent scraping threads (default 5)
    """
    targets = args["targets"]
    max_workers = args.get("max_workers", 5)

    if not targets:
        return {
            "content": [{
                "type": "text",
                "text": "No targets provided. Please specify URLs to scrape as a list of objects with 'title' and 'link' keys."
            }]
        }

    # Validate target format
    urls_data = []
    for target in targets:
        if isinstance(target, dict) and "link" in target:
            urls_data.append({
                "title": target.get("title", "Unknown"),
                "link": target["link"]
            })
        elif isinstance(target, str):
            # If just a URL string was passed
            urls_data.append({
                "title": "Unknown",
                "link": target
            })

    if not urls_data:
        return {
            "content": [{
                "type": "text",
                "text": "Invalid target format. Provide a list of objects with 'title' and 'link' keys, or a list of URL strings."
            }]
        }

    # Run synchronous scraping in executor
    loop = asyncio.get_running_loop()
    try:
        results = await loop.run_in_executor(
            None,
            lambda: scrape_multiple(urls_data, max_workers=max_workers)
        )
    except Exception as e:
        return {
            "content": [{
                "type": "text",
                "text": f"Scraping failed: {str(e)}. Some .onion sites may be offline."
            }]
        }

    if not results:
        return {
            "content": [{
                "type": "text",
                "text": "Failed to scrape any content. The .onion sites may be offline or blocking requests."
            }]
        }

    # Format scraped content
    content_parts = []
    success_count = 0
    for url, content in results.items():
        if content and len(content) > 50:  # Meaningful content
            success_count += 1
            # Truncate very long content
            display_content = content[:2000] + "..." if len(content) > 2000 else content
            content_parts.append(f"## Source: {url}\n\n{display_content}\n\n---")
        else:
            content_parts.append(f"## Source: {url}\n\n*[Minimal or no content extracted]*\n\n---")

    result_text = f"Successfully scraped **{success_count}/{len(urls_data)}** pages.\n\n"
    result_text += "\n".join(content_parts)
    result_text += "\n\n**Next step**: Analyze this content for intelligence artifacts and generate your findings report."

    return {
        "content": [{
            "type": "text",
            "text": result_text
        }]
    }


@tool(
    "save_report",
    "Save the investigation report to a markdown file. Use this when the user asks to save or export the findings.",
    {
        "content": str,
        "filename": str,
    }
)
async def save_report(args: dict[str, Any]) -> dict[str, Any]:
    """
    Save the final report to a markdown file.
    """
    content = args["content"]
    filename = args.get("filename", "")

    if not filename:
        now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"robin_report_{now}.md"

    if not filename.endswith(".md"):
        filename += ".md"

    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)

        return {
            "content": [{
                "type": "text",
                "text": f"Report saved successfully to **{filename}**"
            }]
        }
    except Exception as e:
        return {
            "content": [{
                "type": "text",
                "text": f"Failed to save report: {str(e)}"
            }]
        }


@tool(
    "delegate_analysis",
    """Delegate specialized analysis to expert sub-agents. Available agents:
- ThreatActorProfiler: Profiles threat actors, APT groups, cybercriminals
- IOCExtractor: Extracts IPs, domains, hashes, emails, crypto addresses
- MalwareAnalyst: Analyzes malware, ransomware, exploits
- MarketplaceInvestigator: Investigates dark web markets and vendors

You can delegate to multiple agents simultaneously for comprehensive analysis.""",
    {
        "agent_types": list,
        "content": str,
        "context": str,
    }
)
async def delegate_analysis(args: dict[str, Any]) -> dict[str, Any]:
    """
    Delegate analysis to specialized sub-agents.

    Args:
        agent_types: List of agent types to run (e.g., ["IOCExtractor", "MalwareAnalyst"])
        content: The scraped content to analyze
        context: Additional context (original query, investigation goals)
    """
    agent_types = args["agent_types"]
    content = args["content"]
    context = args.get("context", "")

    if not agent_types:
        available = get_available_subagents()
        agent_list = "\n".join([f"- **{k}**: {v}" for k, v in available.items()])
        return {
            "content": [{
                "type": "text",
                "text": f"No agents specified. Available sub-agents:\n\n{agent_list}"
            }]
        }

    # Validate agent types
    available = get_available_subagents()
    invalid = [a for a in agent_types if a not in available]
    if invalid:
        return {
            "content": [{
                "type": "text",
                "text": f"Invalid agent types: {invalid}. Valid types: {list(available.keys())}"
            }]
        }

    if not content:
        return {
            "content": [{
                "type": "text",
                "text": "No content provided for analysis. Please include the scraped content to analyze."
            }]
        }

    # Run sub-agents in parallel
    try:
        results = await run_subagents_parallel(agent_types, content, context)
    except Exception as e:
        return {
            "content": [{
                "type": "text",
                "text": f"Sub-agent execution failed: {str(e)}"
            }]
        }

    # Format results
    output_parts = [f"## Sub-Agent Analysis Results\n\nDelegated to: {', '.join(agent_types)}\n"]

    for result in results:
        if result.success:
            output_parts.append(f"### {result.agent_type}\n\n{result.analysis}\n")
        else:
            output_parts.append(f"### {result.agent_type}\n\n*Analysis failed: {result.error}*\n")

    output_parts.append("---\n\n**Next step**: Synthesize these findings into your final report.")

    return {
        "content": [{
            "type": "text",
            "text": "\n".join(output_parts)
        }]
    }
