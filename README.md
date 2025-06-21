# Financial Datasets MCP Server

Model Context Protocol (MCP) server providing stock market and crypto data from [Financial Datasets](https://www.financialdatasets.ai/).

## Features

- Income statements, balance sheets, cash flow statements
- Current and historical stock/crypto prices
- Company news and SEC filings
- Available crypto tickers

## Quick Start

### Docker (Recommended)

1. Copy and configure environment variables:
   ```bash
   cp .env.example .env
   # Edit .env and set your FINANCIAL_DATASETS_API_KEY
   ```

2. Run with Docker Compose:
   ```bash
   docker-compose up -d
   ```

3. For HTTP mode, set `MCP_TRANSPORT=sse` in `.env` and access: `http://localhost:8000`

### Native Installation

1. Install dependencies:
   ```bash
   uv sync
   ```

2. Set API key in `.env` file and run:
   ```bash
   uv run server.py
   ```

## Claude Desktop Integration

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "financial-datasets": {
      "command": "uv",
      "args": ["--directory", "/path/to/this/project", "run", "server.py"]
    }
  }
}
```

Replace `/path/to/this/project` with the absolute path to this directory.
