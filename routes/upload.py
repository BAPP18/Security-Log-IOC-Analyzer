import hashlib
import json
import os
import uuid

from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename

from models import db
from models.analysis import Analysis
from models.ioc import IOC
from services.file_parser import allowed_file, parse_file
from services.ioc_extractor import extract_iocs
from utils.helpers import log_activity

upload_bp = Blueprint("upload", __name__)


def _sha256_file(filepath):
    digest = hashlib.sha256()
    with open(filepath, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


@upload_bp.route("/upload", methods=["GET", "POST"])
@login_required
def index():
    if request.method == "POST":
        if "file" not in request.files:
            flash("No file selected.", "warning")
            return redirect(request.url)

        file = request.files["file"]

        if file.filename == "":
            flash("No file selected.", "warning")
            return redirect(request.url)

        if not allowed_file(file.filename):
            flash(
                "File type not allowed. Supported: TXT, LOG, CSV, XLSX, PDF, DOCX",
                "danger",
            )
            return redirect(request.url)

        original_filename = secure_filename(file.filename)
        staging_name = f"{uuid.uuid4().hex}_{original_filename}"
        filepath = os.path.join(current_app.config["UPLOAD_FOLDER"], staging_name)

        try:
            file.save(filepath)
            file_size = os.path.getsize(filepath)
            file_sha256 = _sha256_file(filepath)

            result = parse_file(filepath, original_filename)
            iocs = extract_iocs(result["content_lines"], original_filename)

            total_occurrences = sum(
                ioc_data.get("occurrence_count", 1) for ioc_data in iocs
            )
            high_risk_ioc = sum(
                1 for ioc_data in iocs if ioc_data.get("risk_score", 0) >= 60
            )

            analysis = Analysis(
                filename=original_filename,
                file_type=result["file_type"],
                file_size=file_size,
                file_sha256=file_sha256,
                file_info=json.dumps(result["file_info"]),
                total_ioc=len(iocs),
                total_occurrences=total_occurrences,
                high_risk_ioc=high_risk_ioc,
                analyst_id=current_user.id,
            )
            db.session.add(analysis)
            db.session.flush()

            for ioc_data in iocs:
                db.session.add(
                    IOC(
                        value=ioc_data["value"],
                        ioc_type=ioc_data["ioc_type"],
                        source_file=ioc_data["source_file"],
                        line_number=ioc_data["line_number"],
                        occurrence_count=ioc_data["occurrence_count"],
                        scope=ioc_data["scope"],
                        confidence_score=ioc_data["confidence_score"],
                        risk_score=ioc_data["risk_score"],
                        severity=ioc_data["severity"],
                        triage_reason=ioc_data["triage_reason"],
                        context=ioc_data["context"],
                        detection_time=ioc_data["detection_time"],
                        analysis_id=analysis.id,
                    )
                )

            db.session.commit()

            log_activity(
                current_user.id,
                "Upload File",
                (
                    f"Analyzed {original_filename}: {len(iocs)} unique indicators, "
                    f"{total_occurrences} occurrences, {high_risk_ioc} high-risk candidates"
                ),
                request.remote_addr,
            )

            flash(
                (
                    f'File "{original_filename}" analyzed. '
                    f"Found {len(iocs)} unique indicators across "
                    f"{total_occurrences} occurrences."
                ),
                "success",
            )
            return redirect(url_for("upload.result", analysis_id=analysis.id))

        except Exception:
            db.session.rollback()
            current_app.logger.exception("Security log analysis failed")
            flash(
                "The file could not be analyzed safely. Check its format and try again.",
                "danger",
            )
            return redirect(request.url)
        finally:
            # Uploaded logs can contain sensitive operational data. Keep them only
            # long enough to parse and fingerprint them.
            if os.path.exists(filepath):
                os.remove(filepath)

    return render_template("upload.html")


@upload_bp.route("/upload/result/<int:analysis_id>")
@login_required
def result(analysis_id):
    analysis = Analysis.query.get_or_404(analysis_id)
    iocs = analysis.iocs.order_by(
        IOC.risk_score.desc(), IOC.ioc_type, IOC.value
    ).all()

    ioc_by_type = {}
    for ioc in iocs:
        ioc_by_type[ioc.ioc_type] = ioc_by_type.get(ioc.ioc_type, 0) + 1

    file_info = json.loads(analysis.file_info) if analysis.file_info else {}

    return render_template(
        "upload.html",
        analysis=analysis,
        iocs=iocs,
        ioc_by_type=ioc_by_type,
        file_info=file_info,
        show_result=True,
    )
