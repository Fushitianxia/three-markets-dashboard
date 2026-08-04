"""
Trading signals API: north flow, dragon-tiger board, hot concepts, technical signals.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import date, timedelta
from typing import Optional
from app.database import get_db
from app.models.market import TradingSignal, NorthFlow, DragonTigerBoard, HotConcept
from app.services.analyzers.signals import SignalFactory

router = APIRouter()


@router.get("/technical/{market}/{symbol}")
async def get_technical_signals(
    market: str, symbol: str,
    db: Session = Depends(get_db),
):
    """Get all technical signals for a stock."""
    factory = SignalFactory()
    signals = await factory.generate_technical_signals(market, symbol)

    # Save signals
    for s in signals:
        record = TradingSignal(
            symbol=symbol,
            market=market,
            date=date.today(),
            **s,
        )
        db.add(record)
    db.commit()

    return signals


@router.get("/north-flow")
async def get_north_flow(
    db: Session = Depends(get_db),
    days: int = Query(30, ge=1, le=365),
):
    """Get 北向资金 flow history."""
    start = date.today() - timedelta(days=days)
    return (
        db.query(NorthFlow)
        .filter(NorthFlow.date >= start)
        .order_by(NorthFlow.date.desc())
        .all()
    )


@router.get("/dragon-tiger")
async def get_dragon_tiger_board(
    db: Session = Depends(get_db),
    trade_date: Optional[str] = None,
    symbol: Optional[str] = None,
):
    """Get 龙虎榜 data."""
    query = db.query(DragonTigerBoard)
    if trade_date:
        query = query.filter(DragonTigerBoard.date == date.fromisoformat(trade_date))
    if symbol:
        query = query.filter(DragonTigerBoard.symbol == symbol)
    return query.order_by(DragonTigerBoard.net_buy_amount.desc()).limit(50).all()


@router.get("/hot-concepts")
async def get_hot_concepts(
    db: Session = Depends(get_db),
    market: str = Query("A", description="A/HK/US"),
    trade_date: Optional[str] = None,
):
    """Get today's hot concepts/themes."""
    query = db.query(HotConcept).filter(HotConcept.market == market)
    if trade_date:
        query = query.filter(HotConcept.date == date.fromisoformat(trade_date))
    return query.order_by(HotConcept.hot_score.desc()).limit(30).all()


@router.get("/summary")
async def get_signal_summary(
    db: Session = Depends(get_db),
    market: str = Query("A"),
):
    """Get aggregated signal summary for dashboard."""
    today = date.today()
    return {
        "north_flow": db.query(NorthFlow).filter(NorthFlow.date == today).first(),
        "dragon_tiger_count": db.query(DragonTigerBoard).filter(
            DragonTigerBoard.date == today
        ).count(),
        "hot_concepts": db.query(HotConcept).filter(
            HotConcept.market == market,
            HotConcept.date == today,
        ).order_by(HotConcept.hot_score.desc()).limit(10).all(),
        "bullish_signals": db.query(TradingSignal).filter(
            TradingSignal.date == today,
            TradingSignal.market == market,
            TradingSignal.signal_level.in_(["bullish", "strong_buy"]),
        ).count(),
        "bearish_signals": db.query(TradingSignal).filter(
            TradingSignal.date == today,
            TradingSignal.market == market,
            TradingSignal.signal_level.in_(["bearish", "strong_sell"]),
        ).count(),
    }
