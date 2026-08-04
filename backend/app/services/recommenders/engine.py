"""
Investment Recommendation Engine — generates buy/sell/hold decisions
by integrating technical, fundamental, quantitative, and macro analysis.
"""
import asyncio
from datetime import date, timedelta
from typing import Optional
from loguru import logger
from app.services.analyzers.trend import TrendAnalyzer
from app.services.analyzers.signals import SignalFactory
from app.services.analyzers.quantitative import QuantitativeAnalyzer
from app.services.data_collectors.us_stock import USStockCollector
from app.config import get_settings


class RecommendationEngine:
    """综合投资建议引擎"""

    def __init__(self):
        self.trend_analyzer = TrendAnalyzer()
        self.signal_factory = SignalFactory()
        self.quant_analyzer = QuantitativeAnalyzer()

    async def generate(self, market: str, symbol: str) -> dict:
        """Generate comprehensive investment recommendation."""
        settings = get_settings()

        # Parallel analysis
        trend_task = self.trend_analyzer.analyze(market, symbol)
        signals_task = self.signal_factory.generate_technical_signals(market, symbol)
        quant_task = self.quant_analyzer.analyze(market, symbol)

        trend, signals, factors = await asyncio.gather(
            trend_task, signals_task, quant_task,
            return_exceptions=True,
        )

        if isinstance(trend, Exception):
            trend = {"error": str(trend)}
        if isinstance(signals, Exception):
            signals = []
        if isinstance(factors, Exception):
            factors = {"error": str(factors)}

        # --- Scoring ---
        technical_score = self._score_technical(trend, signals)
        fundamental_score = self._score_fundamental(factors)
        sentiment_score = self._score_sentiment(signals)

        # Macro overlay (if available)
        macro_score = 50.0
        macro_factors = {}
        if market == "US":
            try:
                us_collector = USStockCollector()
                macro_data = await us_collector.get_macro_indicators()
                macro_score = self._score_macro(macro_data)
                macro_factors = macro_data
                await us_collector.close()
            except Exception as e:
                logger.warning(f"Macro data fetch failed: {e}")

        # --- Composite ---
        weights = {"technical": 0.30, "fundamental": 0.30, "sentiment": 0.15, "macro": 0.25}
        composite = (
            technical_score * weights["technical"]
            + fundamental_score * weights["fundamental"]
            + sentiment_score * weights["sentiment"]
            + macro_score * weights["macro"]
        )

        # --- Decision ---
        action, position_pct, time_horizon = self._make_decision(
            composite, trend, signals, factors,
        )

        # --- Target Price & Stop Loss ---
        current_price = trend.get("close", 0) if isinstance(trend, dict) else 0
        atr = trend.get("atr_14", 0) if isinstance(trend, dict) else 0
        target_price, stop_loss = self._calc_price_targets(
            current_price, atr, action, factors,
        )

        # --- Risk Warnings ---
        risk_warnings = self._generate_risk_warnings(trend, factors, macro_factors)

        # --- Key Catalysts ---
        key_catalysts = self._identify_catalysts(signals, factors)

        # --- Generate Report ---
        analysis_report = self._generate_report(
            symbol, market, action, composite,
            technical_score, fundamental_score, sentiment_score, macro_score,
            trend, signals, factors, macro_factors,
            risk_warnings, key_catalysts,
            target_price, stop_loss, position_pct, time_horizon,
        )

        return {
            "action": action,
            "confidence": round(composite / 100, 2),
            "target_price": target_price,
            "stop_loss": stop_loss,
            "position_pct": position_pct,
            "time_horizon": time_horizon,
            "technical_score": round(technical_score, 2),
            "fundamental_score": round(fundamental_score, 2),
            "sentiment_score": round(sentiment_score, 2),
            "macro_score": round(macro_score, 2),
            "composite_score": round(composite, 2),
            "analysis_report": analysis_report,
            "risk_warnings": risk_warnings,
            "key_catalysts": key_catalysts,
            "macro_factors": macro_factors,
        }

    def _score_technical(self, trend: dict, signals: list) -> float:
        """Score technical analysis."""
        if isinstance(trend, Exception) or "error" in trend:
            return 50.0
        score = 50.0

        short = trend.get("short_trend", "")
        medium = trend.get("medium_trend", "")

        if short == "up":
            score += 10
        elif short == "down":
            score -= 15
        if medium == "up":
            score += 10
        elif medium == "down":
            score -= 10

        bullish_count = sum(1 for s in signals if s.get("signal_level") in ("bullish", "strong_buy"))
        bearish_count = sum(1 for s in signals if s.get("signal_level") in ("bearish", "strong_sell"))

        score += bullish_count * 5
        score -= bearish_count * 8

        return min(100, max(0, score))

    def _score_fundamental(self, factors: dict) -> float:
        """Score fundamentals via quant factors."""
        if isinstance(factors, Exception) or "error" in factors:
            return 50.0
        return factors.get("composite_score", 50.0)

    def _score_sentiment(self, signals: list) -> float:
        """Score market sentiment from signals."""
        if not signals:
            return 50.0
        total = len(signals)
        bullish = sum(1 for s in signals if s.get("signal_level") in ("bullish", "strong_buy"))
        return 50.0 + (bullish / total - 0.5) * 40 if total > 0 else 50.0

    def _score_macro(self, macro_data: dict) -> float:
        """Score macro environment."""
        if "error" in macro_data:
            return 50.0
        score = 50.0

        # Fed funds rate: rising = tightening
        fed_rate = macro_data.get("联邦基金利率", {}).get("value")
        if fed_rate is not None:
            if fed_rate > 5:
                score -= 10  # High rates
            elif fed_rate < 2:
                score += 5   # Low rates

        # Yield curve (10Y-2Y spread)
        spread = macro_data.get("10Y-2Y 收益率利差", {}).get("value")
        if spread is not None:
            if spread < 0:
                score -= 15  # Inversion = recession risk
            elif spread > 1:
                score += 10

        # VIX
        vix = macro_data.get("VIX恐慌指数", {}).get("value")
        if vix is not None:
            if vix > 30:
                score -= 15
            elif vix < 15:
                score += 5

        return min(100, max(0, score))

    def _make_decision(self, composite: float, trend: dict, signals: list, factors: dict) -> tuple:
        """Translate scores into actionable decision."""
        if composite >= 75:
            return "buy", 20.0, "medium"  # 建仓20%
        elif composite >= 65:
            return "accumulate", 10.0, "medium"  # 加仓10%
        elif composite >= 45:
            return "hold", 0.0, "short"
        elif composite >= 30:
            return "reduce", -10.0, "short"  # 减仓10%
        else:
            return "sell", -20.0, "short"  # 清仓

    def _calc_price_targets(self, current: float, atr: float, action: str, factors: dict) -> tuple:
        """Calculate target and stop-loss prices."""
        if not current:
            return None, None

        if action in ("buy", "accumulate"):
            target = round(current * 1.15, 2)
            stop = round(current - 2 * (atr or current * 0.05), 2)
        elif action in ("sell", "reduce"):
            target = round(current * 0.90, 2)
            stop = round(current + 2 * (atr or current * 0.05), 2)
        else:
            target = round(current * 1.10, 2)
            stop = round(current * 0.95, 2)

        return target, stop

    def _generate_risk_warnings(self, trend: dict, factors: dict, macro: dict) -> list:
        """Generate risk warnings."""
        risks = []
        if isinstance(factors, dict) and "risk_assessment" in factors:
            risks.extend(factors["risk_assessment"].get("risk_items", []))

        if isinstance(macro, dict):
            spread = macro.get("10Y-2Y 收益率利差", {}).get("value")
            if spread is not None and spread < 0:
                risks.append({"type": "yield_inversion", "level": "high",
                              "message": "美债收益率曲线倒挂，经济衰退风险上升"})

            vix = macro.get("VIX恐慌指数", {}).get("value")
            if vix is not None and vix > 25:
                risks.append({"type": "market_fear", "level": "high",
                              "message": f"VIX={vix}，市场恐慌情绪较高"})

        return risks

    def _identify_catalysts(self, signals: list, factors: dict) -> list:
        """Identify key catalysts."""
        catalysts = []

        bullish_signals = [s for s in signals if s.get("signal_level") in ("bullish", "strong_buy")]
        if len(bullish_signals) >= 3:
            catalysts.append({"type": "technical", "message": "多个技术指标共振看多"})

        ret1m = factors.get("return_1m") if isinstance(factors, dict) else None
        if ret1m is not None and ret1m > 15:
            catalysts.append({"type": "momentum", "message": f"近1月涨幅{ret1m}%，强势动能"})

        roe = factors.get("roe") if isinstance(factors, dict) else None
        if roe is not None and roe > 0.20:
            catalysts.append({"type": "fundamental", "message": f"ROE={roe:.0%}，盈利能力优秀"})

        return catalysts

    def _generate_report(self, symbol, market, action, composite,
                         tech, fund, sent, macro,
                         trend, signals, factors, macro_factors,
                         risks, catalysts, target, stop, position, horizon) -> str:
        """Generate natural language analysis report."""
        action_cn = {"buy": "【买入】", "accumulate": "【加仓】", "hold": "【持有】",
                      "reduce": "【减仓】", "sell": "【卖出】"}
        market_cn = {"A": "A股", "HK": "港股", "US": "美股"}

        lines = [
            f"═══ 三国演义 · 投资分析报告 ═══",
            f"标的：{symbol} ({market_cn.get(market, market)})",
            f"日期：{date.today().isoformat()}",
            f"操作建议：{action_cn.get(action, action)}",
            f"",
            f"【综合评分】{composite:.1f}/100",
            f"  ├ 技术面：{tech:.1f}/100",
            f"  ├ 基本面：{fund:.1f}/100",
            f"  ├ 情绪面：{sent:.1f}/100",
            f"  └ 宏观面：{macro:.1f}/100",
            f"",
        ]

        if target:
            lines.append(f"【目标价位】${target}")
        if stop:
            lines.append(f"【止损价位】${stop}")
        lines.append(f"【建议仓位】{abs(position):.0f}%")
        lines.append(f"【投资周期】{horizon}")
        lines.append("")

        if isinstance(trend, dict) and "summary" in trend:
            lines.append(f"【趋势分析】{trend['summary']}")
            lines.append("")

        if risks:
            lines.append("【风险提示】")
            for r in risks:
                lines.append(f"  ⚠ {r.get('message', '')}")
            lines.append("")

        if catalysts:
            lines.append("【关键催化剂】")
            for c in catalysts:
                lines.append(f"  ✓ {c.get('message', '')}")
            lines.append("")

        lines.append("【免责声明】本报告由AI自动生成，仅供参考，不构成投资建议。投资有风险，入市需谨慎。")

        return "\n".join(lines)
