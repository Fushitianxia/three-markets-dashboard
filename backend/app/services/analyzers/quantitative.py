"""
Quantitative Factor Analyzer — multi-factor model for stock evaluation.
Covers: Value, Growth, Momentum, Volatility, Capital Flow factors.
"""
import asyncio
from datetime import date
from typing import Optional
import numpy as np
from loguru import logger
from app.services.data_collectors.a_stock import AStockCollector
from app.services.data_collectors.hk_stock import HKStockCollector
from app.services.data_collectors.us_stock import USStockCollector


class QuantitativeAnalyzer:
    """量化因子分析器 — 五大因子维度"""

    def __init__(self):
        self._collectors = {
            "A": AStockCollector(),
            "HK": HKStockCollector(),
            "US": USStockCollector(),
        }

    async def analyze(self, market: str, symbol: str) -> dict:
        """Run comprehensive quantitative factor analysis."""
        collector = self._collectors.get(market)
        if not collector:
            return {"error": f"Unsupported market: {market}"}

        # Get data
        klines = await collector.get_kline(symbol, "daily", limit=250)
        if not klines:
            return {"error": "No data available"}

        closes = np.array([k["close"] for k in klines])

        # Get fundamentals (US stocks have richer data)
        fundamentals = {}
        if market == "US":
            fundamentals = await collector.get_financials(symbol)
        elif market == "A":
            fundamentals = await collector.get_financial_summary(symbol)

        # ====== Factor Calculations ======

        # --- Value Factors ---
        value_factors = {
            "pe_ttm": fundamentals.get("pe_ttm"),
            "pb": fundamentals.get("pb"),
            "ps": fundamentals.get("ps"),
            "peg": fundamentals.get("peg"),
            "ev_ebitda": fundamentals.get("ev_ebitda"),
            "pe_percentile_5y": None,  # Would need 5Y PE history
        }

        # --- Growth Factors ---
        growth_factors = {
            "revenue_growth_yoy": fundamentals.get("revenue_growth"),
            "profit_growth_yoy": fundamentals.get("earnings_growth"),
            "roe": fundamentals.get("roe"),
            "roa": fundamentals.get("roa"),
            "gross_margin": fundamentals.get("gross_margin"),
            "net_margin": fundamentals.get("net_margin"),
        }

        # --- Momentum Factors ---
        momentum_factors = self._calc_momentum_factors(closes)

        # --- Volatility Factors ---
        volatility_factors = self._calc_volatility_factors(closes)

        # --- Capital Flow Factors ---
        capital_flow_factors = {
            "north_flow_5d": None,
            "institution_holding_pct": None,
            "margin_balance_change": None,
        }

        # --- Composite Score ---
        composite_score = self._calculate_composite_score(
            value_factors, growth_factors, momentum_factors,
            volatility_factors, capital_flow_factors, market,
        )

        # --- Risk Assessment ---
        risk_assessment = self._assess_risk(volatility_factors, fundamentals)

        # Clean up
        for c in self._collectors.values():
            await c.close()

        return {
            "symbol": symbol,
            "name": fundamentals.get("name", ""),
            "market": market,
            "analysis_date": date.today().isoformat(),
            **value_factors,
            **growth_factors,
            **momentum_factors,
            **volatility_factors,
            **capital_flow_factors,
            "composite_score": round(composite_score, 2),
            "risk_assessment": risk_assessment,
            "factor_details": {
                "value_score": self._score_value(value_factors),
                "growth_score": self._score_growth(growth_factors),
                "momentum_score": self._score_momentum(momentum_factors),
                "volatility_score": self._score_volatility(volatility_factors),
                "capital_flow_score": 50.0,  # Neutral if no data
            },
        }

    def _calc_momentum_factors(self, closes: np.ndarray) -> dict:
        """Calculate momentum-related factors."""
        if len(closes) < 252:
            return {}

        current = closes[-1]

        def ret(period):
            if len(closes) <= period:
                return None
            return round(float((current - closes[-period - 1]) / closes[-period - 1] * 100), 2)

        # Alpha & Beta (vs simple benchmark = equal weight)
        returns = np.diff(closes) / closes[:-1] * 100
        if len(returns) >= 60:
            benchmark_returns = returns[-60:]  # Simplified - would use market index
            stock_returns = returns[-60:]
            beta = np.cov(stock_returns, benchmark_returns)[0][1] / np.var(benchmark_returns) if np.var(benchmark_returns) > 0 else 1
            alpha = np.mean(stock_returns) - beta * np.mean(benchmark_returns)
            sharpe = np.mean(stock_returns) / np.std(stock_returns) * np.sqrt(252) if np.std(stock_returns) > 0 else 0
        else:
            beta, alpha, sharpe = None, None, None

        return {
            "return_1m": ret(21),
            "return_3m": ret(63),
            "return_6m": ret(126),
            "return_12m": ret(252),
            "alpha_60d": round(float(alpha), 4) if alpha is not None else None,
            "beta_60d": round(float(beta), 4) if beta is not None else None,
            "sharpe_60d": round(float(sharpe), 4) if sharpe is not None else None,
        }

    def _calc_volatility_factors(self, closes: np.ndarray) -> dict:
        """Calculate volatility factors."""
        if len(closes) < 60:
            return {}

        returns = np.diff(closes) / closes[:-1] * 100

        def annualized_vol(days):
            if len(returns) < days:
                return None
            return round(float(np.std(returns[-days:]) * np.sqrt(252)), 2)

        # Max drawdown (60-day)
        peak = np.maximum.accumulate(closes[-60:])
        drawdown = (closes[-60:] - peak) / peak * 100
        max_dd = float(np.min(drawdown))

        return {
            "volatility_20d": annualized_vol(20),
            "volatility_60d": annualized_vol(60),
            "max_drawdown_60d": round(max_dd, 2),
        }

    def _calculate_composite_score(
        self, value, growth, momentum, volatility, capital_flow, market,
    ) -> float:
        """Calculate weighted composite score (0-100)."""
        scores = []

        # Value: 25%
        v_score = self._score_value(value)
        scores.append(("value", v_score, 0.25))

        # Growth: 25%
        g_score = self._score_growth(growth)
        scores.append(("growth", g_score, 0.25))

        # Momentum: 25%
        m_score = self._score_momentum(momentum)
        scores.append(("momentum", m_score, 0.25))

        # Volatility: 15%
        vol_score = self._score_volatility(volatility)
        scores.append(("volatility", vol_score, 0.15))

        # Capital flow: 10%
        cf_score = 50.0
        scores.append(("capital_flow", cf_score, 0.10))

        return sum(s * w for _, s, w in scores)

    def _score_value(self, v: dict) -> float:
        """Score value factors — lower PE/PB = higher score."""
        pe = v.get("pe_ttm")
        pb = v.get("pb")
        score = 50.0
        if pe is not None and pe > 0:
            if pe < 15:
                score += 20
            elif pe < 25:
                score += 10
            elif pe > 50:
                score -= 15
        if pb is not None and pb > 0:
            if pb < 1.5:
                score += 15
            elif pb > 5:
                score -= 15
        return min(100, max(0, score))

    def _score_growth(self, g: dict) -> float:
        """Score growth factors."""
        score = 50.0
        rev = g.get("revenue_growth_yoy")
        profit = g.get("profit_growth_yoy")
        roe = g.get("roe")

        if rev is not None:
            if rev > 0.3:
                score += 15
            elif rev > 0.15:
                score += 8
            elif rev < 0:
                score -= 10
        if profit is not None:
            if profit > 0.3:
                score += 15
            elif profit > 0.15:
                score += 8
            elif profit < 0:
                score -= 15
        if roe is not None:
            if roe > 0.2:
                score += 15
            elif roe > 0.1:
                score += 5
            elif roe < 0.05:
                score -= 10
        return min(100, max(0, score))

    def _score_momentum(self, m: dict) -> float:
        """Score momentum factors."""
        score = 50.0
        ret1m = m.get("return_1m")
        ret3m = m.get("return_3m")

        if ret1m is not None:
            if ret1m > 10:
                score += 12
            elif ret1m > 5:
                score += 6
            elif ret1m < -10:
                score -= 15
            elif ret1m < -5:
                score -= 8
        if ret3m is not None:
            if ret3m > 20:
                score += 12
            elif ret3m > 10:
                score += 6
            elif ret3m < -20:
                score -= 15
            elif ret3m < -10:
                score -= 8
        return min(100, max(0, score))

    def _score_volatility(self, v: dict) -> float:
        """Score volatility — lower = better for stability. Higher vol = better for traders."""
        vol60 = v.get("volatility_60d")
        max_dd = v.get("max_drawdown_60d")

        score = 70.0
        if vol60 is not None:
            if vol60 > 60:
                score -= 20
            elif vol60 > 40:
                score -= 10
            elif vol60 < 20:
                score += 10
        if max_dd is not None:
            if abs(max_dd) > 30:
                score -= 20
            elif abs(max_dd) > 20:
                score -= 10
            elif abs(max_dd) < 10:
                score += 10
        return min(100, max(0, score))

    def _assess_risk(self, volatility: dict, fundamentals: dict) -> dict:
        """Assess risk levels."""
        risks = []
        vol60 = volatility.get("volatility_60d")
        max_dd = volatility.get("max_drawdown_60d")

        if vol60 and vol60 > 50:
            risks.append({"type": "high_volatility", "level": "high", "message": f"60日波动率{vol60:.1f}%，处于高波动状态"})
        if max_dd and abs(max_dd) > 25:
            risks.append({"type": "large_drawdown", "level": "high", "message": f"60日最大回撤{abs(max_dd):.1f}%，风险较大"})

        debt = fundamentals.get("debt_to_equity")
        if debt and debt > 2:
            risks.append({"type": "high_leverage", "level": "medium", "message": f"负债权益比{debt:.1f}，杠杆较高"})

        overall = "low"
        if any(r["level"] == "high" for r in risks):
            overall = "high"
        elif len(risks) > 2:
            overall = "medium"

        return {"overall_risk": overall, "risk_items": risks}
