"""Tests for agent prompts."""
import pytest

from agent.prompts import (
    ROBIN_SYSTEM_PROMPT,
    SUBAGENT_PROMPTS,
    SUBAGENT_DESCRIPTIONS,
    THREAT_ACTOR_PROFILER_PROMPT,
    IOC_EXTRACTOR_PROMPT,
    MALWARE_ANALYST_PROMPT,
    MARKETPLACE_INVESTIGATOR_PROMPT,
)


class TestMainAgentPrompt:
    """Tests for the main Robin agent prompt."""

    def test_system_prompt_exists(self):
        """Main system prompt should exist and be non-empty."""
        assert ROBIN_SYSTEM_PROMPT
        assert len(ROBIN_SYSTEM_PROMPT) > 100

    def test_system_prompt_mentions_tools(self):
        """System prompt should document available tools."""
        assert "darkweb_search" in ROBIN_SYSTEM_PROMPT
        assert "darkweb_scrape" in ROBIN_SYSTEM_PROMPT
        assert "save_report" in ROBIN_SYSTEM_PROMPT
        assert "delegate_analysis" in ROBIN_SYSTEM_PROMPT

    def test_system_prompt_mentions_subagents(self):
        """System prompt should document sub-agents."""
        assert "ThreatActorProfiler" in ROBIN_SYSTEM_PROMPT
        assert "IOCExtractor" in ROBIN_SYSTEM_PROMPT
        assert "MalwareAnalyst" in ROBIN_SYSTEM_PROMPT
        assert "MarketplaceInvestigator" in ROBIN_SYSTEM_PROMPT

    def test_system_prompt_has_protocol(self):
        """System prompt should include investigation protocol."""
        assert "Investigation Protocol" in ROBIN_SYSTEM_PROMPT
        assert "Output Format" in ROBIN_SYSTEM_PROMPT


class TestSubAgentPrompts:
    """Tests for sub-agent prompts."""

    def test_all_subagent_prompts_exist(self):
        """All sub-agent prompts should be defined."""
        expected_agents = [
            "ThreatActorProfiler",
            "IOCExtractor",
            "MalwareAnalyst",
            "MarketplaceInvestigator",
        ]
        for agent in expected_agents:
            assert agent in SUBAGENT_PROMPTS
            assert SUBAGENT_PROMPTS[agent]
            assert len(SUBAGENT_PROMPTS[agent]) > 100

    def test_all_subagent_descriptions_exist(self):
        """All sub-agent descriptions should be defined."""
        expected_agents = [
            "ThreatActorProfiler",
            "IOCExtractor",
            "MalwareAnalyst",
            "MarketplaceInvestigator",
        ]
        for agent in expected_agents:
            assert agent in SUBAGENT_DESCRIPTIONS
            assert SUBAGENT_DESCRIPTIONS[agent]

    def test_prompts_and_descriptions_match(self):
        """Prompt keys should match description keys."""
        assert set(SUBAGENT_PROMPTS.keys()) == set(SUBAGENT_DESCRIPTIONS.keys())

    def test_threat_actor_profiler_prompt(self):
        """ThreatActorProfiler prompt should include key sections."""
        prompt = THREAT_ACTOR_PROFILER_PROMPT
        assert "Threat Actor" in prompt
        assert "TTPs" in prompt or "Tactics" in prompt
        assert "MITRE ATT&CK" in prompt

    def test_ioc_extractor_prompt(self):
        """IOCExtractor prompt should mention indicator types."""
        prompt = IOC_EXTRACTOR_PROMPT
        assert "IP" in prompt
        assert "hash" in prompt.lower()
        assert "domain" in prompt.lower()
        assert "Bitcoin" in prompt or "crypto" in prompt.lower()

    def test_malware_analyst_prompt(self):
        """MalwareAnalyst prompt should mention key concepts."""
        prompt = MALWARE_ANALYST_PROMPT
        assert "malware" in prompt.lower()
        assert "ransomware" in prompt.lower()
        assert "C2" in prompt or "command" in prompt.lower()

    def test_marketplace_investigator_prompt(self):
        """MarketplaceInvestigator prompt should mention market concepts."""
        prompt = MARKETPLACE_INVESTIGATOR_PROMPT
        assert "marketplace" in prompt.lower() or "market" in prompt.lower()
        assert "vendor" in prompt.lower()
        assert "escrow" in prompt.lower()
