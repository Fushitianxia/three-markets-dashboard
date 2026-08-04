"""
A-Share data collector — integrates mootdx, Tencent, Eastmoney, THS, iwencai.
Based on a-stock-data skill (V3.1).
"""
import asyncio
import json
from datetime import date, datetime, timedelta
from typing import Optional
import httpx
import pandas as pd
from loguru import logger


class AStockCollector:
    """A股数据采集器 — 覆盖行情/研报/信号/资金面/新闻/基础数据/公告 七层数据"""

    def __init__(self):
        self.client = httpx.AsyncClient(timeout=15.0)
        self.market = "A"

    # ======= Market Data (行情层) =======

    async def get_realtime_quote(self, symbol: str) -> dict:
        """Get real-time quote via Tencent API."""
        code = self._to_tencent_code(symbol)
        url = f"https://qt.gtimg.cn/q={code}"
        resp = await self.client.get(url)
        data = resp.text.strip()
        if "v_" not in data:
            return {"error": "No data"}
        fields = data.split("~")
        if len(fields) < 50:
            return {"error": "Invalid response"}
        return {
            "symbol": symbol,
            "name": fields[1],
            "price": float(fields[3] or 0),
            "change_pct": float(fields[32] or 0),
            "high": float(fields[33] or 0),
            "low": float(fields[34] or 0),
            "open": float(fields[5] or 0),
            "pre_close": float(fields[4] or 0),
            "volume": float(fields[6] or 0),
            "amount": float(fields[37] or 0),
            "turnover": float(fields[38] or 0),
            "pe": float(fields[39] or 0),
            "market_cap": float(fields[45] or 0),
            "pb": float(fields[46] or 0) if len(fields) > 46 else None,
            "update_time": datetime.now().isoformat(),
        }

    async def get_kline(
        self, symbol: str, period: str = "daily",
        start_date: Optional[str] = None, end_date: Optional[str] = None,
        limit: int = 100,
    ) -> list[dict]:
        """Get K-line data via Eastmoney push2 API."""
        secid = self._to_eastmoney_secid(symbol)
        period_map = {"daily": "101", "weekly": "102", "monthly": "103"}
        klt = period_map.get(period, "101")

        if not end_date:
            end_date = date.today().isoformat()
        if not start_date:
            start_date = (date.today() - timedelta(days=365)).isoformat()

        url = "https://push2his.eastmoney.com/api/qt/stock/kline/get"
        params = {
            "secid": secid, "klt": klt, "fqt": "1",
            "beg": start_date.replace("-", ""),
            "end": end_date.replace("-", ""),
            "lmt": limit,
            "fields1": "f1,f2,f3,f4,f5,f6",
            "fields2": "f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61",
        }
        resp = await self.client.get(url, params=params)
        data = resp.json()
        if not data.get("data") or not data["data"].get("klines"):
            return []

        klines = []
        for line in data["data"]["klines"]:
            parts = line.split(",")
            klines.append({
                "date": parts[0],
                "open": float(parts[1]), "close": float(parts[2]),
                "high": float(parts[3]), "low": float(parts[4]),
                "volume": float(parts[5]), "amount": float(parts[6]),
                "change_pct": float(parts[8]) if len(parts) > 8 else 0,
                "turnover": float(parts[10]) if len(parts) > 10 else 0,
            })
        return klines

    async def get_market_overview(self) -> dict:
        """Get A-share market overview with major indices."""
        indices = {
            "sh000001": "上证指数", "sz399001": "深证成指",
            "sz399006": "创业板指", "sh000688": "科创50",
            "sh000300": "沪深300", "sh000016": "上证50",
            "sz399905": "中证500",
        }
        result = {"indices": {}, "market_stats": {}, "timestamp": datetime.now().isoformat()}
        for code, name in indices.items():
            try:
                quote = await self.get_realtime_quote(code)
                result["indices"][name] = {
                    "price": quote.get("price"),
                    "change_pct": quote.get("change_pct"),
                }
            except Exception:
                result["indices"][name] = {"error": "failed"}
        return result

    async def search(self, query: str) -> list[dict]:
        """Search A-share stocks."""
        url = "https://searchadapter.eastmoney.com/api/suggest/get"
        params = {"input": query, "type": "14", "token": "D43BF722C8E33BDC906FB84D85E326E8", "count": 10}
        resp = await self.client.get(url, params=params)
        data = resp.json()
        results = []
        for item in data.get("QuotationCodeTable", {}).get("Data", []):
            results.append({
                "symbol": item.get("Code", ""),
                "name": item.get("Name", ""),
                "market": "A",
                "type": item.get("SecurityTypeName", ""),
            })
        return results

    # ======= Signals (信号层) =======

    async def get_north_flow(self) -> dict:
        """Get 北向资金 real-time flow via THS."""
        url = "https://push2.eastmoney.com/api/qt/kamt.kline/get"
        params = {"fields1": "f1,f2,f3,f4", "fields2": "f51,f52", "klt": "1", "lmt": 60}
        resp = await self.client.get(url, params=params)
        data = resp.json()
        if not data.get("data"):
            return {"error": "No data"}
        flows = []
        for line in data["data"].get("klines", []):
            parts = line.split(",")
            flows.append({"date": parts[0], "net_inflow": float(parts[1])})
        return {"latest": flows[-1] if flows else None, "history": flows}

    async def get_dragon_tiger_board(self, trade_date: Optional[str] = None) -> list[dict]:
        """Get 龙虎榜 data."""
        if not trade_date:
            trade_date = date.today().isoformat().replace("-", "")
        else:
            trade_date = trade_date.replace("-", "")

        url = "https://datacenter-web.eastmoney.com/api/data/v1/get"
        params = {
            "sortColumns": "NET_BUY_AMT",
            "sortTypes": "-1",
            "pageSize": 50,
            "pageNumber": 1,
            "reportName": "RPT_DAILY_BILLBOARDTRADING",
            "columns": "ALL",
            "quoteColumns": "",
            "source": "WEB",
            "client": "WEB",
            "filter": f'(TRADE_DATE>=\'{trade_date}\')',
        }
        resp = await self.client.get(url, params=params)
        data = resp.json()
        results = []
        for item in data.get("result", {}).get("data", []):
            results.append({
                "symbol": item.get("SECURITY_CODE"),
                "name": item.get("SECURITY_NAME_ABBR"),
                "date": item.get("TRADE_DATE"),
                "net_buy_amount": item.get("NET_BUY_AMT"),
                "buy_amount": item.get("BUY_AMT"),
                "sell_amount": item.get("SELL_AMT"),
                "reason": item.get("BILLBOARD_REASON"),
            })
        return results

    async def get_hot_concepts(self) -> list[dict]:
        """Get 热门概念 via THS."""
        url = "https://basic.10jqka.com.cn/api/stockph/index/rise/concept/"
        headers = {"Referer": "https://www.10jqka.com.cn/"}
        try:
            resp = await self.client.get(url, headers=headers)
            data = resp.json()
            concepts = []
            for item in data.get("data", []):
                concepts.append({
                    "name": item.get("name"),
                    "change_pct": item.get("change"),
                    "leading_stock": item.get("leading_stock"),
                    "reason_tags": item.get("reason", "").split(",") if item.get("reason") else [],
                })
            return concepts[:20]
        except Exception as e:
            logger.warning(f"Hot concepts failed: {e}")
            return []

    async def get_industry_ranking(self) -> list[dict]:
        """Get 行业板块排名 via Eastmoney."""
        url = "https://push2.eastmoney.com/api/qt/clist/get"
        params = {
            "pn": 1, "pz": 50, "po": 1, "np": 1,
            "fltt": 2, "invt": 2,
            "fid": "f3", "fs": "m:90+t:2",
            "fields": "f2,f3,f4,f12,f14,f104,f105,f128,f140",
        }
        resp = await self.client.get(url, params=params)
        data = resp.json()
        industries = []
        for item in data.get("data", {}).get("diff", []):
            industries.append({
                "code": item.get("f12"),
                "name": item.get("f14"),
                "change_pct": item.get("f3"),
                "up_count": item.get("f104"),
                "down_count": item.get("f105"),
            })
        return industries

    # ======= Fundamentals (基础数据层) =======

    async def get_financial_summary(self, symbol: str) -> dict:
        """Get financial summary via Eastmoney."""
        secid = self._to_eastmoney_secid(symbol)
        url = "https://push2.eastmoney.com/api/qt/stock/get"
        params = {"secid": secid, "fields": "f43,f44,f45,f46,f48,f49,f50,f55,f57,f58,f60,f115,f116,f117,f162,f167,f168,f169,f170"}
        resp = await self.client.get(url, params=params)
        item = resp.json().get("data", {})
        return {
            "symbol": symbol,
            "price": item.get("f43"),
            "high": item.get("f44"),
            "low": item.get("f45"),
            "volume": item.get("f47"),
            "pe_ttm": item.get("f115"),
            "pb": item.get("f167"),
            "market_cap": item.get("f116"),
            "total_shares": item.get("f168"),
            "float_shares": item.get("f169"),
        }

    async def get_news(self, symbol: str, limit: int = 20) -> list[dict]:
        """Get stock-related news via Eastmoney."""
        url = "https://search-api-web.eastmoney.com/search/jsonp"
        params = {"cb": "jQuery", "param": json.dumps({
            "uid": "", "keyword": symbol, "type": ["8196"], "client": "WEB",
            "clientType": "web", "pageIndex": 1, "pageSize": limit,
        })}
        resp = await self.client.get(url, params=params)
        text = resp.text
        if "jQuery" in text:
            text = text[text.index("(") + 1:text.rindex(")")]
        data = json.loads(text) if text else {}
        news = []
        for item in data.get("Data", []):
            news.append({
                "title": item.get("Title", ""),
                "summary": item.get("Summary", ""),
                "url": item.get("Url", ""),
                "publish_time": item.get("PublishTime", ""),
                "source": item.get("SourceName", ""),
            })
        return news

    # ======= Helpers =======

    def _to_tencent_code(self, symbol: str) -> str:
        """Convert symbol to Tencent format."""
        if symbol.startswith("sh") or symbol.startswith("sz"):
            return symbol
        code = symbol.replace(".SH", "").replace(".SZ", "")
        if len(code) == 6:
            if code.startswith(("6", "5", "9")):
                return f"sh{code}"
            elif code.startswith(("0", "2", "3")):
                return f"sz{code}"
        return f"sz{code}"

    def _to_eastmoney_secid(self, symbol: str) -> str:
        """Convert symbol to Eastmoney secid format."""
        code = symbol.replace(".SH", "").replace(".SZ", "").replace("sh", "").replace("sz", "")
        if code.startswith("6"):
            return f"1.{code}"
        return f"0.{code}"

    async def close(self):
        await self.client.aclose()
