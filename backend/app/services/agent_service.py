"""Agent service wrapping RobinAgent for API use."""
import asyncio
import sys
import time
from pathlib import Path
from typing import Optional
from uuid import UUID

# Add parent robin directory to path for imports
robin_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(robin_root))

from agent import RobinAgent, InvestigationResult
from ..sse.stream import SSEStreamManager
from ..config import get_settings

settings = get_settings()


class AgentService:
    """
    Wraps RobinAgent to provide API-friendly interface with SSE streaming.

    Converts RobinAgent callbacks into SSE events for real-time frontend updates.
    """

    def __init__(
        self,
        investigation_id: UUID,
        stream_manager: SSEStreamManager,
        model: Optional[str] = None,
    ):
        self.investigation_id = investigation_id
        self.stream = stream_manager
        self.model = model or settings.default_model

        self._current_tool_id: Optional[str] = None
        self._tool_start_time: float = 0
        self._tools_used: list[dict] = []
        self._subagent_results: list[dict] = []
        self._full_response: str = ""
        self._result: Optional[InvestigationResult] = None

        # Create agent with callbacks
        self._agent = RobinAgent(
            on_text=self._on_text,
            on_tool_use=self._on_tool_use,
            on_complete=self._on_complete,
            model=self.model,
        )

    def _on_text(self, text: str) -> None:
        """Callback for streaming text - emit SSE event."""
        self._full_response += text
        # Schedule async emit
        asyncio.create_task(self.stream.emit_text(text))

    def _on_tool_use(self, name: str, input_data: dict) -> None:
        """Callback for tool use - emit SSE event."""
        # End previous tool if still running
        if self._current_tool_id:
            duration = int((time.time() - self._tool_start_time) * 1000)
            asyncio.create_task(
                self.stream.emit_tool_end(
                    self._current_tool_id,
                    self._tools_used[-1]["name"],
                    duration,
                )
            )

        # Start new tool
        self._tool_start_time = time.time()
        self._tools_used.append({"name": name, "input": input_data})

        async def emit_start():
            self._current_tool_id = await self.stream.emit_tool_start(name, input_data)
            # Check for sub-agent delegation
            if name == "mcp__robin__delegate_analysis":
                agent_types = input_data.get("agent_types", [])
                for agent_type in agent_types:
                    await self.stream.emit_subagent_start(agent_type)

        asyncio.create_task(emit_start())

    def _on_complete(self, result: InvestigationResult) -> None:
        """Callback for completion - emit SSE event."""
        self._result = result

        # End any running tool
        if self._current_tool_id:
            duration = int((time.time() - self._tool_start_time) * 1000)
            asyncio.create_task(
                self.stream.emit_tool_end(
                    self._current_tool_id,
                    self._tools_used[-1]["name"] if self._tools_used else "unknown",
                    duration,
                )
            )

        asyncio.create_task(
            self.stream.emit_complete(
                text=result.text,
                session_id=result.session_id,
                duration_ms=result.duration_ms,
                num_turns=result.num_turns,
            )
        )

    async def investigate(self, query: str) -> InvestigationResult:
        """
        Run an investigation and stream results via SSE.

        Args:
            query: The investigation query

        Returns:
            InvestigationResult with full response and metadata
        """
        try:
            async for _ in self._agent.investigate(query):
                # Text is handled by on_text callback
                pass

            return self._result or InvestigationResult(text=self._full_response)

        except Exception as e:
            await self.stream.emit_error(str(e))
            raise

    async def follow_up(self, query: str) -> InvestigationResult:
        """
        Send a follow-up query in the same session.

        Args:
            query: The follow-up query

        Returns:
            InvestigationResult with response
        """
        self._full_response = ""  # Reset for new response

        try:
            async for _ in self._agent.follow_up(query):
                pass

            return self._result or InvestigationResult(text=self._full_response)

        except Exception as e:
            await self.stream.emit_error(str(e))
            raise

    @property
    def session_id(self) -> Optional[str]:
        """Get the current session ID."""
        return self._agent.session_id

    @property
    def tools_used(self) -> list[dict]:
        """Get list of tools used in this investigation."""
        return self._tools_used

    @property
    def full_response(self) -> str:
        """Get the full response text."""
        return self._full_response


# Cache for active agent sessions
_active_agents: dict[str, AgentService] = {}


def get_agent(investigation_id: UUID) -> Optional[AgentService]:
    """Get an active agent by investigation ID."""
    return _active_agents.get(str(investigation_id))


def set_agent(investigation_id: UUID, agent: AgentService) -> None:
    """Store an active agent."""
    _active_agents[str(investigation_id)] = agent


def remove_agent(investigation_id: UUID) -> None:
    """Remove an agent from cache."""
    _active_agents.pop(str(investigation_id), None)
