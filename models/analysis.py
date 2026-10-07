from datetime import datetime

from . import db


class Analysis(db.Model):
    __tablename__ = "analyses"

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    file_type = db.Column(db.String(10), nullable=False)
    file_size = db.Column(db.Integer, default=0)
    file_sha256 = db.Column(db.String(64), nullable=True, index=True)
    file_info = db.Column(db.Text, nullable=True)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)

    # total_ioc = unique normalized indicators.
    total_ioc = db.Column(db.Integer, default=0)
    total_occurrences = db.Column(db.Integer, default=0)
    high_risk_ioc = db.Column(db.Integer, default=0)

    analyst_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    iocs = db.relationship(
        "IOC",
        backref="analysis",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )
