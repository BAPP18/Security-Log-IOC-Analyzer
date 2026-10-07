from flask import Blueprint, render_template
from flask_login import login_required

from models import db
from models.analysis import Analysis
from models.ioc import IOC
from utils.helpers import get_report_data

report_bp = Blueprint("report", __name__)


@report_bp.route("/report")
@login_required
def index():
    data = get_report_data()

    ioc_type_data = (
        db.session.query(
            IOC.ioc_type,
            db.func.count(IOC.id).label("count"),
        )
        .group_by(IOC.ioc_type)
        .order_by(db.func.count(IOC.id).desc())
        .all()
    )

    analyses_by_date = (
        db.session.query(
            db.func.date(Analysis.upload_date).label("date"),
            db.func.count(Analysis.id).label("count"),
        )
        .group_by(db.func.date(Analysis.upload_date))
        .order_by(db.func.date(Analysis.upload_date).desc())
        .limit(10)
        .all()
    )

    top_iocs = (
        IOC.query.order_by(
            IOC.risk_score.desc(),
            IOC.detection_time.desc(),
        )
        .limit(20)
        .all()
    )

    return render_template(
        "report.html",
        data=data,
        ioc_type_data=ioc_type_data,
        analyses_by_date=analyses_by_date,
        top_iocs=top_iocs,
    )
