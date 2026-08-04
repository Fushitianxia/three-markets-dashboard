"""
APScheduler Jobs — daily data collection, signal generation, and email push.
"""
import asyncio
from datetime import date, datetime, timedelta
from loguru import logger
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from app.database import SessionLocal, init_db

_scheduler: BackgroundScheduler = None


def start_scheduler():
    """Start the background scheduler."""
    global _scheduler
    if _scheduler:
        return

    _scheduler = BackgroundScheduler(timezone="Asia/Shanghai")
    logger.info("Starting scheduler...")

    # Market data collection: every trading day after market close
    _scheduler.add_job(
        collect_daily_data,
        CronTrigger(hour=15, minute=30, day_of_week="mon-fri"),
        id="collect_daily_data",
        name="每日数据采集",
        replace_existing=True,
    )

    # Signal generation: after data collection
    _scheduler.add_job(
        generate_daily_signals,
        CronTrigger(hour=15, minute=45, day_of_week="mon-fri"),
        id="generate_signals",
        name="每日信号生成",
        replace_existing=True,
    )

    # Daily report email: late afternoon
    _scheduler.add_job(
        send_daily_reports,
        CronTrigger(hour=16, minute=0, day_of_week="mon-fri"),
        id="daily_report",
        name="每日报告推送",
        replace_existing=True,
    )

    # Tracking alerts: check every 30 minutes during trading hours
    _scheduler.add_job(
        check_tracking_alerts,
        CronTrigger(minute="*/30", hour="9-15", day_of_week="mon-fri"),
        id="tracking_alerts",
        name="追踪股票预警",
        replace_existing=True,
    )

    _scheduler.start()
    logger.info("Scheduler started with 4 jobs")


def stop_scheduler():
    """Stop the scheduler."""
    global _scheduler
    if _scheduler:
        _scheduler.shutdown(wait=False)
        _scheduler = None
        logger.info("Scheduler stopped")


# ======= Job Functions =======

def collect_daily_data():
    """Collect daily market data for all tracked markets."""
    logger.info("Job: Collecting daily market data...")
    try:
        # In production, this would iterate tracked stocks and collect data
        # For MVP, we log the intent
        from app.services.data_collectors.a_stock import AStockCollector
        from app.services.data_collectors.hk_stock import HKStockCollector
        from app.services.data_collectors.us_stock import USStockCollector

        async def _collect():
            collectors = [AStockCollector(), HKStockCollector(), USStockCollector()]
            for c in collectors:
                try:
                    overview = await c.get_market_overview()
                    logger.info(f"{c.market} market overview collected")
                except Exception as e:
                    logger.error(f"{c.market} data collection failed: {e}")
                finally:
                    await c.close()

        asyncio.run(_collect())
    except Exception as e:
        logger.error(f"Daily data collection failed: {e}")


def generate_daily_signals():
    """Generate trading signals for tracked stocks."""
    logger.info("Job: Generating daily signals...")
    try:
        db = SessionLocal()
        try:
            from app.models.market import TrackedStock
            stocks = db.query(TrackedStock).filter(
                TrackedStock.is_active == True,
                TrackedStock.alert_enabled == True,
            ).all()

            logger.info(f"Generating signals for {len(stocks)} tracked stocks")

            async def _generate():
                from app.services.analyzers.signals import SignalFactory
                factory = SignalFactory()
                for stock in stocks:
                    try:
                        signals = await factory.generate_technical_signals(
                            stock.market, stock.symbol,
                        )
                        logger.info(f"  {stock.symbol}: {len(signals)} signals")
                        # Save signals to DB
                        for s in signals:
                            from app.models.market import TradingSignal
                            record = TradingSignal(
                                symbol=stock.symbol,
                                market=stock.market,
                                date=date.today(),
                                **s,
                            )
                            db.add(record)
                        db.commit()
                    except Exception as e:
                        logger.error(f"  {stock.symbol} signal generation failed: {e}")

            asyncio.run(_generate())
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Signal generation failed: {e}")


def send_daily_reports():
    """Send daily report emails."""
    logger.info("Job: Sending daily reports...")
    try:
        db = SessionLocal()
        try:
            from app.models.market import EmailConfig
            from app.services.email_service import EmailService

            config = db.query(EmailConfig).first()
            if not config or not config.email_address or not config.daily_report_enabled:
                logger.info("No email config or daily report disabled")
                return

            service = EmailService()

            async def _send():
                await service.send_daily_report(config.email_address, "A")

            asyncio.run(_send())
            logger.info(f"Daily report sent to {config.email_address}")
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Daily report send failed: {e}")


def check_tracking_alerts():
    """Check tracking stock alerts."""
    logger.info("Job: Checking tracking alerts...")
    try:
        db = SessionLocal()
        try:
            from app.models.market import TrackedStock
            stocks = db.query(TrackedStock).filter(
                TrackedStock.is_active == True,
                TrackedStock.alert_enabled == True,
            ).all()

            logger.info(f"Checking alerts for {len(stocks)} stocks")

            async def _check():
                from app.services.analyzers.trend import TrendAnalyzer
                analyzer = TrendAnalyzer()
                alerts_triggered = 0
                for stock in stocks:
                    try:
                        trend = await analyzer.analyze(stock.market, stock.symbol)
                        close = trend.get("close", 0)
                        change_pct = trend.get("change_pct", 0)

                        triggered = False
                        if stock.target_buy_price and close <= stock.target_buy_price:
                            triggered = True
                            logger.info(f"  BUY alert: {stock.symbol} @ {close} <= {stock.target_buy_price}")
                        if stock.target_sell_price and close >= stock.target_sell_price:
                            triggered = True
                            logger.info(f"  SELL alert: {stock.symbol} @ {close} >= {stock.target_sell_price}")
                        if stock.stop_loss_price and close <= stock.stop_loss_price:
                            triggered = True
                            logger.info(f"  STOP LOSS: {stock.symbol} @ {close} <= {stock.stop_loss_price}")
                        if abs(change_pct) >= stock.alert_change_pct:
                            triggered = True
                            logger.info(f"  VOLATILITY alert: {stock.symbol} {change_pct}%")

                        if triggered:
                            alerts_triggered += 1
                    except Exception as e:
                        logger.error(f"  Alert check failed for {stock.symbol}: {e}")

                if alerts_triggered > 0:
                    # Send alert email
                    try:
                        from app.models.market import EmailConfig
                        from app.services.email_service import EmailService
                        config = db.query(EmailConfig).first()
                        if config and config.email_address and config.tracking_alert_enabled:
                            service = EmailService()
                            await service.send_tracking_recommendations(config.email_address)
                            logger.info(f"Alert email sent for {alerts_triggered} triggers")
                    except Exception as e:
                        logger.error(f"Alert email failed: {e}")

            asyncio.run(_check())
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Tracking alert check failed: {e}")
