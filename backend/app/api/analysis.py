"""
Analysis API: trend analysis, quantitative factors, and market insights.
"""
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from datetime import date, timedelta
from typing import Optional
from app.database import get_db
from app.models.market import TrendAnalysis, QuantitativeFactor
from app.services.analyzers.trend import TrendAnalyzer
from app.services.analyzers.quantitative import QuantitativeAnalyzer

router = APIRouter()


@router.get("/trend/{market}/{symbol}")
async def analyze_trend(
    market: str, symbol: str,
    db: Session = Depends(get_db),
):
    """Run comprehensive trend analysis for a stock."""
    analyzer = TrendAnalyzer()
    result = await analyzer.analyze(market, symbol)

    # Save to DB
    record = TrendAnalysis(
        symbol=symbol,
        market=market,
        analysis_date=date.today(),
        **result,
    )
    db.add(record)
    db.commit()

    return result


@router.get("/factors/{market}/{symbol}")
async def get_quantitative_factors(
    market: str, symbol: str,
    db: Session = Depends(get_db),
):
    """Run quantitative factor analysis."""
    analyzer = QuantitativeAnalyzer()
    result = await analyzer.analyze(market, symbol)

    # Save to DB
    record = QuantitativeFactor(
        symbol=symbol,
        market=market,
        analysis_date=date.today(),
        **result,
    )
    db.add(record)
    db.commit()

    return result


@router.get("/factors/history/{market}/{symbol}")
async def get_factor_history(
    market: str, symbol: str,
    db: Session = Depends(get_db),
    days: int = Query(90, ge=1, le=365),
):
    """Get historical quantitative factor data."""
    start = date.today() - timedelta(days=days)
    return (
        db.query(QuantitativeFactor)
        .filter(
            QuantitativeFactor.symbol == symbol,
            QuantitativeFactor.market == market,
            QuantitativeFactor.analysis_date >= start,
        )
        .order_by(QuantitativeFactor.analysis_date.desc())
        .all()
    )
