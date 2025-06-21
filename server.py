import json
import os
import httpx
import logging
import sys
import time
from typing import Dict, Any, Optional
from fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import PlainTextResponse, JSONResponse
from config import config
from cache_manager import CacheManager

# Configure logging to write to stderr
logging.basicConfig(
    level=getattr(logging, config.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger("financial-datasets-mcp")

# Initialize FastMCP server and cache manager
mcp = FastMCP("financial-datasets")
cache = CacheManager(ttl_minutes=config.cache_ttl_minutes)


async def make_request(url: str, use_cache: bool = True) -> Dict[str, Any]:
    """Make a request to the Financial Datasets API with proper error handling and caching."""
    # Check cache first if enabled
    if use_cache:
        cached_data = cache.get(url)
        if cached_data is not None:
            logger.info(f"Cache hit for: {url}")
            return cached_data
    
    headers = {}
    if config.api_key:
        headers["X-API-KEY"] = config.api_key
    else:
        logger.warning("No API key found. Some endpoints may be rate-limited.")

    async with httpx.AsyncClient() as client:
        try:
            logger.info(f"Making request to: {url}")
            response = await client.get(url, headers=headers, timeout=config.default_timeout)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Successfully retrieved data from {url}")
            
            # Cache the successful response if caching is enabled
            if use_cache and "Error" not in data:
                cache.set(url, data)
                logger.debug(f"Cached response for: {url}")
            
            return data
            
        except httpx.HTTPStatusError as e:
            error_msg = f"HTTP {e.response.status_code} error: {e.response.text}"
            logger.error(error_msg)
            return {"Error": error_msg}
        except httpx.TimeoutException:
            error_msg = "Request timeout"
            logger.error(error_msg)
            return {"Error": error_msg}
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            logger.error(error_msg)
            return {"Error": error_msg}

@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request) -> PlainTextResponse:
    """Enhanced health check with API connectivity test and cache status."""
    try:
        # Test API connectivity
        test_url = f"{config.base_url}"
        async with httpx.AsyncClient() as client:
            response = await client.get(test_url, timeout=config.health_check_timeout)
            api_status = "OK" if response.status_code == 200 else "DEGRADED"
    except Exception:
        api_status = "ERROR"
    
    # Get cache statistics
    try:
        cache_stats = cache.stats()
        cache_status = "OK"
    except Exception as e:
        cache_stats = {"error": str(e)}
        cache_status = "ERROR"
    
    health_data = {
        "status": "OK",
        "timestamp": time.time(),
        "api_status": api_status,
        "cache_status": cache_status,
        "cache_stats": cache_stats,
        "version": "0.2.0"
    }
    
    return PlainTextResponse(json.dumps(health_data))

@mcp.tool()
async def get_income_statements(
    ticker: str,
    period: str = "annual",
    limit: int = 4,
) -> str:
    """Get income statements for a company.

    Args:
        ticker: Ticker symbol of the company (e.g. AAPL, GOOGL)
        period: Period of the income statement (e.g. annual, quarterly, ttm)
        limit: Number of income statements to return (default: 4)
    """
    # Fetch data from the API
    url = f"{config.base_url}/financials/income-statements/?ticker={ticker}&period={period}&limit={limit}"
    data = await make_request(url)

    # Check if data is found
    if not data:
        return "Unable to fetch income statements or no income statements found."

    # Extract the income statements
    income_statements = data.get("income_statements", [])

    # Check if income statements are found
    if not income_statements:
        return "Unable to fetch income statements or no income statements found."

    # Stringify the income statements
    return json.dumps(income_statements, indent=2)


@mcp.tool()
async def get_balance_sheets(
    ticker: str,
    period: str = "annual",
    limit: int = 4,
) -> str:
    """Get balance sheets for a company.

    Args:
        ticker: Ticker symbol of the company (e.g. AAPL, GOOGL)
        period: Period of the balance sheet (e.g. annual, quarterly, ttm)
        limit: Number of balance sheets to return (default: 4)
        use_cache: Whether to use cached data if available (default: True)
    """
    # Fetch data from the API
    url = f"{config.base_url}/financials/balance-sheets/?ticker={ticker}&period={period}&limit={limit}"
    data = await make_request(url)

    # Check if data is found
    if not data:
        return "Unable to fetch balance sheets or no balance sheets found."

    # Extract the balance sheets
    balance_sheets = data.get("balance_sheets", [])

    # Check if balance sheets are found
    if not balance_sheets:
        return "Unable to fetch balance sheets or no balance sheets found."

    # Stringify the balance sheets
    return json.dumps(balance_sheets, indent=2)


@mcp.tool()
async def get_cash_flow_statements(
    ticker: str,
    period: str = "annual",
    limit: int = 4,
) -> str:
    """Get cash flow statements for a company.

    Args:
        ticker: Ticker symbol of the company (e.g. AAPL, GOOGL)
        period: Period of the cash flow statement (e.g. annual, quarterly, ttm)
        limit: Number of cash flow statements to return (default: 4)
    """
    # Fetch data from the API
    url = f"{config.base_url}/financials/cash-flow-statements/?ticker={ticker}&period={period}&limit={limit}"
    data = await make_request(url)

    # Check if data is found
    if not data:
        return "Unable to fetch cash flow statements or no cash flow statements found."

    # Extract the cash flow statements
    cash_flow_statements = data.get("cash_flow_statements", [])

    # Check if cash flow statements are found
    if not cash_flow_statements:
        return "Unable to fetch cash flow statements or no cash flow statements found."

    # Stringify the cash flow statements
    return json.dumps(cash_flow_statements, indent=2)


@mcp.tool()
async def get_current_stock_price(ticker: str) -> str:
    """Get the current / latest price of a company.

    Args:
        ticker: Ticker symbol of the company (e.g. AAPL, GOOGL)
        use_cache: Whether to use cached data if available (default: False for real-time data)
    """
    # Fetch data from the API
    url = f"{config.base_url}/prices/snapshot/?ticker={ticker}"
    data = await make_request(url, use_cache=False)

    # Check if data is found
    if not data:
        return "Unable to fetch current price or no current price found."

    # Extract the current price
    snapshot = data.get("snapshot", {})

    # Check if current price is found
    if not snapshot:
        return "Unable to fetch current price or no current price found."

    # Stringify the current price
    return json.dumps(snapshot, indent=2)


@mcp.tool()
async def get_historical_stock_prices(
    ticker: str,
    start_date: str,
    end_date: str,
    interval: str = "day",
    interval_multiplier: int = 1,
) -> str:
    """Gets historical stock prices for a company.

    Args:
        ticker: Ticker symbol of the company (e.g. AAPL, GOOGL)
        start_date: Start date of the price data (e.g. 2020-01-01)
        end_date: End date of the price data (e.g. 2020-12-31)
        interval: Interval of the price data (e.g. minute, hour, day, week, month)
        interval_multiplier: Multiplier of the interval (e.g. 1, 2, 3)
    """
    # Fetch data from the API
    url = f"{config.base_url}/prices/?ticker={ticker}&interval={interval}&interval_multiplier={interval_multiplier}&start_date={start_date}&end_date={end_date}"
    data = await make_request(url)

    # Check if data is found
    if not data:
        return "Unable to fetch prices or no prices found."

    # Extract the prices
    prices = data.get("prices", [])

    # Check if prices are found
    if not prices:
        return "Unable to fetch prices or no prices found."

    # Stringify the prices
    return json.dumps(prices, indent=2)


@mcp.tool()
async def get_company_news(ticker: str) -> str:
    """Get news for a company.

    Args:
        ticker: Ticker symbol of the company (e.g. AAPL, GOOGL)
    """
    # Fetch data from the API
    url = f"{config.base_url}/news/?ticker={ticker}"
    data = await make_request(url)

    # Check if data is found
    if not data:
        return "Unable to fetch news or no news found."

    # Extract the news
    news = data.get("news", [])

    # Check if news are found
    if not news:
        return "Unable to fetch news or no news found."
    return json.dumps(news, indent=2)


@mcp.tool()
async def get_available_crypto_tickers() -> str:
    """
    Gets all available crypto tickers.
    """
    # Fetch data from the API
    url = f"{config.base_url}/crypto/prices/tickers"
    data = await make_request(url)

    # Check if data is found
    if not data:
        return "Unable to fetch available crypto tickers or no available crypto tickers found."

    # Extract the available crypto tickers
    tickers = data.get("tickers", [])

    # Stringify the available crypto tickers
    return json.dumps(tickers, indent=2)


@mcp.tool()
async def get_crypto_prices(
    ticker: str,
    start_date: str,
    end_date: str,
    interval: str = "day",
    interval_multiplier: int = 1,
) -> str:
    """
    Gets historical prices for a crypto currency.
    """
    # Fetch data from the API
    url = f"{config.base_url}/crypto/prices/?ticker={ticker}&interval={interval}&interval_multiplier={interval_multiplier}&start_date={start_date}&end_date={end_date}"
    data = await make_request(url)

    # Check if data is found
    if not data:
        return "Unable to fetch prices or no prices found."

    # Extract the prices
    prices = data.get("prices", [])

    # Check if prices are found
    if not prices:
        return "Unable to fetch prices or no prices found."

    # Stringify the prices
    return json.dumps(prices, indent=2)


@mcp.tool()
async def get_historical_crypto_prices(
    ticker: str,
    start_date: str,
    end_date: str,
    interval: str = "day",
    interval_multiplier: int = 1,
) -> str:
    """Gets historical prices for a crypto currency.

    Args:
        ticker: Ticker symbol of the crypto currency (e.g. BTC-USD). The list of available crypto tickers can be retrieved via the get_available_crypto_tickers tool.
        start_date: Start date of the price data (e.g. 2020-01-01)
        end_date: End date of the price data (e.g. 2020-12-31)
        interval: Interval of the price data (e.g. minute, hour, day, week, month)
        interval_multiplier: Multiplier of the interval (e.g. 1, 2, 3)
    """
    # Fetch data from the API
    url = f"{config.base_url}/crypto/prices/?ticker={ticker}&interval={interval}&interval_multiplier={interval_multiplier}&start_date={start_date}&end_date={end_date}"
    data = await make_request(url)

    # Check if data is found
    if not data:
        return "Unable to fetch prices or no prices found."

    # Extract the prices
    prices = data.get("prices", [])

    # Check if prices are found
    if not prices:
        return "Unable to fetch prices or no prices found."

    # Stringify the prices
    return json.dumps(prices, indent=2)


@mcp.tool()
async def get_current_crypto_price(ticker: str) -> str:
    """Get the current / latest price of a crypto currency.

    Args:
        ticker: Ticker symbol of the crypto currency (e.g. BTC-USD). The list of available crypto tickers can be retrieved via the get_available_crypto_tickers tool.
        use_cache: Whether to use cached data if available (default: False for real-time data)
    """
    # Fetch data from the API
    url = f"{config.base_url}/crypto/prices/snapshot/?ticker={ticker}"
    data = await make_request(url, use_cache=False)

    # Check if data is found
    if not data:
        return "Unable to fetch current price or no current price found."

    # Extract the current price
    snapshot = data.get("snapshot", {})

    # Check if current price is found
    if not snapshot:
        return "Unable to fetch current price or no current price found."

    # Stringify the current price
    return json.dumps(snapshot, indent=2)


@mcp.tool()
async def get_sec_filings(
    ticker: str,
    limit: int = 10,
    filing_type: str | None = None,
) -> str:
    """Get all SEC filings for a company.

    Args:
        ticker: Ticker symbol of the company (e.g. AAPL, GOOGL)
        limit: Number of SEC filings to return (default: 10)
        filing_type: Type of SEC filing (e.g. 10-K, 10-Q, 8-K)
    """
    # Fetch data from the API
    url = f"{config.base_url}/filings/?ticker={ticker}&limit={limit}"
    if filing_type:
        url += f"&filing_type={filing_type}"
 
    # Call the API
    data = await make_request(url)

    # Extract the SEC filings
    filings = data.get("filings", [])

    # Check if SEC filings are found
    if not filings:
        return f"Unable to fetch SEC filings or no SEC filings found."

    # Stringify the SEC filings
    return json.dumps(filings, indent=2)

@mcp.custom_route("/cache/status", methods=["GET"])
async def cache_status(request: Request) -> JSONResponse:
    """Get cache status and statistics."""
    try:
        stats = cache.stats()
        cache_data = {
            "cache_enabled": True,
            "cache_ttl_minutes": config.cache_ttl_minutes,
            "statistics": stats,
            "timestamp": time.time()
        }
        return JSONResponse(cache_data)
    except Exception as e:
        logger.error(f"Error getting cache status: {str(e)}")
        return JSONResponse(
            {"error": f"Failed to get cache status: {str(e)}"}, 
            status_code=500
        )

@mcp.custom_route("/cache/clear", methods=["POST"])
async def cache_clear(request: Request) -> JSONResponse:
    """Clear all cache entries."""
    try:
        cache.clear()
        logger.info("Cache cleared manually via API")
        return JSONResponse({
            "message": "Cache cleared successfully",
            "timestamp": time.time()
        })
    except Exception as e:
        logger.error(f"Error clearing cache: {str(e)}")
        return JSONResponse(
            {"error": f"Failed to clear cache: {str(e)}"}, 
            status_code=500
        )

@mcp.custom_route("/cache/cleanup", methods=["POST"])
async def cache_cleanup(request: Request) -> JSONResponse:
    """Clean up expired cache entries."""
    try:
        expired_count = cache.cleanup_expired()
        logger.info(f"Cache cleanup completed, removed {expired_count} expired entries")
        return JSONResponse({
            "message": f"Cache cleanup completed",
            "expired_entries_removed": expired_count,
            "timestamp": time.time()
        })
    except Exception as e:
        logger.error(f"Error cleaning up cache: {str(e)}")
        return JSONResponse(
            {"error": f"Failed to cleanup cache: {str(e)}"}, 
            status_code=500
        )

if __name__ == "__main__":
    # Log server startup
    logger.info("Starting Financial Datasets MCP Server...")
    logger.info(f"Cache enabled with TTL: {config.cache_ttl_minutes} minutes")
    logger.info(f"Transport type: {config.transport_type}")

    # Initialize and run the server
    if config.transport_type == "streamable-http":
        mcp.run(transport='streamable-http', host=config.host, port=config.port)
    elif config.transport_type == "sse":
        mcp.run(transport='sse', port=config.port)
    else:
        mcp.run(transport="stdio")

    # This line won't be reached during normal operation
    logger.info("Server stopped")
