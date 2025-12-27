"""Tests for RobinAgent client."""
import pytest
from unittest.mock import patch, MagicMock, AsyncMock

from agent.client import RobinAgent, InvestigationResult, run_investigation
from config import DEFAULT_MODEL


class TestInvestigationResult:
    """Tests for InvestigationResult dataclass."""

    def test_minimal_result(self):
        """Should create result with just text."""
        result = InvestigationResult(text="Investigation complete")
        assert result.text == "Investigation complete"
        assert result.session_id is None
        assert result.duration_ms is None
        assert result.num_turns is None
        assert result.tools_used == []

    def test_full_result(self):
        """Should create result with all fields."""
        result = InvestigationResult(
            text="Full report here",
            session_id="abc123",
            duration_ms=5000,
            num_turns=3,
            tools_used=[{"name": "darkweb_search", "input": {"query": "test"}}],
        )
        assert result.session_id == "abc123"
        assert result.duration_ms == 5000
        assert result.num_turns == 3
        assert len(result.tools_used) == 1


class TestRobinAgent:
    """Tests for RobinAgent class."""

    def test_initialization_defaults(self):
        """Should initialize with defaults."""
        agent = RobinAgent()
        assert agent.model == DEFAULT_MODEL
        assert agent.session_id is None
        assert agent.on_text is None
        assert agent.on_tool_use is None
        assert agent.on_complete is None

    def test_initialization_custom_callbacks(self):
        """Should accept custom callbacks."""
        on_text = MagicMock()
        on_tool_use = MagicMock()
        on_complete = MagicMock()

        agent = RobinAgent(
            on_text=on_text,
            on_tool_use=on_tool_use,
            on_complete=on_complete,
        )
        assert agent.on_text is on_text
        assert agent.on_tool_use is on_tool_use
        assert agent.on_complete is on_complete

    def test_initialization_custom_model(self):
        """Should accept custom model."""
        agent = RobinAgent(model="claude-opus-4-5-20250514")
        assert agent.model == "claude-opus-4-5-20250514"

    def test_reset_session(self):
        """Should clear session state."""
        agent = RobinAgent()
        agent.session_id = "test-session"
        agent._tools_used = [{"name": "test"}]

        agent.reset_session()

        assert agent.session_id is None
        assert agent._tools_used == []

    def test_mcp_server_lazy_initialization(self):
        """MCP server should be lazily initialized."""
        agent = RobinAgent()
        assert agent._mcp_server is None

        # First call creates server
        server1 = agent._get_mcp_server()
        assert agent._mcp_server is not None

        # Second call returns same server
        server2 = agent._get_mcp_server()
        assert server1 is server2

    def test_build_options_without_session(self):
        """Should build options without session resume."""
        agent = RobinAgent()
        options = agent._build_options()

        assert options.model == agent.model
        assert options.max_turns > 0
        assert "mcp__robin__darkweb_search" in options.allowed_tools
        assert "mcp__robin__darkweb_scrape" in options.allowed_tools
        assert "mcp__robin__save_report" in options.allowed_tools
        assert "mcp__robin__delegate_analysis" in options.allowed_tools

    def test_build_options_with_session(self):
        """Should include session resume when session exists."""
        agent = RobinAgent()
        agent.session_id = "existing-session-id"
        options = agent._build_options()

        assert options.resume == "existing-session-id"


class TestRunInvestigation:
    """Tests for run_investigation convenience function."""

    def test_function_signature(self):
        """Should accept expected parameters."""
        import inspect
        sig = inspect.signature(run_investigation)
        params = list(sig.parameters.keys())
        assert "query_text" in params
        assert "on_text" in params
        assert "on_tool_use" in params
