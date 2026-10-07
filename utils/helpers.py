from datetime import datetime, timedelta

from models import db
from models.activity import ActivityLog
from models.analysis import Analysis
from models.ioc import IOC
from models.user import User


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
        ip_address=ip_address,
    )
    db.session.add(log)
    db.session.commit()


def get_dashboard_stats():
    total_analyses = Analysis.query.count()
    total_iocs = IOC.query.count()
    total_occurrences = (
        db.session.query(db.func.coalesce(db.func.sum(IOC.occurrence_count), 0)).scalar()
        or 0
    )
    high_risk_count = IOC.query.filter(IOC.risk_score >= 60).count()
    likely_noise_count = IOC.query.filter(
        IOC.risk_score < 20,
        IOC.confidence_score < 80,
    ).count()

    last_scan = Analysis.query.order_by(Analysis.upload_date.desc()).first()

    ip_count = IOC.query.filter_by(ioc_type="IPv4").count()
    domain_count = IOC.query.filter_by(ioc_type="Domain").count()
    url_count = IOC.query.filter_by(ioc_type="URL").count()
    email_count = IOC.query.filter_by(ioc_type="Email").count()
    hash_count = IOC.query.filter(
        IOC.ioc_type.in_(["MD5", "SHA1", "SHA256"])
    ).count()

    return {
        "total_analyses": total_analyses,
        "total_uploads": total_analyses,
        "total_iocs": total_iocs,
        "total_occurrences": int(total_occurrences),
        "high_risk_count": high_risk_count,
        "likely_noise_count": likely_noise_count,
        "ip_count": ip_count,
        "domain_count": domain_count,
        "url_count": url_count,
        "email_count": email_count,
        "hash_count": hash_count,
        "last_scan": last_scan.upload_date if last_scan else None,
    }


def get_upload_activity(days=30):
    since = datetime.utcnow() - timedelta(days=days)
    return (
        db.session.query(
            db.func.date(Analysis.upload_date).label("date"),
            db.func.count(Analysis.id).label("count"),
        )
        .filter(Analysis.upload_date >= since)
        .group_by(db.func.date(Analysis.upload_date))
        .all()
    )


def get_report_data():
    stats = get_dashboard_stats()
    return {
        "total_iocs": stats["total_iocs"],
        "total_occurrences": stats["total_occurrences"],
        "high_risk_count": stats["high_risk_count"],
        "likely_noise_count": stats["likely_noise_count"],
        "total_analyses": stats["total_analyses"],
        "total_ips": stats["ip_count"],
        "total_domains": stats["domain_count"],
        "total_urls": stats["url_count"],
        "total_emails": stats["email_count"],
        "total_hashes": stats["hash_count"],
    }
