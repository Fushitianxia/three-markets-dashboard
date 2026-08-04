"""
US Stock data collector — integrates yfinance + Finnhub + Alpha Vantage + FRED.
Based on global-stock-data skill (V1.0).
"""
import asyncio
import os
from datetime import date, datetime, timedelta
from typing import Optional
import httpx
from loguru import logger


class USStockCollector:
    """美股数据采集器 — 基于 yfinance + Finnhub + FRED"""

    def __init__(self):
        self.client = httpx.AsyncClient(timeout=15.0)
        self.market = "US"
        self._finnhub_key = os.getenv("FINNHUB_API_KEY", "")
        self._fred_key = os.getenv("FRED_API_KEY", "")

    async def get_realtime_quote(self, symbol: str) -> dict:
        """Get real-time US stock quote via yfinance."""
        try:
            import yfinance as yf
            ticker = yf.Ticker(symbol.upper())
            info = await asyncio.to_thread(lambda: ticker.info)
            return {
                "symbol": symbol.upper(),
                "name": info.get("longName", info.get("shortName", "")),
                "price": info.get("currentPrice") or info.get("regularMarketPrice"),
                "change_pct": info.get("regularMarketChangePercent"),
                "open": info.get("regularMarketOpen"),
                "high": info.get("regularMarketDayHigh"),
                "low": info.get("regularMarketDayLow"),
                "pre_close": info.get("previousClose"),
                "volume": info.get("regularMarketVolume"),
                "market_cap": info.get("marketCap"),
                "pe": info.get("trailingPE"),
                "pb": info.get("priceToBook"),
                "eps": info.get("trailingEps"),
                "dividend_yield": info.get("dividendYield"),
                "sector": info.get("sector"),
                "industry": info.get("industry"),
                "currency": "USD",
                "update_time": datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"US quote error for {symbol}: {e}")
            return {"error": str(e), "symbol": symbol}

    async def get_kline(
        self, symbol: str, period: str = "daily",
        start_date: Optional[str] = None, end_date: Optional[str] = None,
        limit: int = 100,
    ) -> list[dict]:
        """Get US stock K-line data."""
        interval_map = {"daily": "1d", "weekly": "1wk", "monthly": "1mo"}
        interval = interval_map.get(period, "1d")

        try:
            import yfinance as yf
            ticker = yf.Ticker(symbol.upper())
            if not start_date:
                start_date = (date.today() - timedelta(days=365)).isoformat()
            if not end_date:
                end_date = date.today().isoformat()

            df = await asyncio.to_thread(
                lambda: ticker.history(start=start_date, end=end_date, interval=interval)
            )
            if df.empty:
                return []

            klines = []
            for idx, row in df.iterrows():
                klines.append({
                    "date": idx.strftime("%Y-%m-%d") if hasattr(idx, "strftime") else str(idx)[:10],
                    "open": float(row["Open"]),
                    "high": float(row["High"]),
                    "low": float(row["Low"]),
                    "close": float(row["Close"]),
                    "volume": float(row["Volume"]),
                })
            return klines[-limit:]
        except Exception as e:
            logger.error(f"US kline error: {e}")
            return []

    async def get_market_overview(self) -> dict:
        """Get US market overview with major indices."""
        indices = {
            "^GSPC": "标普500", "^DJI": "道琼斯", "^IXIC": "纳斯达克",
            "^RUT": "罗素2000", "^VIX": "VIX恐慌指数",
        }
        result = {"indices": {}, "timestamp": datetime.now().isoformat()}
        try:
            import yfinance as yf
            for code, name in indices.items():
                ticker = yf.Ticker(code)
                info = await asyncio.to_thread(lambda: ticker.info)
                result["indices"][name] = {
                    "price": info.get("regularMarketPrice"),
                    "change_pct": info.get("regularMarketChangePercent"),
                }
        except Exception as e:
            logger.error(f"US overview error: {e}")
        return result

    async def search(self, query: str) -> list[dict]:
        """Search US stocks."""
        try:
            url = f"https://query1.finance.yahoo.com/v1/finance/search?q={query}&quotesCount=10&newsCount=0"
            resp = await self.client.get(url, headers={"User-Agent": "Mozilla/5.0"})
            data = resp.json()
            results = []
            for q in data.get("quotes", []):
                if q.get("exchange") in ("NMS", "NYQ", "ASE", "BTS", "NGM"):
                    results.append({
                        "symbol": q.get("symbol", ""),
                        "name": q.get("shortname") or q.get("longname", ""),
                        "market": "US",
                        "type": q.get("quoteType", ""),
                    })
            return results[:10]
        except Exception:
            return []

    # ======= Fundamentals =======

    async def get_financials(self, symbol: str) -> dict:
        """Get US stock financial statements via yfinance."""
        try:
            import yfinance as yf
            ticker = yf.Ticker(symbol.upper())

            info = await asyncio.to_thread(lambda: ticker.info)
            # Key metrics from FMP if key is set
            key_metrics = {}
            if os.getenv("FMP_API_KEY"):
                fmp_url = f"https://financialmodelingprep.com/api/v3/key-metrics/{symbol}?apikey={os.getenv('FMP_API_KEY')}&limit=1"
                fmp_resp = await self.client.get(fmp_url)
                if fmp_resp.status_code == 200:
                    fmp_data = fmp_resp.json()
                    if fmp_data:
                        key_metrics = fmp_data[0]

            return {
                "symbol": symbol,
                "market_cap": info.get("marketCap"),
                "enterprise_value": info.get("enterpriseValue"),
                "pe_ttm": info.get("trailingPE"),
                "forward_pe": info.get("forwardPE"),
                "peg": info.get("pegRatio"),
                "pb": info.get("priceToBook"),
                "ps": info.get("priceToSales"),
                "ev_ebitda": info.get("enterpriseToEbitda"),
                "roe": info.get("returnOnEquity"),
                "roa": info.get("returnOnAssets"),
                "gross_margin": info.get("grossMargins"),
                "net_margin": info.get("profitMargins"),
                "revenue_growth": info.get("revenueGrowth"),
                "earnings_growth": info.get("earningsGrowth"),
                "debt_to_equity": info.get("debtToEquity"),
                "current_ratio": info.get("currentRatio"),
                "beta": info.get("beta"),
                "short_pct": info.get("shortPercentOfFloat"),
                "dividend_yield": info.get("dividendYield"),
                "fmp_metrics": key_metrics,
            }
        except Exception as e:
            logger.error(f"US financials error: {e}")
            return {"error": str(e)}

    # ======= Analyst Estimates =======

    async def get_analyst_estimates(self, symbol: str) -> dict:
        """Get analyst recommendations and target prices."""
        try:
            import yfinance as yf
            ticker = yf.Ticker(symbol.upper())
            info = await asyncio.to_thread(lambda: ticker.info)
            return {
                "symbol": symbol,
                "recommendation": info.get("recommendationKey"),
                "target_high": info.get("targetHighPrice"),
                "target_low": info.get("targetLowPrice"),
                "target_mean": info.get("targetMeanPrice"),
                "target_median": info.get("targetMedianPrice"),
                "num_analysts": info.get("numberOfAnalystOpinions"),
                "earnings_growth": info.get("earningsGrowth"),
                "revenue_growth": info.get("revenueGrowth"),
                "next_earnings_date": info.get("earningsDate"),
            }
        except Exception as e:
            return {"error": str(e)}

    # ======= Insider Trading =======

    async def get_insider_trades(self, symbol: str) -> list[dict]:
        """Get insider trading data via Finnhub."""
        if not self._finnhub_key:
            return []
        try:
            url = "https://finnhub.io/api/v1/stock/insider-transactions"
            params = {"symbol": symbol, "token": self._finnhub_key}
            resp = await self.client.get(url, params=params)
            data = resp.json().get("data", [])
            trades = []
            for t in data[:20]:
                trades.append({
                    "name": t.get("name"),
                    "share": t.get("share"),
                    "change": t.get("change"),
                    "transaction_date": t.get("transactionDate"),
                    "transaction_type": t.get("transactionCode"),
                })
            return trades
        except Exception:
            return []

    # ======= Macro: FRED Data =======

    async def get_macro_indicators(self) -> dict:
        """Get key US macro indicators via FRED."""
        indicators = {
            "GDP": "GDP 国内生产总值",
            "CPIAUCSL": "CPI 消费者物价指数",
            "UNRATE": "失业率",
            "FEDFUNDS": "联邦基金利率",
            "DGS10": "10年期国债收益率",
            "DXY": "美元指数",
            "T10Y2Y": "10Y-2Y 收益率利差",
            "WTI": "WTI原油",
        }
        result = {}
        if not self._fred_key:
            return {"error": "FRED API key not configured"}

        for series_id, name in indicators.items():
            try:
                url = "https://api.stlouisfed.org/fred/series/observations"
                params = {
                    "series_id": series_id,
                    "api_key": self._fred_key,
                    "file_type": "json",
                    "sort_order": "desc",
                    "limit": 1,
                }
                resp = await self.client.get(url, params=params)
                obs = resp.json().get("observations", [])
                if obs:
                    result[name] = {
                        "value": float(obs[0]["value"]) if obs[0]["value"] != "." else None,
                        "date": obs[0]["date"],
                    }
            except Exception:
                result[name] = {"error": "failed"}
        return result

    async def close(self):
        await self.client.aclose()
