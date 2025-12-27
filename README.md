<div align="center">
   <img src=".github/assets/logo.png" alt="Logo" width="300">
   <br><a href="https://github.com/apurvsinghgautam/robin/actions/workflows/binary.yml"><img alt="Build" src="https://github.com/apurvsinghgautam/robin/actions/workflows/binary.yml/badge.svg"></a> <a href="https://github.com/apurvsinghgautam/robin/releases"><img alt="GitHub Release" src="https://img.shields.io/github/v/release/apurvsinghgautam/robin"></a> <a href="https://hub.docker.com/r/apurvsg/robin"><img alt="Docker Pulls" src="https://img.shields.io/docker/pulls/apurvsg/robin"></a>
   <h1>Robin: AI-Powered Dark Web OSINT Tool</h1>

   <p>Robin is an autonomous AI agent for conducting dark web OSINT investigations. Built with the Claude Agent SDK, it uses specialized sub-agents to search, scrape, and analyze dark web content through Tor.</p>
   <a href="#installation">Installation</a> &bull; <a href="#usage">Usage</a> &bull; <a href="#architecture">Architecture</a> &bull; <a href="#contributing">Contributing</a><br><br>
</div>

![Demo](.github/assets/screen.png)
![Demo](.github/assets/screen-ui.png)

---

## Features

- **Autonomous Investigation** - Claude decides when to search, which results to scrape, and how to analyze
- **Multi-Agent Architecture** - Specialized sub-agents for threat actors, IOCs, malware, and marketplaces
- **Conversational Follow-ups** - Ask follow-up questions within the same session
- **17 Dark Web Search Engines** - Concurrent searches across multiple .onion search engines
- **Streamlit Chat UI** - Interactive web interface with streaming responses
- **CLI & Interactive Modes** - Terminal-first design with optional interactive sessions
- **Session Continuity** - Resume investigations with full context preserved

---

## Architecture

Robin uses a coordinator-subagent pattern powered by Claude Agent SDK:

```
┌─────────────────────────────────────────────────────────────┐
│                    RobinAgent (Coordinator)                  │
│                                                             │
│  Tools:                                                     │
│  • darkweb_search - Search 17 .onion search engines         │
│  • darkweb_scrape - Extract content from .onion URLs        │
│  • save_report - Export findings to markdown                │
│  • delegate_analysis - Invoke specialized sub-agents        │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Specialized Sub-Agents                    │
├─────────────────┬─────────────────┬─────────────────────────┤
│ ThreatActor     │ IOCExtractor    │ MalwareAnalyst          │
│ Profiler        │                 │                         │
│                 │                 │                         │
│ Profiles APT    │ Extracts IPs,   │ Analyzes malware        │
│ groups, threat  │ domains, hashes,│ families, capabilities, │
│ actors, TTPs    │ crypto wallets  │ and mitigations         │
├─────────────────┴─────────────────┴─────────────────────────┤
│                 MarketplaceInvestigator                      │
│                                                             │
│     Investigates dark web markets, vendors, pricing         │
└─────────────────────────────────────────────────────────────┘
```

---

## Disclaimer

> This tool is intended for educational and lawful investigative purposes only. Accessing or interacting with certain dark web content may be illegal depending on your jurisdiction. The author is not responsible for any misuse of this tool or the data gathered using it.
>
> Use responsibly and at your own risk. Ensure you comply with all relevant laws and institutional policies before conducting OSINT investigations.

---

## Installation

### Prerequisites

1. **Tor** - Required for dark web access
   ```bash
   # Linux/WSL
   apt install tor

   # macOS
   brew install tor
   ```
   Ensure Tor is running: `systemctl status tor` or check port 9050

2. **Anthropic API Key** - Set in environment or `.env` file
   ```bash
   export ANTHROPIC_API_KEY="your-key-here"
   ```

### Install from Source

```bash
# Clone repository
git clone https://github.com/apurvsinghgautam/robin.git
cd robin

# Install dependencies
pip install -r requirements.txt

# Run CLI
python main.py cli -q "ransomware payments 2024"

# Or run Web UI
python main.py ui
```

### Docker (Web UI)

```bash
docker pull apurvsg/robin:latest

docker run --rm \
   -e ANTHROPIC_API_KEY="your-key" \
   -p 8501:8501 \
   apurvsg/robin:latest ui --ui-port 8501 --ui-host 0.0.0.0
```

