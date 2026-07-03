from flask import Blueprint, render_template, request
from flask_login import login_required
from models import db
from models.activity import ActivityLog

activity_bp = Blueprint('activity', __name__)

@activity_bp.route('/activity-log')
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    per_page = 20

    action_filter = request.args.get('action', '')

    query = ActivityLog.query

    if action_filter:
        query = query.filter_by(action=action_filter)

    query = query.order_by(ActivityLog.timestamp.desc())

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    activities = pagination.items

    actions = db.session.query(ActivityLog.action).distinct().order_by(ActivityLog.action).all()
    actions = [a[0] for a in actions]

    return render_template(
        'activity_log.html',
        activities=activities,
        pagination=pagination,
        actions=actions,
        selected_action=action_filter
    )
