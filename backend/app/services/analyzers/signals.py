"""
Signal Factory — generates trading signals from technical, fundamental, and sentiment data.
"""
import asyncio
from datetime import date
from typing import Optional
import numpy as np
from loguru import logger
from app.services.data_collectors.a_stock import AStockCollector
from app.services.data_collectors.hk_stock import HKStockCollector
from app.services.data_collectors.us_stock import USStockCollector


class SignalFactory:
    """交易信号工厂 — 多维度信号生成"""

    def __init__(self):
        self._collectors = {
            "A": AStockCollector(),
            "HK": HKStockCollector(),
            "US": USStockCollector(),
        }

    async def generate_technical_signals(self, market: str, symbol: str) -> list[dict]:
        """Generate all technical signals."""
        collector = self._collectors.get(market)
        if not collector:
            return []

        klines = await collector.get_kline(symbol, "daily", limit=250)
        if not klines:
            return []

        closes = np.array([k["close"] for k in klines])
        highs = np.array([k["high"] for k in klines])
        lows = np.array([k["low"] for k in klines])
        volumes = np.array([k["volume"] for k in klines])

        signals = []

        # --- MACD Signal ---
        macd_signal = self._check_macd(closes)
        if macd_signal:
            signals.append(macd_signal)

        # --- RSI Signal ---
        rsi_signal = self._check_rsi(closes)
        if rsi_signal:
            signals.append(rsi_signal)

        # --- KDJ Signal ---
        kdj_signal = self._check_kdj(highs, lows, closes)
        if kdj_signal:
            signals.append(kdj_signal)

        # --- Bollinger Band Signal ---
        bb_signal = self._check_bollinger(closes)
        if bb_signal:
            signals.append(bb_signal)

        # --- MA Cross Signal ---
        ma_signal = self._check_ma_cross(closes)
        if ma_signal:
            signals.append(ma_signal)

        # --- Volume Signal ---
        vol_signal = self._check_volume(volumes, closes)
        if vol_signal:
            signals.append(vol_signal)

        # --- Support/Resistance Signal ---
        sr_signal = self._check_sr_levels(closes, highs, lows)
        if sr_signal:
            signals.append(sr_signal)

        # Clean up
        for c in self._collectors.values():
            await c.close()

        return signals

    def _check_macd(self, closes: np.ndarray) -> Optional[dict]:
        """MACD golden/death cross signal."""
        dif, dea, bar = self._calc_macd(closes)
        if len(dif) < 3:
            return None

        # Golden cross: DIF crosses above DEA
        if dif[-2] <= dea[-2] and dif[-1] > dea[-1]:
            return {
                "signal_type": "MACD",
                "signal_name": "MACD金叉",
                "signal_value": round(float(dif[-1]), 4),
                "signal_level": "bullish",
                "confidence": 0.7,
                "description": "DIF上穿DEA，短期看涨信号",
            }

        # Death cross: DIF crosses below DEA
        if dif[-2] >= dea[-2] and dif[-1] < dea[-1]:
            return {
                "signal_type": "MACD",
                "signal_name": "MACD死叉",
                "signal_value": round(float(dif[-1]), 4),
                "signal_level": "bearish",
                "confidence": 0.7,
                "description": "DIF下穿DEA，短期看跌信号",
            }
        return None

    def _check_rsi(self, closes: np.ndarray) -> Optional[dict]:
        """RSI overbought/oversold signal."""
        rsi = self._calc_rsi(closes)
        val = rsi[-1]

        if val > 80:
            return {
                "signal_type": "RSI",
                "signal_name": "RSI超买",
                "signal_value": round(float(val), 2),
                "signal_level": "bearish",
                "confidence": 0.65,
                "description": f"RSI={val:.1f}，处于超买区域，回调风险加大",
            }
        if val < 20:
            return {
                "signal_type": "RSI",
                "signal_name": "RSI超卖",
                "signal_value": round(float(val), 2),
                "signal_level": "bullish",
                "confidence": 0.65,
                "description": f"RSI={val:.1f}，处于超卖区域，反弹概率较大",
            }
        return None

    def _check_kdj(self, highs, lows, closes) -> Optional[dict]:
        """KDJ signal."""
        k, d, j = self._calc_kdj(highs, lows, closes)
        if k[-1] is None:
            return None

        if j[-1] > 100:
            return {
                "signal_type": "KDJ",
                "signal_name": "KDJ超买",
                "signal_value": round(float(j[-1]), 2),
                "signal_level": "bearish",
                "confidence": 0.6,
                "description": f"J值={j[-1]:.1f}>100，超买区域",
            }
        if j[-1] < 0:
            return {
                "signal_type": "KDJ",
                "signal_name": "KDJ超卖",
                "signal_value": round(float(j[-1]), 2),
                "signal_level": "bullish",
                "confidence": 0.6,
                "description": f"J值={j[-1]:.1f}<0，超卖区域",
            }
        return None

    def _check_bollinger(self, closes: np.ndarray) -> Optional[dict]:
        """Bollinger Band breakout signal."""
        mid = self._sma(closes, 20)
        std = np.nanstd(closes[-20:]) if len(closes) >= 20 else 0
        upper = mid + 2 * std
        lower = mid - 2 * std

        price = closes[-1]

        if price > upper[-1]:
            return {
                "signal_type": "BOLL",
                "signal_name": "布林带上轨突破",
                "signal_value": round(float(price), 2),
                "signal_level": "bullish" if closes[-1] > closes[-2] else "bearish",
                "confidence": 0.55,
                "description": "价格突破布林带上轨，强势特征",
            }
        if price < lower[-1]:
            return {
                "signal_type": "BOLL",
                "signal_name": "布林带下轨跌破",
                "signal_value": round(float(price), 2),
                "signal_level": "bearish" if closes[-1] < closes[-2] else "bullish",
                "confidence": 0.55,
                "description": "价格跌破布林带下轨，弱势特征",
            }
        return None

    def _check_ma_cross(self, closes: np.ndarray) -> Optional[dict]:
        """MA crossover signal."""
        ma5 = self._sma(closes, 5)
        ma20 = self._sma(closes, 20)

        if len(ma5) < 3:
            return None

        # Golden cross: MA5 crosses above MA20
        if ma5[-2] <= ma20[-2] and ma5[-1] > ma20[-1]:
            return {
                "signal_type": "MA_CROSS",
                "signal_name": "5日均线上穿20日均线",
                "signal_value": round(float(closes[-1]), 2),
                "signal_level": "strong_buy",
                "confidence": 0.75,
                "description": "短期均线上穿中期均线，趋势转多",
            }

        if ma5[-2] >= ma20[-2] and ma5[-1] < ma20[-1]:
            return {
                "signal_type": "MA_CROSS",
                "signal_name": "5日均线下穿20日均线",
                "signal_value": round(float(closes[-1]), 2),
                "signal_level": "strong_sell",
                "confidence": 0.75,
                "description": "短期均线下穿中期均线，趋势转空",
            }
        return None

    def _check_volume(self, volumes: np.ndarray, closes: np.ndarray) -> Optional[dict]:
        """Volume anomaly signal."""
        vol_ma20 = self._sma(volumes, 20)
        ratio = volumes[-1] / vol_ma20[-1] if vol_ma20[-1] > 0 else 1

        if ratio > 2.5:
            direction = "放量上涨" if closes[-1] > closes[-2] else "放量下跌"
            return {
                "signal_type": "VOLUME",
                "signal_name": f"{direction}",
                "signal_value": round(float(ratio), 2),
                "signal_level": "bullish" if closes[-1] > closes[-2] else "bearish",
                "confidence": 0.5,
                "description": f"量比{ratio:.1f}，" + ("资金介入明显" if closes[-1] > closes[-2] else "资金出逃信号"),
            }
        return None

    def _check_sr_levels(self, closes, highs, lows) -> Optional[dict]:
        """Support/resistance breakout signal."""
        recent_high = float(np.max(highs[-60:]))
        recent_low = float(np.min(lows[-60:]))
        price = closes[-1]

        if price > recent_high * 0.98:
            return {
                "signal_type": "BREAKOUT",
                "signal_name": "接近前高阻力",
                "signal_value": round(float(price), 2),
                "signal_level": "bullish",
                "confidence": 0.5,
                "description": f"价格接近60日前高{recent_high:.2f}，突破则打开空间",
            }
        if price < recent_low * 1.02:
            return {
                "signal_type": "BREAKDOWN",
                "signal_name": "接近前低支撑",
                "signal_value": round(float(price), 2),
                "signal_level": "bearish",
                "confidence": 0.5,
                "description": f"价格接近60日前低{recent_low:.2f}，跌破则下行风险加大",
            }
        return None

    # === Helpers ===

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
    def _calc_macd(data, fast=12, slow=26, signal=9):
        ef = SignalFactory._ema(data, fast)
        es = SignalFactory._ema(data, slow)
        dif = ef - es
        dea = SignalFactory._ema(dif, signal)
        bar = 2 * (dif - dea)
        return dif, dea, bar

    @staticmethod
    def _calc_rsi(data: np.ndarray, period: int = 14) -> np.ndarray:
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
    def _calc_kdj(highs, lows, closes, n=9, m1=3, m2=3):
        k = np.full(len(closes), np.nan)
        d = np.full(len(closes), np.nan)
        j = np.full(len(closes), np.nan)
        for i in range(n - 1, len(closes)):
            hh = np.max(highs[i - n + 1:i + 1])
            ll = np.min(lows[i - n + 1:i + 1])
            rsv = (closes[i] - ll) / (hh - ll) * 100 if hh != ll else 50
            if i == n - 1:
                k[i] = (2/3) * 50 + (1/3) * rsv
                d[i] = (2/3) * 50 + (1/3) * k[i]
            else:
                k[i] = (2/3) * k[i - 1] + (1/3) * rsv
                d[i] = (2/3) * d[i - 1] + (1/3) * k[i]
            j[i] = 3 * k[i] - 2 * d[i]
        return k, d, j
