import os
import json
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from models import db
from models.analysis import Analysis
from models.ioc import IOC
from services.file_parser import allowed_file, parse_file, get_file_type
from services.ioc_extractor import extract_iocs
from utils.helpers import log_activity

upload_bp = Blueprint('upload', __name__)

@upload_bp.route('/upload', methods=['GET', 'POST'])
@login_required
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file selected.', 'warning')
            return redirect(request.url)

        file = request.files['file']

        if file.filename == '':
            flash('No file selected.', 'warning')
            return redirect(request.url)

        if not allowed_file(file.filename):
            flash('File type not allowed. Supported: TXT, LOG, CSV, XLSX, PDF, DOCX', 'danger')
            return redirect(request.url)

        filename = secure_filename(file.filename)
        upload_folder = current_app.config['UPLOAD_FOLDER']
        filepath = os.path.join(upload_folder, filename)

        file.save(filepath)

        file_size = os.path.getsize(filepath)

        result = parse_file(filepath, filename)

        iocs = extract_iocs(result['content_lines'], filename)

        analysis = Analysis(
            filename=filename,
            file_type=result['file_type'],
            file_size=file_size,
            file_info=json.dumps(result['file_info']),
            total_ioc=len(iocs),
            analyst_id=current_user.id
        )
        db.session.add(analysis)
        db.session.flush()

        for ioc_data in iocs:
            ioc = IOC(
                value=ioc_data['value'],
                ioc_type=ioc_data['ioc_type'],
                source_file=ioc_data['source_file'],
                line_number=ioc_data['line_number'],
                detection_time=ioc_data['detection_time'],
                analysis_id=analysis.id
            )
            db.session.add(ioc)

        db.session.commit()

        log_activity(
            current_user.id,
            'Upload File',
            f'Uploaded and analyzed: {filename} ({len(iocs)} IOCs found)',
            request.remote_addr
        )

        flash(f'File "{filename}" uploaded successfully! Found {len(iocs)} IOCs.', 'success')
        return redirect(url_for('upload.result', analysis_id=analysis.id))

    return render_template('upload.html')

@upload_bp.route('/upload/result/<int:analysis_id>')
@login_required
def result(analysis_id):
    analysis = Analysis.query.get_or_404(analysis_id)
    iocs = analysis.iocs.order_by(IOC.line_number).all()

    ioc_by_type = {}
    for ioc in iocs:
        ioc_type = ioc.ioc_type
        if ioc_type not in ioc_by_type:
            ioc_by_type[ioc_type] = 0
        ioc_by_type[ioc_type] += 1

    file_info = json.loads(analysis.file_info) if analysis.file_info else {}

    return render_template(
        'upload.html',
        analysis=analysis,
        iocs=iocs,
        ioc_by_type=ioc_by_type,
        file_info=file_info,
        show_result=True
    )
