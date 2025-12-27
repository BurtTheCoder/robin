"""Pytest configuration and fixtures."""
import sys
from pathlib import Path

import pytest

# Configure pytest-asyncio
pytest_plugins = ('pytest_asyncio',)

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture
def sample_search_results():
    """Sample dark web search results for testing."""
    return [
        {
            "title": "RansomHub Leaked Data Forum",
            "link": "http://ransomhubxxx.onion/leaks"
        },
        {
            "title": "APT28 Discussion Thread",
            "link": "http://hackforum123.onion/apt28"
        },
        {
            "title": "Credential Dump Marketplace",
            "link": "http://credsmarket.onion/dumps"
        },
    ]


@pytest.fixture
def sample_scraped_content():
    """Sample scraped dark web content for testing."""
    return {
        "http://ransomhubxxx.onion/leaks": """
        RansomHub Leak Site

        Latest victims:
        - Acme Corp (500GB data)
        - Example Inc (200GB data)

        Contact: ransomhub@protonmail.com
        BTC: 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa
        """,
        "http://hackforum123.onion/apt28": """
        APT28 Tools and TTPs Discussion

        Known aliases: Fancy Bear, Sofacy
        Primary targets: Government, Defense

        Recent campaign IOCs:
        - 192.168.1.100
        - malware.evil.com
        - SHA256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
        """,
    }


@pytest.fixture
def sample_ioc_content():
    """Sample content with various IOCs for testing."""
    return """
    Threat Intelligence Report

    Network IOCs:
    - C2 Server: 45.33.32.156
    - Domain: evil-c2.com
    - Onion: http://evilc2xxx.onion

    File IOCs:
    - MD5: d41d8cd98f00b204e9800998ecf8427e
    - SHA256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855

    Contact:
    - Email: threat@actor.com
    - Telegram: @threatactor

    Payment:
    - BTC: 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa
    - ETH: 0x742d35Cc6634C0532925a3b844Bc9e7595f5aB2c

    Vulnerability: CVE-2024-1234
    """


@pytest.fixture
def mock_agent_response():
    """Mock response structure from Claude Agent SDK."""
    return {
        "content": [
            {"type": "text", "text": "Investigation complete. Found 3 relevant results."}
        ],
        "session_id": "test-session-123",
    }
