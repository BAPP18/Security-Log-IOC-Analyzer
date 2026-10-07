from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from models import db
from models.analysis import Analysis
from models.ioc import IOC
from utils.helpers import log_activity

ioc_bp = Blueprint("ioc", __name__)

SEVERITIES = ["Critical", "High", "Medium", "Low", "Informational"]


@ioc_bp.route("/search", methods=["GET"])
@login_required
def search():
    query = request.args.get("q", "").strip()
    ioc_type = request.args.get("type", "")
    severity = request.args.get("severity", "")
    source_file = request.args.get("file", "")
    page = request.args.get("page", 1, type=int)
    per_page = 25

    ioc_query = IOC.query

    if query:
        ioc_query = ioc_query.filter(IOC.value.contains(query))
    if ioc_type:
        ioc_query = ioc_query.filter_by(ioc_type=ioc_type)
    if severity in SEVERITIES:
        ioc_query = ioc_query.filter_by(severity=severity)
    if source_file:
        ioc_query = ioc_query.filter_by(source_file=source_file)

    ioc_query = ioc_query.order_by(
        IOC.risk_score.desc(),
        IOC.detection_time.desc(),
    )

    pagination = ioc_query.paginate(page=page, per_page=per_page, error_out=False)
    iocs = pagination.items

    ioc_types = db.session.query(IOC.ioc_type).distinct().order_by(IOC.ioc_type).all()
    ioc_types = [item[0] for item in ioc_types]

    source_files = (
        db.session.query(IOC.source_file)
        .distinct()
        .order_by(IOC.source_file)
        .all()
    )
    source_files = [item[0] for item in source_files]

    return render_template(
        "search.html",
        iocs=iocs,
        pagination=pagination,
        query=query,
        selected_type=ioc_type,
        selected_severity=severity,
        selected_file=source_file,
        severities=SEVERITIES,
        ioc_types=ioc_types,
        source_files=source_files,
    )


@ioc_bp.route("/ioc/<int:ioc_id>")
@login_required
def detail(ioc_id):
    ioc = IOC.query.get_or_404(ioc_id)
    analysis = db.session.get(Analysis, ioc.analysis_id)
    return render_template("ioc_detail.html", ioc=ioc, analysis=analysis)


@ioc_bp.route("/history")
@login_required
def history():
    page = request.args.get("page", 1, type=int)
    analyses = Analysis.query.order_by(Analysis.upload_date.desc()).paginate(
        page=page,
        per_page=15,
        error_out=False,
    )
    return render_template("history.html", analyses=analyses)


@ioc_bp.route("/history/delete/<int:analysis_id>", methods=["POST"])
@login_required
def delete_history(analysis_id):
    analysis = Analysis.query.get_or_404(analysis_id)

    if not current_user.is_admin():
        flash("Only administrators can delete analysis history.", "danger")
        return redirect(url_for("ioc.history"))

    filename = analysis.filename
    db.session.delete(analysis)
    db.session.commit()

    log_activity(
        current_user.id,
        "Delete History",
        f"Deleted analysis: {filename}",
        request.remote_addr,
    )

    flash(f'Analysis "{filename}" has been deleted.', "success")
    return redirect(url_for("ioc.history"))
