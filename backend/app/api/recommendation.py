"""
Investment recommendation API.
"""
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from datetime import date, timedelta
from typing import Optional
from app.database import get_db
from app.models.market import InvestmentRecommendation
from app.services.recommenders.engine import RecommendationEngine

router = APIRouter()


@router.post("/generate/{market}/{symbol}")
async def generate_recommendation(
    market: str, symbol: str,
    db: Session = Depends(get_db),
):
    """Generate comprehensive investment recommendation."""
    engine = RecommendationEngine()
    result = await engine.generate(market, symbol)

    # Save to DB
    rec = InvestmentRecommendation(
        symbol=symbol,
        market=market,
        date=date.today(),
        **result,
    )
    db.add(rec)
    db.commit()
    db.refresh(rec)
    return rec


@router.get("/")
async def list_recommendations(
    db: Session = Depends(get_db),
    market: Optional[str] = None,
    symbol: Optional[str] = None,
    days: int = Query(7, ge=1, le=90),
):
    """Get recent recommendations."""
    start = date.today() - timedelta(days=days)
    query = db.query(InvestmentRecommendation).filter(
        InvestmentRecommendation.date >= start
    )
    if market:
        query = query.filter(InvestmentRecommendation.market == market)
    if symbol:
        query = query.filter(InvestmentRecommendation.symbol == symbol)
    return query.order_by(InvestmentRecommendation.date.desc()).limit(50).all()


@router.get("/{rec_id}")
async def get_recommendation_detail(rec_id: int, db: Session = Depends(get_db)):
    """Get full recommendation report."""
    rec = db.query(InvestmentRecommendation).filter(
        InvestmentRecommendation.id == rec_id
    ).first()
    if not rec:
        raise HTTPException(404, "Recommendation not found")
    return rec


@router.get("/daily/{market}")
async def get_daily_recommendations(
    market: str,
    db: Session = Depends(get_db),
):
    """Get today's top recommendations for a market."""
    return (
        db.query(InvestmentRecommendation)
        .filter(
            InvestmentRecommendation.market == market,
            InvestmentRecommendation.date == date.today(),
        )
        .order_by(InvestmentRecommendation.composite_score.desc())
        .limit(10)
        .all()
    )
