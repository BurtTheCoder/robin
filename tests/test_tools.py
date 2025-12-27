"""Tests for agent tools."""
import pytest
from unittest.mock import patch, MagicMock


class TestToolDefinitions:
    """Tests for tool definitions and metadata."""

    def test_darkweb_search_exists(self):
        """darkweb_search tool should be defined."""
        from agent.tools import darkweb_search
        assert darkweb_search is not None
        # Check it's an SDK tool object
        assert hasattr(darkweb_search, 'name') or hasattr(darkweb_search, '__name__')

    def test_darkweb_scrape_exists(self):
        """darkweb_scrape tool should be defined."""
        from agent.tools import darkweb_scrape
        assert darkweb_scrape is not None

    def test_save_report_exists(self):
        """save_report tool should be defined."""
        from agent.tools import save_report
        assert save_report is not None

    def test_delegate_analysis_exists(self):
        """delegate_analysis tool should be defined."""
        from agent.tools import delegate_analysis
        assert delegate_analysis is not None


class TestSearchLogic:
    """Tests for search-related logic."""

    def test_get_search_results_import(self):
        """Should be able to import search function."""
        from core.search import get_search_results
        assert callable(get_search_results)


class TestScrapeLogic:
    """Tests for scrape-related logic."""

    def test_scrape_multiple_import(self):
        """Should be able to import scrape function."""
        from core.scrape import scrape_multiple
        assert callable(scrape_multiple)


class TestSubagentOrchestration:
    """Tests for sub-agent orchestration in delegate_analysis."""

    def test_get_available_subagents(self):
        """Should return available sub-agents."""
        from agent.subagents import get_available_subagents
        available = get_available_subagents()
        assert "ThreatActorProfiler" in available
        assert "IOCExtractor" in available
        assert "MalwareAnalyst" in available
        assert "MarketplaceInvestigator" in available

    def test_run_subagent_import(self):
        """Should be able to import run_subagent."""
        from agent.subagents import run_subagent
        assert callable(run_subagent)

    def test_run_subagents_parallel_import(self):
        """Should be able to import run_subagents_parallel."""
        from agent.subagents import run_subagents_parallel
        assert callable(run_subagents_parallel)


class TestToolModuleExports:
    """Tests for module-level exports."""

    def test_all_tools_exported(self):
        """All tools should be exported from agent module."""
        from agent import darkweb_search, darkweb_scrape, save_report, delegate_analysis
        assert darkweb_search is not None
        assert darkweb_scrape is not None
        assert save_report is not None
        assert delegate_analysis is not None

    def test_tools_in_all(self):
        """Tools should be in __all__."""
        from agent import __all__
        assert "darkweb_search" in __all__
        assert "darkweb_scrape" in __all__
        assert "save_report" in __all__
        assert "delegate_analysis" in __all__
