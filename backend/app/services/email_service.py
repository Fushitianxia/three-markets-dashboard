"""
Email Push Service — QQ Mail SMTP integration.
Sends daily reports, signal alerts, tracking alerts, and investment recommendations.
"""
import asyncio
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import date, datetime
from typing import Optional
from loguru import logger
from app.config import get_settings


class EmailService:
    """邮件推送服务 — QQ邮箱"""

    def __init__(self):
        self.settings = get_settings()

    async def send_test(self, to_email: str) -> tuple[bool, str]:
        """Send test email."""
        subject = "[三国演义] 邮件推送测试"
        body = f"""
        <h2>三国演义 · 全球三市数据可视化系统</h2>
        <p>✅ 邮件推送服务配置成功！</p>
        <p>发送时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <hr>
        <p style="color: #666; font-size: 12px;">
            您将收到以下类型的邮件：<br>
            📊 每日市场报告 · 🚨 交易信号预警 · 🎯 追踪股票预警 · 💡 投资建议
        </p>
        """
        return await self._send(to_email, subject, body)

    async def send_daily_report(self, to_email: str, market: str = "A") -> tuple[bool, str]:
        """Send daily market report."""
        market_names = {"A": "A股", "HK": "港股", "US": "美股"}
        market_name = market_names.get(market, market)

        today = date.today().isoformat()

        body = f"""
        <html>
        <head><style>
            body {{ font-family: 'Microsoft YaHei', Arial, sans-serif; color: #333; }}
            .header {{ background: linear-gradient(135deg, #d4380d, #cf1322); color: white; padding: 20px; border-radius: 8px; }}
            .section {{ margin: 20px 0; padding: 15px; background: #fafafa; border-radius: 8px; border-left: 4px solid #d4380d; }}
            .metric {{ display: inline-block; margin: 10px 15px; text-align: center; }}
            .metric .value {{ font-size: 24px; font-weight: bold; color: #d4380d; }}
            .metric .label {{ font-size: 12px; color: #999; }}
            .up {{ color: #cf1322; }}
            .down {{ color: #3f8600; }}
            .signal-buy {{ background: #fff1f0; padding: 8px; border-radius: 4px; margin: 5px 0; }}
            .signal-sell {{ background: #f6ffed; padding: 8px; border-radius: 4px; margin: 5px 0; }}
            .footer {{ font-size: 11px; color: #999; margin-top: 30px; text-align: center; }}
        </style></head>
        <body>
            <div class="header">
                <h1>📊 {market_name} 每日市场报告</h1>
                <p>报告日期：{today}</p>
            </div>

            <div class="section">
                <h3>📈 主要指数</h3>
                <div class="metric">
                    <div class="value">--</div>
                    <div class="label">上证指数</div>
                </div>
                <div class="metric">
                    <div class="value">--</div>
                    <div class="label">深证成指</div>
                </div>
                <div class="metric">
                    <div class="value">--</div>
                    <div class="label">创业板指</div>
                </div>
            </div>

            <div class="section">
                <h3>🔥 今日热门概念</h3>
                <p>数据加载中，请登录系统查看完整数据</p>
            </div>

            <div class="section">
                <h3>🚨 交易信号摘要</h3>
                <p>📈 看涨信号：-- 个</p>
                <p>📉 看跌信号：-- 个</p>
            </div>

            <div class="section">
                <h3>💰 北向资金</h3>
                <p>今日净流入：数据加载中...</p>
            </div>

            <div class="section">
                <h3>💡 今日投资建议</h3>
                <p>登录系统查看完整投资建议和个股分析</p>
            </div>

            <div class="footer">
                <p>本报告由 三国演义 · 全球三市数据可视化系统 自动生成</p>
                <p>⚠ 本报告仅供参考，不构成投资建议。投资有风险，入市需谨慎。</p>
                <p>发送时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
        </body>
        </html>
        """

        subject = f"[三国演义] {market_name}每日市场报告 - {today}"
        return await self._send(to_email, subject, body)

    async def send_tracking_recommendations(self, to_email: str) -> tuple[bool, str]:
        """Send investment recommendations for tracked stocks."""
        today = date.today().isoformat()

        body = f"""
        <html>
        <head><style>
            body {{ font-family: 'Microsoft YaHei', Arial, sans-serif; color: #333; }}
            .header {{ background: linear-gradient(135deg, #d4380d, #fa8c16); color: white; padding: 20px; border-radius: 8px; }}
            .rec-card {{ margin: 15px 0; padding: 15px; background: #fff; border: 1px solid #e8e8e8; border-radius: 8px; }}
            .rec-card h4 {{ margin-top: 0; }}
            .score-bar {{ height: 8px; background: #f0f0f0; border-radius: 4px; margin: 8px 0; }}
            .score-fill {{ height: 100%; border-radius: 4px; }}
            .action-buy {{ color: #cf1322; font-weight: bold; }}
            .action-sell {{ color: #3f8600; font-weight: bold; }}
            .action-hold {{ color: #fa8c16; font-weight: bold; }}
            .footer {{ font-size: 11px; color: #999; margin-top: 30px; text-align: center; }}
        </style></head>
        <body>
            <div class="header">
                <h1>🎯 追踪股票投资建议</h1>
                <p>报告日期：{today}</p>
            </div>

            <p>📌 您追踪的股票最新分析建议如下：</p>
            <p style="color: #999;">登录系统生成完整分析报告</p>

            <div class="footer">
                <p>本报告由 三国演义 · 全球三市数据可视化系统 自动生成</p>
                <p>⚠ 本报告仅供参考，不构成投资建议。</p>
                <p>发送时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
        </body>
        </html>
        """

        subject = f"[三国演义] 追踪股票投资建议 - {today}"
        return await self._send(to_email, subject, body)

    async def _send(self, to_email: str, subject: str, html_body: str) -> tuple[bool, str]:
        """Send email via QQ SMTP."""
        settings = self.settings

        if not settings.QQ_EMAIL_SENDER or not settings.QQ_EMAIL_AUTH_CODE:
            return False, "QQ邮箱未配置：请设置 QQ_EMAIL_SENDER 和 QQ_EMAIL_AUTH_CODE"

        try:
            msg = MIMEMultipart("alternative")
            msg["From"] = settings.QQ_EMAIL_SENDER
            msg["To"] = to_email
            msg["Subject"] = subject
            msg.attach(MIMEText(html_body, "html", "utf-8"))

            # Run SMTP in thread (blocking)
            def _send_sync():
                with smtplib.SMTP(settings.QQ_SMTP_SERVER, settings.QQ_SMTP_PORT, timeout=30) as server:
                    server.starttls()
                    server.login(settings.QQ_EMAIL_SENDER, settings.QQ_EMAIL_AUTH_CODE)
                    server.sendmail(settings.QQ_EMAIL_SENDER, to_email, msg.as_string())

            await asyncio.to_thread(_send_sync)
            logger.info(f"Email sent to {to_email}: {subject}")
            return True, "发送成功"

        except smtplib.SMTPAuthenticationError:
            return False, "QQ邮箱认证失败：请检查授权码是否正确"
        except smtplib.SMTPException as e:
            return False, f"SMTP错误：{str(e)}"
        except Exception as e:
            return False, f"发送失败：{str(e)}"
