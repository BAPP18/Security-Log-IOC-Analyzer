from datetime import datetime
from . import db

class IOC(db.Model):
    __tablename__ = 'iocs'

    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.String(512), nullable=False)
    ioc_type = db.Column(db.String(50), nullable=False)
    source_file = db.Column(db.String(255), nullable=False)
    line_number = db.Column(db.Integer, default=0)
    detection_time = db.Column(db.DateTime, default=datetime.utcnow)
    analysis_id = db.Column(db.Integer, db.ForeignKey('analyses.id'), nullable=False)
