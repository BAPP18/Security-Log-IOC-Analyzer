import os
import csv
import pandas as pd
from datetime import datetime
from flask import Blueprint, render_template, request, send_file, current_app, flash, redirect, url_for
from flask_login import login_required, current_user
from models.ioc import IOC
from models.analysis import Analysis
from services.ioc_extractor import count_ioc_types
from utils.helpers import log_activity

export_bp = Blueprint('export', __name__)

@export_bp.route('/export')
@login_required
def index():
    analyses = Analysis.query.order_by(Analysis.upload_date.desc()).all()
    return render_template('export.html', analyses=analyses)

@export_bp.route('/export/excel', methods=['POST'])
@login_required
def export_excel():
    analysis_id = request.form.get('analysis_id', 'all')
    export_folder = current_app.config['EXPORT_FOLDER']

    iocs = _get_iocs_for_export(analysis_id)

    if not iocs:
        flash('No IOCs found to export.', 'warning')
        return redirect(url_for('export.index'))

    data = []
    for ioc in iocs:
        data.append({
            'IOC Value': ioc.value,
            'IOC Type': ioc.ioc_type,
            'Source File': ioc.source_file,
            'Line Number': ioc.line_number,
            'Detection Time': ioc.detection_time.strftime('%Y-%m-%d %H:%M:%S') if ioc.detection_time else ''
        })

    df = pd.DataFrame(data)
    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    filename = f'ioc_export_{timestamp}.xlsx'
    filepath = os.path.join(export_folder, filename)
    df.to_excel(filepath, index=False, engine='openpyxl')

    log_activity(
        current_user.id,
        'Export Report',
        f'Exported {len(iocs)} IOCs to Excel: {filename}',
        request.remote_addr
    )

    flash(f'Successfully exported {len(iocs)} IOCs to Excel.', 'success')
    return send_file(filepath, as_attachment=True, download_name=filename)

@export_bp.route('/export/csv', methods=['POST'])
@login_required
def export_csv():
    analysis_id = request.form.get('analysis_id', 'all')
    export_folder = current_app.config['EXPORT_FOLDER']

    iocs = _get_iocs_for_export(analysis_id)

    if not iocs:
        flash('No IOCs found to export.', 'warning')
        return redirect(url_for('export.index'))

    data = []
    for ioc in iocs:
        data.append({
            'IOC Value': ioc.value,
            'IOC Type': ioc.ioc_type,
            'Source File': ioc.source_file,
            'Line Number': ioc.line_number,
            'Detection Time': ioc.detection_time.strftime('%Y-%m-%d %H:%M:%S') if ioc.detection_time else ''
        })

    df = pd.DataFrame(data)
    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    filename = f'ioc_export_{timestamp}.csv'
    filepath = os.path.join(export_folder, filename)
    df.to_csv(filepath, index=False)

    log_activity(
        current_user.id,
        'Export Report',
        f'Exported {len(iocs)} IOCs to CSV: {filename}',
        request.remote_addr
    )

    flash(f'Successfully exported {len(iocs)} IOCs to CSV.', 'success')
    return send_file(filepath, as_attachment=True, download_name=filename)

def _get_iocs_for_export(analysis_id):
    if analysis_id == 'all':
        return IOC.query.order_by(IOC.detection_time.desc()).all()
    else:
        try:
            analysis = Analysis.query.get(int(analysis_id))
            if analysis:
                return analysis.iocs.order_by(IOC.line_number).all()
        except (ValueError, TypeError):
            pass
    return []