---

## Usage

### CLI Mode

```bash
# Basic investigation
python main.py cli -q "ransomware payments 2024"

# Interactive mode (follow-up questions)
python main.py cli -q "APT28 infrastructure" --interactive

# Custom output file
python main.py cli -q "credential dumps" -o my_report.md

# Custom model
python main.py cli -q "zero day exploits" -m claude-opus-4-5-20250514
```

### Web UI Mode

```bash
python main.py ui

# Custom port
python main.py ui --ui-port 8080
```

Open `http://localhost:8501` for the chat interface.

### CLI Options

```
Robin: AI-Powered Dark Web OSINT Agent

Commands:
  cli  Run investigation from command line
  ui   Launch Streamlit web interface

CLI Options:
  -q, --query TEXT     Investigation query (required)
  -o, --output TEXT    Output filename for report
  -i, --interactive    Enable follow-up questions
  -m, --model TEXT     Claude model to use (default: claude-sonnet-4-5-20250514)
  -h, --help           Show help message

Examples:
  python main.py cli -q "ransomware payments"
  python main.py cli -q "threat actor APT28" --interactive
  python main.py cli -q "dark web marketplaces" -o report.md
  python main.py ui --ui-port 8080
```

### Python API

```python
import asyncio
from agent import RobinAgent, run_investigation

# Simple one-shot investigation
async def main():
    result = await run_investigation("ransomware payments 2024")
    print(result.text)

asyncio.run(main())

# Or with callbacks and session management
agent = RobinAgent(
    on_text=lambda t: print(t, end=""),
    on_tool_use=lambda name, args: print(f"\n[Tool: {name}]"),
)

async def interactive():
    async for chunk in agent.investigate("APT28"):
        pass  # Streaming handled by callback

    # Follow-up in same session
    async for chunk in agent.follow_up("What malware do they use?"):
        pass

asyncio.run(interactive())
```

---

## Configuration

Environment variables (or `.env` file):

| Variable | Description | Default |
|----------|-------------|---------|
| `ANTHROPIC_API_KEY` | Anthropic API key | Required |
| `TOR_SOCKS_PROXY` | Tor SOCKS5 proxy URL | `socks5h://127.0.0.1:9050` |
| `ROBIN_MODEL` | Claude model to use | `claude-sonnet-4-5-20250514` |
| `MAX_AGENT_TURNS` | Max agent reasoning turns | `20` |
| `MAX_SEARCH_WORKERS` | Concurrent search threads | `5` |
| `MAX_SCRAPE_WORKERS` | Concurrent scrape threads | `5` |

---

## Project Structure

```
robin/
├── agent/
│   ├── __init__.py       # Module exports
│   ├── client.py         # RobinAgent with session management
│   ├── tools.py          # Custom MCP tools
│   ├── prompts.py        # System prompts for all agents
│   └── subagents.py      # Specialized sub-agent classes
├── core/
│   ├── search.py         # Dark web search engine integration
│   └── scrape.py         # Tor-based content scraping
├── tests/
│   ├── test_client.py    # Agent client tests
│   ├── test_tools.py     # Tool function tests
│   ├── test_subagents.py # Sub-agent tests
│   └── test_prompts.py   # Prompt validation tests
├── config.py             # Configuration management
├── main.py               # CLI entry point
├── ui.py                 # Streamlit web interface
└── requirements.txt      # Python dependencies
```

---

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=agent --cov-report=html

# Run specific test file
pytest tests/test_tools.py -v
```

---

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Run tests (`pytest tests/ -v`)
4. Commit your changes (`git commit -m 'Add some amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

---

## Acknowledgements

- Idea inspiration from [Thomas Roccia](https://x.com/fr0gger_) and his demo of [Perplexity of the Dark Web](https://x.com/fr0gger_/status/1908051083068645558)
- Tools inspiration from [OSINT Tools for the Dark Web](https://github.com/apurvsinghgautam/dark-web-osint-tools) repository
- LLM Prompt inspiration from [OSINT-Assistant](https://github.com/AXRoux/OSINT-Assistant) repository
- Logo Design by [Tanishq Rupaal](https://github.com/Tanq16/)
- Workflow Design by [Chintan Gurjar](https://www.linkedin.com/in/chintangurjar)
