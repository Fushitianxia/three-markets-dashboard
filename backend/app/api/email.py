"""
Email configuration and push API.
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional
from app.database import get_db
from app.models.market import EmailConfig, EmailLog
from app.services.email_service import EmailService

router = APIRouter()


class EmailConfigRequest(BaseModel):
    email_address: str
    daily_report_enabled: bool = True
    signal_alert_enabled: bool = True
    tracking_alert_enabled: bool = True
    recommendation_enabled: bool = True
    push_time: str = "16:00"


class TestEmailRequest(BaseModel):
    email_address: str


@router.get("/config")
async def get_email_config(db: Session = Depends(get_db)):
    """Get current email configuration."""
    config = db.query(EmailConfig).first()
    if not config:
        return {"configured": False}
    return {"configured": True, "config": config}


@router.post("/config")
async def save_email_config(req: EmailConfigRequest, db: Session = Depends(get_db)):
    """Save or update email configuration."""
    existing = db.query(EmailConfig).first()
    if existing:
        for key, value in req.model_dump().items():
            setattr(existing, key, value)
    else:
        existing = EmailConfig(**req.model_dump())
        db.add(existing)
    db.commit()
    db.refresh(existing)
    return {"status": "saved", "config": existing}


@router.post("/test")
async def send_test_email(req: TestEmailRequest, db: Session = Depends(get_db)):
    """Send a test email."""
    service = EmailService()
    success, msg = await service.send_test(req.email_address)

    log = EmailLog(
        recipient=req.email_address,
        subject="[三国演义] 测试邮件",
        content_type="test",
        status="sent" if success else "failed",
        error_msg=msg if not success else None,
    )
    db.add(log)
    db.commit()

    return {"success": success, "message": msg}


@router.post("/trigger/daily-report")
async def trigger_daily_report(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    market: str = "A",
):
    """Manually trigger daily report email."""
    config = db.query(EmailConfig).first()
    if not config or not config.email_address:
        raise HTTPException(400, "Email config not set")

    service = EmailService()
    background_tasks.add_task(service.send_daily_report, config.email_address, market)
    return {"status": "queued", "message": f"Daily report for {market} market queued"}


@router.post("/trigger/recommendations")
async def trigger_recommendation_email(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """Manually trigger recommendation email for tracked stocks."""
    config = db.query(EmailConfig).first()
    if not config or not config.email_address:
        raise HTTPException(400, "Email config not set")

    service = EmailService()
    background_tasks.add_task(service.send_tracking_recommendations, config.email_address)
    return {"status": "queued", "message": "Recommendation emails queued"}


@router.get("/logs")
async def get_email_logs(
    db: Session = Depends(get_db),
    limit: int = 20,
):
    """Get email send history."""
    return (
        db.query(EmailLog)
        .order_by(EmailLog.sent_at.desc())
        .limit(limit)
        .all()
    )
