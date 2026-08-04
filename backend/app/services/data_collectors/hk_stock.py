"""
HK Stock data collector — integrates yfinance + Alpha Vantage.
Based on global-stock-data skill.
"""
import asyncio
from datetime import date, datetime, timedelta
from typing import Optional
import httpx
from loguru import logger


class HKStockCollector:
    """港股数据采集器 — 基于 yfinance + Alpha Vantage"""

    def __init__(self):
        self.client = httpx.AsyncClient(timeout=15.0)
        self.market = "HK"
        self._yf_cache = {}

    def _to_yf_symbol(self, symbol: str) -> str:
        """Ensure HK ticker format (e.g. 0700 → 0700.HK)."""
        symbol = symbol.strip().upper()
        if symbol.endswith(".HK"):
            return symbol
        # Pad to 4 digits for HK stocks
        code = symbol.zfill(4) if symbol.isdigit() else symbol
        return f"{code}.HK"

    async def get_realtime_quote(self, symbol: str) -> dict:
        """Get real-time quote via Yahoo Finance API."""
        yf_sym = self._to_yf_symbol(symbol)
        try:
            import yfinance as yf
            ticker = yf.Ticker(yf_sym)
            info = await asyncio.to_thread(lambda: ticker.info)
            fast_info = await asyncio.to_thread(lambda: ticker.fast_info)
            return {
                "symbol": symbol,
                "name": info.get("longName", info.get("shortName", "")),
                "price": fast_info.get("lastPrice") or info.get("currentPrice"),
                "change_pct": info.get("regularMarketChangePercent"),
                "open": fast_info.get("open") or info.get("regularMarketOpen"),
                "high": fast_info.get("dayHigh") or info.get("regularMarketDayHigh"),
                "low": fast_info.get("dayLow") or info.get("regularMarketDayLow"),
                "pre_close": fast_info.get("previousClose") or info.get("previousClose"),
                "volume": fast_info.get("lastVolume") or info.get("regularMarketVolume"),
                "market_cap": info.get("marketCap"),
                "pe": info.get("trailingPE"),
                "pb": info.get("priceToBook"),
                "currency": info.get("currency", "HKD"),
                "update_time": datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"HK quote error for {symbol}: {e}")
            return {"error": str(e), "symbol": symbol}

    async def get_kline(
        self, symbol: str, period: str = "daily",
        start_date: Optional[str] = None, end_date: Optional[str] = None,
        limit: int = 100,
    ) -> list[dict]:
        """Get K-line data via yfinance."""
        yf_sym = self._to_yf_symbol(symbol)
        interval_map = {"daily": "1d", "weekly": "1wk", "monthly": "1mo"}
        interval = interval_map.get(period, "1d")

        try:
            import yfinance as yf
            ticker = yf.Ticker(yf_sym)
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
            logger.error(f"HK kline error: {e}")
            return []

    async def get_market_overview(self) -> dict:
        """Get HK market overview."""
        indices = {"^HSI": "恒生指数", "^HSCE": "国企指数", "^HSCCI": "红筹指数"}
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
            logger.error(f"HK overview error: {e}")
        return result

    async def search(self, query: str) -> list[dict]:
        """Search HK stocks via Yahoo Finance."""
        try:
            # Basic search via yfinance
            url = f"https://query1.finance.yahoo.com/v1/finance/search?q={query}&quotesCount=10&newsCount=0"
            resp = await self.client.get(url, headers={"User-Agent": "Mozilla/5.0"})
            data = resp.json()
            results = []
            for q in data.get("quotes", []):
                if q.get("exchange") in ("HKG", "HNK"):
                    results.append({
                        "symbol": q.get("symbol", "").replace(".HK", ""),
                        "name": q.get("shortname") or q.get("longname", ""),
                        "market": "HK",
                        "type": q.get("quoteType", ""),
                    })
            return results
        except Exception:
            return []

    async def close(self):
        await self.client.aclose()
