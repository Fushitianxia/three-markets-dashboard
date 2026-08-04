"""
Market data API endpoints — unified A/HK/US market data.
"""
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from datetime import date, timedelta
from typing import Optional
from app.database import get_db
from app.models.market import MarketSnapshot, IndexSnapshot
from app.services.data_collectors.a_stock import AStockCollector
from app.services.data_collectors.hk_stock import HKStockCollector
from app.services.data_collectors.us_stock import USStockCollector

router = APIRouter()


# ---- Unified Market Quotes ----

@router.get("/quote/{market}/{symbol}")
async def get_quote(market: str, symbol: str):
    """Get live quote for a single stock."""
    collectors = {"A": AStockCollector(), "HK": HKStockCollector(), "US": USStockCollector()}
    if market not in collectors:
        raise HTTPException(400, f"Invalid market: {market}. Use A/HK/US.")
    return await collectors[market].get_realtime_quote(symbol)


@router.get("/kline/{market}/{symbol}")
async def get_kline(
    market: str, symbol: str,
    period: str = Query("daily", description="daily/weekly/monthly"),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = Query(100, ge=1, le=500),
):
    """Get K-line data."""
    collectors = {"A": AStockCollector(), "HK": HKStockCollector(), "US": USStockCollector()}
    if market not in collectors:
        raise HTTPException(400, f"Invalid market: {market}. Use A/HK/US.")
    return await collectors[market].get_kline(symbol, period, start_date, end_date, limit)


@router.get("/snapshots/{market}")
async def get_market_snapshots(
    market: str,
    db: Session = Depends(get_db),
    trade_date: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200),
):
    """Get daily market snapshots."""
    query = db.query(MarketSnapshot).filter(MarketSnapshot.market == market)
    if trade_date:
        query = query.filter(MarketSnapshot.date == date.fromisoformat(trade_date))
    else:
        latest_date = db.query(func.max(MarketSnapshot.date)).filter(
            MarketSnapshot.market == market
        ).scalar()
        if latest_date:
            query = query.filter(MarketSnapshot.date == latest_date)
    return query.order_by(desc(MarketSnapshot.change_pct)).limit(limit).all()


# ---- Indices ----

@router.get("/indices/{market}")
async def get_indices(
    market: str,
    db: Session = Depends(get_db),
    days: int = Query(30, ge=1, le=365),
):
    """Get index snapshots for a market."""
    start = date.today() - timedelta(days=days)
    return (
        db.query(IndexSnapshot)
        .filter(IndexSnapshot.market == market, IndexSnapshot.date >= start)
        .order_by(IndexSnapshot.date.desc())
        .all()
    )


# ---- Market Overview ----

@router.get("/overview")
async def get_market_overview():
    """Get all-markets overview with key indices."""
    collectors = {
        "A": AStockCollector(),
        "HK": HKStockCollector(),
        "US": USStockCollector(),
    }
    overview = {}
    for mkt, collector in collectors.items():
        try:
            overview[mkt] = await collector.get_market_overview()
        except Exception as e:
            overview[mkt] = {"error": str(e)}
    return overview


# ---- Search ----

@router.get("/search")
async def search_stocks(
    q: str = Query(..., min_length=1),
    market: Optional[str] = Query(None, description="A/HK/US"),
):
    """Search stocks across markets."""
    results = []
    collectors = []
    if market:
        mkt_map = {"A": AStockCollector, "HK": HKStockCollector, "US": USStockCollector}
        if market in mkt_map:
            collectors = [mkt_map[market]()]
    else:
        collectors = [AStockCollector(), HKStockCollector(), USStockCollector()]

    for c in collectors:
        try:
            results.extend(await c.search(q))
        except Exception:
            pass
    return results[:20]
