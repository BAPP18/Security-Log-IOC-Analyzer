import os
import json
from flask import Blueprint, render_template
from flask_login import login_required
from utils.helpers import get_dashboard_stats, get_upload_activity
from models.ioc import IOC
from models.analysis import Analysis

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
@login_required
def index():
    stats = get_dashboard_stats()
    upload_activity = get_upload_activity(days=30)

    ioc_by_type = {}
    for ioc_type in ['IPv4', 'Domain', 'URL', 'Email', 'MD5', 'SHA1', 'SHA256']:
        count = IOC.query.filter_by(ioc_type=ioc_type).count()
        if count > 0:
            ioc_by_type[ioc_type] = count

    recent_analyses = Analysis.query.order_by(
        Analysis.upload_date.desc()
    ).limit(5).all()

    labels = [str(a.upload_date.strftime('%Y-%m-%d')) if a.upload_date else '' for a in recent_analyses]
    ioc_counts = [a.total_ioc for a in recent_analyses]

    activity_labels = json.dumps([str(r.date) for r in upload_activity])
    activity_counts = json.dumps([r.count for r in upload_activity])

    ioc_type_labels = json.dumps(list(ioc_by_type.keys()))
    ioc_type_counts = json.dumps(list(ioc_by_type.values()))

    return render_template(
        'dashboard.html',
        stats=stats,
        activity_labels=activity_labels,
        activity_counts=activity_counts,
        ioc_type_labels=ioc_type_labels,
        ioc_type_counts=ioc_type_counts,
        labels=json.dumps(labels),
        ioc_counts=json.dumps(ioc_counts),
        recent_analyses=recent_analyses
    )
