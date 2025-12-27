"""Robin Agent client using Claude Agent SDK."""
import asyncio
from dataclasses import dataclass, field
from typing import Any, AsyncIterator, Callable, Optional

from claude_code_sdk import (
    query,
    ClaudeCodeOptions,
    AssistantMessage,
    ResultMessage,
    TextBlock,
    ToolUseBlock,
    tool,
    create_sdk_mcp_server,
)

from .prompts import ROBIN_SYSTEM_PROMPT
from .tools import darkweb_search, darkweb_scrape, save_report, delegate_analysis
from config import DEFAULT_MODEL, MAX_AGENT_TURNS


@dataclass
class InvestigationResult:
    """Result of an investigation query."""
    text: str
    session_id: Optional[str] = None
    duration_ms: Optional[int] = None
    num_turns: Optional[int] = None
    tools_used: list = field(default_factory=list)


class RobinAgent:
    """
    Autonomous dark web OSINT agent with session management.

    Wraps the Claude Agent SDK to provide:
    - Dark web search and scraping via custom tools
    - Session continuity for conversational follow-ups
    - Streaming responses with callbacks
    """

    def __init__(
        self,
        on_text: Optional[Callable[[str], None]] = None,
        on_tool_use: Optional[Callable[[str, dict], None]] = None,
        on_complete: Optional[Callable[[InvestigationResult], None]] = None,
        model: Optional[str] = None,
    ):
        """
        Initialize RobinAgent.

        Args:
            on_text: Callback for streaming text chunks
            on_tool_use: Callback when a tool is invoked
            on_complete: Callback when investigation completes
            model: Claude model to use (default from config)
        """
        self.on_text = on_text
        self.on_tool_use = on_tool_use
        self.on_complete = on_complete
        self.model = model or DEFAULT_MODEL
        self.session_id: Optional[str] = None
        self._tools_used: list = []
        self._mcp_server = None

    def _get_mcp_server(self):
        """Create MCP server with custom tools (lazy initialization)."""
        if self._mcp_server is None:
            self._mcp_server = create_sdk_mcp_server(
                name="robin",
                version="1.0.0",
                tools=[darkweb_search, darkweb_scrape, save_report, delegate_analysis]
            )
        return self._mcp_server

    def _build_options(self) -> ClaudeCodeOptions:
        """Build ClaudeCodeOptions with custom tools."""
        mcp_server = self._get_mcp_server()

        options = ClaudeCodeOptions(
            system_prompt=ROBIN_SYSTEM_PROMPT,
            model=self.model,
            max_turns=MAX_AGENT_TURNS,
            mcp_servers={"robin": mcp_server},
            allowed_tools=[
                "mcp__robin__darkweb_search",
                "mcp__robin__darkweb_scrape",
                "mcp__robin__save_report",
                "mcp__robin__delegate_analysis",
            ],
            permission_mode="acceptEdits",
        )

        # Handle session resumption
        if self.session_id:
            options.resume = self.session_id

        return options

    async def investigate(
        self,
        query_text: str,
        stream: bool = True,
    ) -> AsyncIterator[str]:
        """
        Run an OSINT investigation query.

        The agent autonomously decides:
        - How to refine the query
        - Which search engines to use
        - Which results to scrape
        - How to analyze findings

        Args:
            query_text: The investigation query (e.g., "ransomware payments 2024")
            stream: Whether to stream responses (default True)

        Yields:
            Text chunks as they arrive (if streaming)
        """
        self._tools_used = []
        full_response = ""

        options = self._build_options()

        async for message in query(prompt=query_text, options=options):
            # Check for session ID in init message
            if hasattr(message, 'subtype') and message.subtype == 'init':
                if hasattr(message, 'data') and message.data:
                    self.session_id = message.data.get('session_id')
                continue

            if isinstance(message, AssistantMessage):
                # Process assistant message content blocks
                for block in message.content:
                    if isinstance(block, TextBlock):
                        text = block.text
                        full_response += text
                        if self.on_text:
                            self.on_text(text)
                        if stream:
                            yield text
                    elif isinstance(block, ToolUseBlock):
                        tool_name = block.name
                        tool_input = block.input
                        self._tools_used.append({
                            "name": tool_name,
                            "input": tool_input
                        })
                        if self.on_tool_use:
                            self.on_tool_use(tool_name, tool_input)

            elif isinstance(message, ResultMessage):
                # End of response - capture final result
                if hasattr(message, 'result') and message.result:
                    result_text = message.result
                    if result_text and result_text not in full_response:
                        full_response += result_text
                        if self.on_text:
                            self.on_text(result_text)
                        if stream:
                            yield result_text

                result = InvestigationResult(
                    text=full_response,
                    session_id=self.session_id,
                    duration_ms=getattr(message, 'duration_ms', None),
                    num_turns=getattr(message, 'num_turns', None),
                    tools_used=self._tools_used.copy(),
                )

                if self.on_complete:
                    self.on_complete(result)

        if not stream:
            yield full_response

    async def follow_up(self, query_text: str) -> AsyncIterator[str]:
        """
        Send a follow-up query in the same session.

        Claude remembers all previous context from the investigation.

        Examples:
            - "dig deeper into result #3"
            - "search for more about that threat actor"
            - "save the report"

        Args:
            query_text: Follow-up query

        Yields:
            Text responses from Claude
        """
        # Session ID is automatically used via _build_options()
        async for chunk in self.investigate(query_text):
            yield chunk

    def reset_session(self) -> None:
        """Clear the current session to start fresh."""
        self.session_id = None
        self._tools_used = []


async def run_investigation(
    query_text: str,
    on_text: Optional[Callable[[str], None]] = None,
    on_tool_use: Optional[Callable[[str, dict], None]] = None,
) -> InvestigationResult:
    """
    Convenience function to run a one-shot investigation.

    Args:
        query_text: The investigation query
        on_text: Optional streaming text callback
        on_tool_use: Optional tool use callback

    Returns:
        InvestigationResult with full response and metadata
    """
    result_holder = []

    def capture_result(result: InvestigationResult):
        result_holder.append(result)

    agent = RobinAgent(
        on_text=on_text,
        on_tool_use=on_tool_use,
        on_complete=capture_result,
    )

    full_text = ""
    async for chunk in agent.investigate(query_text):
        full_text += chunk

    if result_holder:
        return result_holder[0]
    else:
        return InvestigationResult(text=full_text)
