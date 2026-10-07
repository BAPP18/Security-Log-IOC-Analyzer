import os
from datetime import datetime

import pandas as pd
from flask import Blueprint, current_app, flash, redirect, render_template, request, send_file, url_for
from flask_login import current_user, login_required

from models import db
from models.analysis import Analysis
from models.ioc import IOC
from utils.helpers import log_activity

export_bp = Blueprint("export", __name__)


def _spreadsheet_safe(value):
    if value is None:
        return ""
    text = str(value)
    if text.startswith(("=", "+", "-", "@", "\t", "\r")):
        return "'" + text
    return text


def _ioc_rows(iocs):
    rows = []
    for ioc in iocs:
        rows.append(
            {
                "IOC Value": _spreadsheet_safe(ioc.value),
                "IOC Type": ioc.ioc_type,
                "Severity": ioc.severity,
                "Risk Score": ioc.risk_score,
                "Confidence": ioc.confidence_score,
                "Scope": ioc.scope,
                "Occurrences": ioc.occurrence_count,
                "Source File": _spreadsheet_safe(ioc.source_file),
                "Representative Line": ioc.line_number,
                "Context": _spreadsheet_safe(ioc.context),
                "Triage Reason": _spreadsheet_safe(ioc.triage_reason),
                "Detection Time": (
                    ioc.detection_time.strftime("%Y-%m-%d %H:%M:%S")
                    if ioc.detection_time
                    else ""
                ),
            }
        )
    return rows


@export_bp.route("/export")
@login_required
def index():
    analyses = Analysis.query.order_by(Analysis.upload_date.desc()).all()
    return render_template("export.html", analyses=analyses)


@export_bp.route("/export/excel", methods=["POST"])
@login_required
def export_excel():
    analysis_id = request.form.get("analysis_id", "all")
    iocs = _get_iocs_for_export(analysis_id)

    if not iocs:
        flash("No IOCs found to export.", "warning")
        return redirect(url_for("export.index"))

    os.makedirs(current_app.config["EXPORT_FOLDER"], exist_ok=True)
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filename = f"ioc_triage_{timestamp}.xlsx"
    filepath = os.path.join(current_app.config["EXPORT_FOLDER"], filename)

    pd.DataFrame(_ioc_rows(iocs)).to_excel(filepath, index=False, engine="openpyxl")

    log_activity(
        current_user.id,
        "Export Report",
        f"Exported {len(iocs)} IOC triage records to Excel: {filename}",
        request.remote_addr,
    )
    return send_file(filepath, as_attachment=True, download_name=filename)


@export_bp.route("/export/csv", methods=["POST"])
@login_required
def export_csv():
    analysis_id = request.form.get("analysis_id", "all")
    iocs = _get_iocs_for_export(analysis_id)

    if not iocs:
        flash("No IOCs found to export.", "warning")
        return redirect(url_for("export.index"))

    os.makedirs(current_app.config["EXPORT_FOLDER"], exist_ok=True)
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filename = f"ioc_triage_{timestamp}.csv"
    filepath = os.path.join(current_app.config["EXPORT_FOLDER"], filename)

    pd.DataFrame(_ioc_rows(iocs)).to_csv(filepath, index=False)

    log_activity(
        current_user.id,
        "Export Report",
        f"Exported {len(iocs)} IOC triage records to CSV: {filename}",
        request.remote_addr,
    )
    return send_file(filepath, as_attachment=True, download_name=filename)


def _get_iocs_for_export(analysis_id):
    if analysis_id == "all":
        return IOC.query.order_by(
            IOC.risk_score.desc(),
            IOC.detection_time.desc(),
        ).all()

    try:
        analysis = db.session.get(Analysis, int(analysis_id))
    except (ValueError, TypeError):
        return []

    if not analysis:
        return []

    return analysis.iocs.order_by(
        IOC.risk_score.desc(),
        IOC.line_number,
    ).all()
