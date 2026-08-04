"""
Stock tracking API: manage tracked stocks and alerts.
"""
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from datetime import date
from typing import Optional, List
from pydantic import BaseModel
from app.database import get_db
from app.models.market import TrackedStock
from app.services.analyzers.trend import TrendAnalyzer
from app.services.analyzers.quantitative import QuantitativeAnalyzer

router = APIRouter()


class TrackStockRequest(BaseModel):
    symbol: str
    name: str
    market: str
    target_buy_price: Optional[float] = None
    target_sell_price: Optional[float] = None
    stop_loss_price: Optional[float] = None
    alert_change_pct: float = 5.0
    alert_volume_ratio: float = 2.0
    notes: Optional[str] = None


class UpdateTrackRequest(BaseModel):
    target_buy_price: Optional[float] = None
    target_sell_price: Optional[float] = None
    stop_loss_price: Optional[float] = None
    alert_enabled: Optional[bool] = None
    alert_change_pct: Optional[float] = None
    alert_volume_ratio: Optional[float] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None


@router.get("/")
async def list_tracked_stocks(
    db: Session = Depends(get_db),
    market: Optional[str] = None,
    active_only: bool = True,
):
    """List all tracked stocks."""
    query = db.query(TrackedStock)
    if market:
        query = query.filter(TrackedStock.market == market)
    if active_only:
        query = query.filter(TrackedStock.is_active == True)
    return query.order_by(TrackedStock.added_date.desc()).all()


@router.post("/")
async def add_tracked_stock(req: TrackStockRequest, db: Session = Depends(get_db)):
    """Add a stock to tracking list."""
    existing = db.query(TrackedStock).filter(
        TrackedStock.symbol == req.symbol,
        TrackedStock.market == req.market,
    ).first()
    if existing:
        raise HTTPException(400, f"Stock {req.symbol} already tracked")

    stock = TrackedStock(
        symbol=req.symbol,
        name=req.name,
        market=req.market,
        added_date=date.today(),
        target_buy_price=req.target_buy_price,
        target_sell_price=req.target_sell_price,
        stop_loss_price=req.stop_loss_price,
        alert_change_pct=req.alert_change_pct,
        alert_volume_ratio=req.alert_volume_ratio,
        notes=req.notes,
    )
    db.add(stock)
    db.commit()
    db.refresh(stock)
    return stock


@router.put("/{stock_id}")
async def update_tracked_stock(
    stock_id: int,
    req: UpdateTrackRequest,
    db: Session = Depends(get_db),
):
    """Update tracking stock settings."""
    stock = db.query(TrackedStock).filter(TrackedStock.id == stock_id).first()
    if not stock:
        raise HTTPException(404, "Tracked stock not found")

    for key, value in req.model_dump(exclude_unset=True).items():
        setattr(stock, key, value)
    db.commit()
    return {"status": "updated"}


@router.delete("/{stock_id}")
async def remove_tracked_stock(stock_id: int, db: Session = Depends(get_db)):
    """Remove a stock from tracking."""
    stock = db.query(TrackedStock).filter(TrackedStock.id == stock_id).first()
    if not stock:
        raise HTTPException(404, "Tracked stock not found")
    db.delete(stock)
    db.commit()
    return {"status": "deleted"}


@router.get("/{stock_id}/dashboard")
async def get_tracking_dashboard(stock_id: int, db: Session = Depends(get_db)):
    """Get comprehensive tracking dashboard for a tracked stock."""
    stock = db.query(TrackedStock).filter(TrackedStock.id == stock_id).first()
    if not stock:
        raise HTTPException(404, "Tracked stock not found")

    # Get trend + factors + signals
    trend = await TrendAnalyzer().analyze(stock.market, stock.symbol)
    factors = await QuantitativeAnalyzer().analyze(stock.market, stock.symbol)

    return {
        "stock": stock,
        "trend": trend,
        "factors": factors,
        "alerts": _check_alerts(stock, trend),
    }


def _check_alerts(stock: TrackedStock, trend: dict) -> list:
    """Check if any alert conditions are triggered."""
    alerts = []
    close_price = trend.get("close", 0)

    if stock.target_buy_price and close_price <= stock.target_buy_price:
        alerts.append({
            "type": "buy_target",
            "message": f"股价 {close_price} 已达到目标买入价 {stock.target_buy_price}",
            "level": "info",
        })
    if stock.target_sell_price and close_price >= stock.target_sell_price:
        alerts.append({
            "type": "sell_target",
            "message": f"股价 {close_price} 已达到目标卖出价 {stock.target_sell_price}",
            "level": "warning",
        })
    if stock.stop_loss_price and close_price <= stock.stop_loss_price:
        alerts.append({
            "type": "stop_loss",
            "message": f"股价 {close_price} 已触发止损价 {stock.stop_loss_price}",
            "level": "danger",
        })

    change_pct = trend.get("change_pct", 0)
    if abs(change_pct) >= stock.alert_change_pct:
        alerts.append({
            "type": "volatility",
            "message": f"当日涨跌幅 {change_pct:.2f}% 超过预警阈值 {stock.alert_change_pct}%",
            "level": "warning" if change_pct < 0 else "info",
        })

    return alerts
