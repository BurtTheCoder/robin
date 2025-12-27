"""Tests for sub-agent classes."""
import pytest

from agent.subagents import (
    SubAgent,
    SubAgentResult,
    ThreatActorProfiler,
    IOCExtractor,
    MalwareAnalyst,
    MarketplaceInvestigator,
    get_available_subagents,
)
from agent.prompts import SUBAGENT_PROMPTS, SUBAGENT_DESCRIPTIONS


class TestSubAgentResult:
    """Tests for SubAgentResult dataclass."""

    def test_success_result(self):
        """Test successful result creation."""
        result = SubAgentResult(
            agent_type="IOCExtractor",
            analysis="Found 5 IP addresses",
            success=True,
        )
        assert result.agent_type == "IOCExtractor"
        assert result.analysis == "Found 5 IP addresses"
        assert result.success is True
        assert result.error is None

    def test_failure_result(self):
        """Test failed result creation."""
        result = SubAgentResult(
            agent_type="MalwareAnalyst",
            analysis="",
            success=False,
            error="API timeout",
        )
        assert result.success is False
        assert result.error == "API timeout"


class TestSubAgentBase:
    """Tests for SubAgent base class."""

    def test_valid_agent_type(self):
        """Valid agent types should initialize successfully."""
        for agent_type in SUBAGENT_PROMPTS.keys():
            agent = SubAgent(agent_type)
            assert agent.agent_type == agent_type
            assert agent.system_prompt == SUBAGENT_PROMPTS[agent_type]
            assert agent.description == SUBAGENT_DESCRIPTIONS[agent_type]

    def test_invalid_agent_type(self):
        """Invalid agent types should raise ValueError."""
        with pytest.raises(ValueError) as exc_info:
            SubAgent("InvalidAgent")
        assert "Unknown agent type" in str(exc_info.value)

    def test_custom_model(self):
        """Custom model should be set correctly."""
        agent = SubAgent("IOCExtractor", model="claude-opus-4-5-20250514")
        assert agent.model == "claude-opus-4-5-20250514"


class TestSpecializedAgents:
    """Tests for specialized sub-agent classes."""

    def test_threat_actor_profiler(self):
        """ThreatActorProfiler should initialize correctly."""
        agent = ThreatActorProfiler()
        assert agent.agent_type == "ThreatActorProfiler"
        assert "threat actor" in agent.system_prompt.lower()

    def test_ioc_extractor(self):
        """IOCExtractor should initialize correctly."""
        agent = IOCExtractor()
        assert agent.agent_type == "IOCExtractor"
        assert "ioc" in agent.system_prompt.lower()

    def test_malware_analyst(self):
        """MalwareAnalyst should initialize correctly."""
        agent = MalwareAnalyst()
        assert agent.agent_type == "MalwareAnalyst"
        assert "malware" in agent.system_prompt.lower()

    def test_marketplace_investigator(self):
        """MarketplaceInvestigator should initialize correctly."""
        agent = MarketplaceInvestigator()
        assert agent.agent_type == "MarketplaceInvestigator"
        assert "marketplace" in agent.system_prompt.lower()

    def test_all_have_analyze_method(self):
        """All specialized agents should have analyze method."""
        agents = [
            ThreatActorProfiler(),
            IOCExtractor(),
            MalwareAnalyst(),
            MarketplaceInvestigator(),
        ]
        for agent in agents:
            assert hasattr(agent, "analyze")
            assert callable(agent.analyze)


class TestGetAvailableSubagents:
    """Tests for get_available_subagents function."""

    def test_returns_all_agents(self):
        """Should return all available sub-agents."""
        available = get_available_subagents()
        expected = {
            "ThreatActorProfiler",
            "IOCExtractor",
            "MalwareAnalyst",
            "MarketplaceInvestigator",
        }
        assert set(available.keys()) == expected

    def test_returns_copy(self):
        """Should return a copy, not the original dict."""
        available1 = get_available_subagents()
        available2 = get_available_subagents()
        available1["Test"] = "test"
        assert "Test" not in available2
