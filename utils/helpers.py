import os
import json
from datetime import datetime, timedelta
from models import db
from models.user import User
from models.analysis import Analysis
from models.ioc import IOC
from models.activity import ActivityLog

def create_default_users():
    """Create deterministic local-demo users.

    This function is intentionally called only when SEED_DEMO_USERS is enabled.
    Production deployments should provision identities separately.
    """
    if User.query.filter_by(username="admin").first() is None:
        admin = User(username="admin", role="admin")
        admin.set_password("admin123")
        db.session.add(admin)

    if User.query.filter_by(username="analyst").first() is None:
        analyst = User(username="analyst", role="analyst")
        analyst.set_password("analyst123")
        db.session.add(analyst)

    db.session.commit()

def log_activity(user_id, action, description=None, ip_address=None):
    log = ActivityLog(
        user_id=user_id,
        action=action,
        description=description,
        ip_address=ip_address
    )
    db.session.add(log)
    db.session.commit()

def get_dashboard_stats():
    total_analyses = Analysis.query.count()
    total_uploads = Analysis.query.count()
    total_iocs = IOC.query.count()

    ioc_by_type = db.session.query(
        IOC.ioc_type, db.func.count(IOC.id)
    ).group_by(IOC.ioc_type).all()

    last_scan = Analysis.query.order_by(Analysis.upload_date.desc()).first()

    ip_count = IOC.query.filter_by(ioc_type='IPv4').count()
    domain_count = IOC.query.filter_by(ioc_type='Domain').count()
    url_count = IOC.query.filter_by(ioc_type='URL').count()
    email_count = IOC.query.filter_by(ioc_type='Email').count()
    hash_count = IOC.query.filter(
        IOC.ioc_type.in_(['MD5', 'SHA1', 'SHA256'])
    ).count()

    return {
        'total_analyses': total_analyses,
        'total_uploads': total_uploads,
        'total_iocs': total_iocs,
        'ip_count': ip_count,
        'domain_count': domain_count,
        'url_count': url_count,
        'email_count': email_count,
        'hash_count': hash_count,
        'last_scan': last_scan.upload_date if last_scan else None
    }

def get_upload_activity(days=30):
    since = datetime.utcnow() - timedelta(days=days)
    activity = db.session.query(
        db.func.date(Analysis.upload_date).label('date'),
        db.func.count(Analysis.id).label('count')
    ).filter(Analysis.upload_date >= since
    ).group_by(db.func.date(Analysis.upload_date)).all()

    return activity

def get_report_data():
    total_iocs = IOC.query.count()
    total_analyses = Analysis.query.count()

    ioc_by_type = db.session.query(
        IOC.ioc_type, db.func.count(IOC.id).label('count')
    ).group_by(IOC.ioc_type).all()

    ioc_counts = {row.ioc_type: row[1] for row in ioc_by_type}

    return {
        'total_iocs': total_iocs,
        'total_analyses': total_analyses,
        'total_ips': ioc_counts.get('IPv4', 0),
        'total_domains': ioc_counts.get('Domain', 0),
        'total_urls': ioc_counts.get('URL', 0),
        'total_emails': ioc_counts.get('Email', 0),
        'total_hashes': ioc_counts.get('MD5', 0) + ioc_counts.get('SHA1', 0) + ioc_counts.get('SHA256', 0)
    }
