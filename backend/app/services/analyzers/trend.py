"""
Trend Analyzer — multi-timeframe technical trend analysis.
Uses MA, MACD, RSI, Bollinger Bands, ATR, volume analysis.
"""
import asyncio
from datetime import date, datetime
from typing import Optional
import numpy as np
from loguru import logger
from app.services.data_collectors.a_stock import AStockCollector
from app.services.data_collectors.hk_stock import HKStockCollector
from app.services.data_collectors.us_stock import USStockCollector


class TrendAnalyzer:
    """多周期趋势分析器"""

    def __init__(self):
        self._collectors = {
            "A": AStockCollector(),
            "HK": HKStockCollector(),
            "US": USStockCollector(),
        }

    async def analyze(self, market: str, symbol: str) -> dict:
        """Run comprehensive trend analysis."""
        collector = self._collectors.get(market)
        if not collector:
            return {"error": f"Unsupported market: {market}"}

        # Get K-line data
        klines = await collector.get_kline(symbol, "daily", limit=250)
        if not klines:
            return {"error": "No K-line data available"}

        closes = np.array([k["close"] for k in klines])
        highs = np.array([k["high"] for k in klines])
        lows = np.array([k["low"] for k in klines])
        volumes = np.array([k["volume"] for k in klines])

        latest = klines[-1]

        # --- Moving Averages ---
        ma5 = self._sma(closes, 5)
        ma10 = self._sma(closes, 10)
        ma20 = self._sma(closes, 20)
        ma60 = self._sma(closes, 60)
        ma120 = self._sma(closes, 120) if len(closes) >= 120 else None

        # --- RSI ---
        rsi14 = self._rsi(closes, 14)

        # --- MACD ---
        macd_dif, macd_dea, macd_bar = self._macd(closes)

        # --- Bollinger Bands ---
        bb_upper, bb_mid, bb_lower = self._bollinger(closes, 20, 2)

        # --- ATR ---
        atr14 = self._atr(highs, lows, closes, 14)

        # --- Volume Analysis ---
        vol_ma20 = self._sma(volumes, 20)
        vol_ratio = volumes[-1] / vol_ma20[-1] if vol_ma20[-1] > 0 else 1.0

        # --- Trend Classification ---
        short_trend = self._classify_trend(closes, 5, 20)
        medium_trend = self._classify_trend(closes, 20, 60)
        long_trend = self._classify_trend(closes, 60, 120)

        # --- Support / Resistance ---
        support, resistance = self._find_sr_levels(closes)

        # --- Summary ---
        summary = self._generate_summary(
            short_trend, medium_trend, long_trend,
            rsi14[-1], macd_bar[-1], vol_ratio,
            latest["close"], ma20[-1], ma60[-1],
        )

        # Clean up
        for c in self._collectors.values():
            await c.close()

        return {
            "symbol": symbol,
            "market": market,
            "analysis_date": date.today().isoformat(),
            "close": latest["close"],
            "change_pct": latest.get("change_pct", 0),
            "ma5": self._last(ma5), "ma10": self._last(ma10),
            "ma20": self._last(ma20), "ma60": self._last(ma60),
            "ma120": self._last(ma120) if ma120 else None,
            "rsi_14": self._last(rsi14),
            "macd_dif": self._last(macd_dif),
            "macd_dea": self._last(macd_dea),
            "macd_bar": self._last(macd_bar),
            "boll_upper": self._last(bb_upper),
            "boll_mid": self._last(bb_mid),
            "boll_lower": self._last(bb_lower),
            "atr_14": self._last(atr14),
            "volume_ratio": round(vol_ratio, 2),
            "short_trend": short_trend,
            "medium_trend": medium_trend,
            "long_trend": long_trend,
            "support": support,
            "resistance": resistance,
            "summary": summary,
        }

    # ---- Technical Indicators ----

    @staticmethod
    def _sma(data: np.ndarray, period: int) -> np.ndarray:
        if len(data) < period:
            return np.full_like(data, np.nan)
        weights = np.ones(period) / period
        result = np.convolve(data, weights, mode='valid')
        return np.concatenate([np.full(period - 1, np.nan), result])

    @staticmethod
    def _ema(data: np.ndarray, period: int) -> np.ndarray:
        result = np.zeros_like(data)
        result[0] = data[0]
        alpha = 2 / (period + 1)
        for i in range(1, len(data)):
            result[i] = alpha * data[i] + (1 - alpha) * result[i - 1]
        return result

    @staticmethod
    def _rsi(data: np.ndarray, period: int = 14) -> np.ndarray:
        deltas = np.diff(data, prepend=data[0])
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        result = np.zeros(len(data))
        result[:period] = np.nan
        avg_gain = np.mean(gains[:period])
        avg_loss = np.mean(losses[:period])
        for i in range(period, len(data)):
            avg_gain = (avg_gain * (period - 1) + gains[i]) / period
            avg_loss = (avg_loss * (period - 1) + losses[i]) / period
            rs = avg_gain / avg_loss if avg_loss > 0 else 100
            result[i] = 100 - (100 / (1 + rs))
        return result

    @staticmethod
    def _macd(data: np.ndarray, fast: int = 12, slow: int = 26, signal: int = 9):
        ema_fast = TrendAnalyzer._ema(data, fast)
        ema_slow = TrendAnalyzer._ema(data, slow)
        dif = ema_fast - ema_slow
        dea = TrendAnalyzer._ema(dif, signal)
        bar = 2 * (dif - dea)
        return dif, dea, bar

    @staticmethod
    def _bollinger(data: np.ndarray, period: int = 20, std_dev: int = 2):
        mid = TrendAnalyzer._sma(data, period)
        rolling_std = np.array([
            np.nanstd(data[max(0, i - period + 1):i + 1])
            if i >= period - 1 else np.nan
            for i in range(len(data))
        ])
        upper = mid + std_dev * rolling_std
        lower = mid - std_dev * rolling_std
        return upper, mid, lower

    @staticmethod
    def _atr(high: np.ndarray, low: np.ndarray, close: np.ndarray, period: int = 14) -> np.ndarray:
        prev_close = np.roll(close, 1)
        prev_close[0] = close[0]
        tr = np.maximum(high - low, np.maximum(
            np.abs(high - prev_close), np.abs(low - prev_close)
        ))
        return TrendAnalyzer._sma(tr, period)

    @staticmethod
    def _classify_trend(closes: np.ndarray, short_period: int, long_period: int) -> str:
        """Classify trend as up / down / sideways."""
        if len(closes) < long_period:
            return "unknown"
        short_ma = TrendAnalyzer._sma(closes, short_period)[-1]
        long_ma = TrendAnalyzer._sma(closes, long_period)[-1]
        if np.isnan(short_ma) or np.isnan(long_ma):
            return "unknown"
        diff_pct = (short_ma - long_ma) / long_ma * 100
        if diff_pct > 2:
            return "up"
        elif diff_pct < -2:
            return "down"
        return "sideways"

    @staticmethod
    def _find_sr_levels(closes: np.ndarray) -> tuple:
        """Simple support/resistance based on recent highs/lows."""
        recent = closes[-60:] if len(closes) >= 60 else closes
        support = float(np.percentile(recent, 10))
        resistance = float(np.percentile(recent, 90))
        return round(support, 2), round(resistance, 2)

    @staticmethod
    def _generate_summary(short, medium, long, rsi, macd_bar, vol_ratio, close, ma20, ma60) -> str:
        parts = []
        # Price vs MAs
        if close > ma20 > ma60:
            parts.append("多头排列，短期均线在中期均线上方")
        elif close < ma20 < ma60:
            parts.append("空头排列，短期均线在中期均线下方")
        else:
            parts.append("均线交织，方向不明")

        # RSI
        if rsi > 70:
            parts.append(f"RSI={rsi:.1f}，超买区域")
        elif rsi < 30:
            parts.append(f"RSI={rsi:.1f}，超卖区域")
        else:
            parts.append(f"RSI={rsi:.1f}，中性区间")

        # MACD
        if macd_bar > 0:
            parts.append("MACD红柱，多头动能")
        else:
            parts.append("MACD绿柱，空头动能")

        # Volume
        if vol_ratio > 2:
            parts.append(f"放量(量比{vol_ratio:.1f})，需关注")
        elif vol_ratio < 0.5:
            parts.append(f"缩量(量比{vol_ratio:.1f})，交投清淡")

        return "；".join(parts)

    @staticmethod
    def _last(arr: np.ndarray) -> Optional[float]:
        val = arr[-1]
        return round(float(val), 4) if not np.isnan(val) else None
