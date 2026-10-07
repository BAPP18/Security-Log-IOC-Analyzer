from datetime import datetime

from . import db


class IOC(db.Model):
    __tablename__ = "iocs"

    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.String(512), nullable=False)
    ioc_type = db.Column(db.String(50), nullable=False)
    source_file = db.Column(db.String(255), nullable=False)
    line_number = db.Column(db.Integer, default=0)
    occurrence_count = db.Column(db.Integer, nullable=False, default=1)

    scope = db.Column(db.String(30), nullable=False, default="unknown")
    confidence_score = db.Column(db.Integer, nullable=False, default=50)
    risk_score = db.Column(db.Integer, nullable=False, default=0)
    severity = db.Column(db.String(20), nullable=False, default="Informational")
    triage_reason = db.Column(db.String(500), nullable=True)
    context = db.Column(db.Text, nullable=True)

    detection_time = db.Column(db.DateTime, default=datetime.utcnow)
    analysis_id = db.Column(
        db.Integer,
        db.ForeignKey("analyses.id"),
        nullable=False,
        index=True,
    )

    __table_args__ = (
        db.Index("ix_ioc_type_value", "ioc_type", "value"),
        db.Index("ix_ioc_risk_score", "risk_score"),
    )
