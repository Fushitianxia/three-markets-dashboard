"""
SQLAlchemy database models for the Three Markets Dashboard.
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, JSON, ForeignKey, Index, Date
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base


def utcnow():
    return datetime.now(timezone.utc)


# ==================== Market Data ====================

class MarketSnapshot(Base):
    """Daily OHLCV snapshot for a single stock across all markets."""
    __tablename__ = "market_snapshots"

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(20), nullable=False, index=True)
    name = Column(String(100))
    market = Column(String(10), nullable=False, comment="A/HK/US")
    date = Column(Date, nullable=False, index=True)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(Float)
    amount = Column(Float, comment="成交额")
    turnover = Column(Float, comment="换手率 %")
    change_pct = Column(Float, comment="涨跌幅 %")
    pe = Column(Float, comment="市盈率")
    pb = Column(Float, comment="市净率")
    market_cap = Column(Float, comment="总市值")
    created_at = Column(DateTime, default=utcnow)

    __table_args__ = (
        Index("idx_market_date_symbol", "date", "symbol"),
        Index("idx_market_market_date", "market", "date"),
    )


class IndexSnapshot(Base):
    """Daily index data (上证, 恒生, 标普500, etc.)"""
    __tablename__ = "index_snapshots"

    id = Column(Integer, primary_key=True, autoincrement=True)
    index_code = Column(String(20), nullable=False, index=True)
    index_name = Column(String(100))
    market = Column(String(10))
    date = Column(Date, nullable=False, index=True)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(Float)
    change_pct = Column(Float)
    created_at = Column(DateTime, default=utcnow)


# ==================== Signals ====================

class TradingSignal(Base):
    """Technical and fundamental trading signals."""
    __tablename__ = "trading_signals"

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(20), nullable=False, index=True)
    market = Column(String(10))
    date = Column(Date, nullable=False, index=True)
    signal_type = Column(String(50), comment="MACD/RSI/KDJ/BOLL/北向资金/龙虎榜/etc")
    signal_name = Column(String(100))
    signal_value = Column(Float)
    signal_level = Column(String(20), comment="bullish/bearish/neutral/strong_buy/strong_sell")
    confidence = Column(Float, comment="置信度 0-1")
    description = Column(Text)
    extra_data = Column(JSON)
    created_at = Column(DateTime, default=utcnow)


class NorthFlow(Base):
    """北向资金流向 (沪深港通)"""
    __tablename__ = "north_flow"

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date, nullable=False, index=True)
    time = Column(String(10), comment="HH:MM")
    hgt_net_inflow = Column(Float, comment="沪股通净流入(亿)")
    sgt_net_inflow = Column(Float, comment="深股通净流入(亿)")
    total_net_inflow = Column(Float, comment="合计净流入(亿)")
    created_at = Column(DateTime, default=utcnow)


class DragonTigerBoard(Base):
    """龙虎榜数据"""
    __tablename__ = "dragon_tiger_board"

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date, nullable=False, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    name = Column(String(100))
    net_buy_amount = Column(Float, comment="净买额(万)")
    buy_amount = Column(Float)
    sell_amount = Column(Float)
    reason = Column(String(200), comment="上榜原因")
    top_buy_brokers = Column(JSON, comment="买入前5席位")
    top_sell_brokers = Column(JSON, comment="卖出前5席位")
    created_at = Column(DateTime, default=utcnow)


class HotConcept(Base):
    """热门概念/题材"""
    __tablename__ = "hot_concepts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date, nullable=False, index=True)
    concept_name = Column(String(100), index=True)
    market = Column(String(10))
    change_pct = Column(Float, comment="概念涨跌幅")
    leading_stock = Column(String(20), comment="领涨股")
    leading_stock_name = Column(String(100))
    hot_score = Column(Float, comment="热度评分")
    reason_tags = Column(JSON, comment="归因标签")
    created_at = Column(DateTime, default=utcnow)


# ==================== Analysis ====================

class TrendAnalysis(Base):
    """Market trend analysis results."""
    __tablename__ = "trend_analyses"

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(20), index=True)
    market = Column(String(10))
    analysis_date = Column(Date, nullable=False, index=True)
    short_trend = Column(String(20), comment="短期趋势: up/down/sideways")
    medium_trend = Column(String(20), comment="中期趋势")
    long_trend = Column(String(20), comment="长期趋势")
    ma5 = Column(Float)
    ma10 = Column(Float)
    ma20 = Column(Float)
    ma60 = Column(Float)
    rsi_14 = Column(Float)
    macd_dif = Column(Float)
    macd_dea = Column(Float)
    macd_bar = Column(Float)
    boll_upper = Column(Float)
    boll_mid = Column(Float)
    boll_lower = Column(Float)
    atr_14 = Column(Float)
    volume_ratio = Column(Float, comment="量比")
    summary = Column(Text, comment="趋势总结")
    created_at = Column(DateTime, default=utcnow)


class QuantitativeFactor(Base):
    """Quantitative factor analysis for individual stocks."""
    __tablename__ = "quantitative_factors"

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(20), nullable=False, index=True)
    name = Column(String(100))
    market = Column(String(10))
    analysis_date = Column(Date, nullable=False, index=True)

    # 估值因子
    pe_ttm = Column(Float)
    pe_percentile_5y = Column(Float, comment="5年PE分位")
    pb = Column(Float)
    ps = Column(Float)
    peg = Column(Float)
    ev_ebitda = Column(Float)

    # 成长因子
    revenue_growth_yoy = Column(Float)
    profit_growth_yoy = Column(Float)
    roe = Column(Float)
    roa = Column(Float)
    gross_margin = Column(Float)
    net_margin = Column(Float)

    # 动量因子
    return_1m = Column(Float)
    return_3m = Column(Float)
    return_6m = Column(Float)
    return_12m = Column(Float)
    alpha_60d = Column(Float)
    beta_60d = Column(Float)
    sharpe_60d = Column(Float)

    # 波动率因子
    volatility_20d = Column(Float)
    volatility_60d = Column(Float)
    max_drawdown_60d = Column(Float)

    # 资金面因子
    north_flow_5d = Column(Float, comment="北向资金5日净流入(亿)")
    institution_holding_pct = Column(Float)
    margin_balance_change = Column(Float)

    # 综合评分
    composite_score = Column(Float, comment="综合量化评分 0-100")
    factor_details = Column(JSON)
    created_at = Column(DateTime, default=utcnow)


# ==================== Tracking & Recommendation ====================

class TrackedStock(Base):
    """User-tracked stocks with alert configuration."""
    __tablename__ = "tracked_stocks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(20), nullable=False, index=True)
    name = Column(String(100))
    market = Column(String(10))
    added_date = Column(Date, default=datetime.now)
    target_buy_price = Column(Float, comment="目标买入价")
    target_sell_price = Column(Float, comment="目标卖出价")
    stop_loss_price = Column(Float, comment="止损价")
    alert_enabled = Column(Boolean, default=True)
    alert_change_pct = Column(Float, default=5.0, comment="涨跌幅预警阈值%")
    alert_volume_ratio = Column(Float, default=2.0, comment="量比预警阈值")
    notes = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)


class InvestmentRecommendation(Base):
    """AI-generated investment recommendations."""
    __tablename__ = "investment_recommendations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(20), nullable=False, index=True)
    name = Column(String(100))
    market = Column(String(10))
    date = Column(Date, nullable=False, index=True)
    action = Column(String(20), comment="buy/sell/hold/accumulate/reduce")
    confidence = Column(Float, comment="置信度 0-1")
    target_price = Column(Float)
    stop_loss = Column(Float)
    position_pct = Column(Float, comment="建议仓位占比%")
    time_horizon = Column(String(20), comment="short/medium/long")

    # 分析依据
    technical_score = Column(Float, comment="技术面评分 0-100")
    fundamental_score = Column(Float, comment="基本面评分 0-100")
    sentiment_score = Column(Float, comment="情绪面评分 0-100")
    macro_score = Column(Float, comment="宏观面评分 0-100")
    composite_score = Column(Float, comment="综合评分 0-100")

    # 详细分析报告
    analysis_report = Column(Text, comment="完整分析报告")
    risk_warnings = Column(JSON, comment="风险提示列表")
    key_catalysts = Column(JSON, comment="关键催化剂")
    macro_factors = Column(JSON, comment="宏观影响因素")

    is_sent = Column(Boolean, default=False, comment="是否已推送邮件")
    created_at = Column(DateTime, default=utcnow)


class EmailConfig(Base):
    """User email configuration."""
    __tablename__ = "email_configs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email_address = Column(String(200), nullable=False)
    is_verified = Column(Boolean, default=False)
    daily_report_enabled = Column(Boolean, default=True, comment="每日市场报告")
    signal_alert_enabled = Column(Boolean, default=True, comment="交易信号预警")
    tracking_alert_enabled = Column(Boolean, default=True, comment="追踪股票预警")
    recommendation_enabled = Column(Boolean, default=True, comment="投资建议推送")
    push_time = Column(String(5), default="16:00", comment="推送时间 HH:MM")
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)


class EmailLog(Base):
    """Email push history."""
    __tablename__ = "email_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    recipient = Column(String(200))
    subject = Column(String(300))
    content_type = Column(String(50), comment="daily_report/signal_alert/tracking_alert/recommendation")
    status = Column(String(20), comment="sent/failed/pending")
    error_msg = Column(Text)
    sent_at = Column(DateTime, default=utcnow)


# ==================== Macro Data ====================

class MacroIndicator(Base):
    """Global macroeconomic indicators."""
    __tablename__ = "macro_indicators"

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date, nullable=False, index=True)
    indicator_name = Column(String(200), index=True)
    indicator_code = Column(String(50), comment="FRED series ID / World Bank code")
    value = Column(Float)
    country = Column(String(50))
    source = Column(String(50), comment="FRED/World Bank/etc")
    notes = Column(Text)
    created_at = Column(DateTime, default=utcnow)
