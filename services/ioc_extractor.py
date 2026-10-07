import ipaddress
import re
from datetime import datetime
from urllib.parse import urlsplit, urlunsplit

IOC_PATTERNS = {
    "URL": re.compile(r"https?://[^\s<>\"'(){}|\\^\x60\[\]]+", re.IGNORECASE),
    "Email": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
    "SHA256": re.compile(r"\b[a-fA-F0-9]{64}\b"),
    "SHA1": re.compile(r"\b[a-fA-F0-9]{40}\b"),
    "MD5": re.compile(r"\b[a-fA-F0-9]{32}\b"),
    "IPv4": re.compile(
        r"\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}"
        r"(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b"
    ),
    "Domain": re.compile(
        r"\b(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+"
        r"[a-zA-Z]{2,}\b"
    ),
}

_INTERNAL_SUFFIXES = (".local", ".lan", ".internal", ".localhost", ".home", ".corp")
_FILELIKE_SUFFIXES = {
    "exe", "dll", "sys", "log", "txt", "json", "xml", "yaml", "yml", "csv",
    "xlsx", "docx", "pptx", "pdf", "png", "jpg", "jpeg", "gif", "js", "css",
    "html", "htm", "php", "py", "ps1", "bat", "cmd", "sh",
}

_SUSPICIOUS_TERMS = (
    "malicious", "malware", "phishing", "exploit", "ransomware", "c2",
    "command and control", "beacon", "brute force", "credential", "attack",
    "suspicious", "powershell", "encodedcommand", "mimikatz", "webshell",
)
_SECURITY_ACTION_TERMS = (
    "blocked", "denied", "dropped", "reject", "failed login", "authentication failure",
    "unauthorized", "intrusion", "alert",
)
_BENIGN_CONTEXT_TERMS = (
    "example", "documentation", "sample data", "healthcheck", "localhost",
    "unit test", "test fixture",
)


def extract_iocs(content_lines, source_filename):
    """Extract and aggregate IOC candidates for SOC triage.

    The result is intentionally a *candidate triage* view, not a threat-intelligence
    verdict. Risk is derived only from local context and indicator characteristics.
    """
    aggregated = {}
    detected_at = datetime.utcnow()

    for line_number, raw_line in enumerate(content_lines, 1):
        line = str(raw_line)
        protected_spans = []

        for ioc_type, pattern in IOC_PATTERNS.items():
            for match in pattern.finditer(line):
                if ioc_type in {"IPv4", "Domain"} and _overlaps(
                    match.span(), protected_spans
                ):
                    continue

                normalized = _normalize_ioc(match.group(0), ioc_type)
                if not normalized:
                    continue

                if ioc_type in {"URL", "Email"}:
                    protected_spans.append(match.span())

                scope = _classify_scope(normalized, ioc_type)
                confidence = _confidence_score(ioc_type, scope)
                risk, reason = _risk_score(ioc_type, scope, line)
                key = (ioc_type, normalized)

                candidate = {
                    "value": normalized,
                    "ioc_type": ioc_type,
                    "source_file": source_filename,
                    "line_number": line_number,
                    "occurrence_count": 1,
                    "scope": scope,
                    "confidence_score": confidence,
                    "risk_score": risk,
                    "severity": severity_for_score(risk),
                    "triage_reason": reason,
                    "context": _clean_context(line),
                    "detection_time": detected_at,
                }

                if key not in aggregated:
                    aggregated[key] = candidate
                    continue

                existing = aggregated[key]
                existing["occurrence_count"] += 1

                # Keep the most suspicious representative occurrence/context.
                if risk > existing["risk_score"]:
                    existing["risk_score"] = risk
                    existing["severity"] = severity_for_score(risk)
                    existing["triage_reason"] = reason
                    existing["context"] = _clean_context(line)
                    existing["line_number"] = line_number

                existing["confidence_score"] = max(
                    existing["confidence_score"], confidence
                )

    for candidate in aggregated.values():
        repeats = candidate["occurrence_count"] - 1
        if repeats > 0:
            candidate["risk_score"] = min(
                100, candidate["risk_score"] + min(10, repeats * 2)
            )
            candidate["severity"] = severity_for_score(candidate["risk_score"])
            candidate["triage_reason"] = (
                f'{candidate["triage_reason"]}; observed '
                f'{candidate["occurrence_count"]} times'
            )

    return sorted(
        aggregated.values(),
        key=lambda item: (-item["risk_score"], item["ioc_type"], item["value"]),
    )


def _overlaps(span, protected_spans):
    start, end = span
    return any(start < p_end and end > p_start for p_start, p_end in protected_spans)


def _normalize_ioc(value, ioc_type):
    value = value.strip()

    if ioc_type == "IPv4":
        try:
            return str(ipaddress.ip_address(value))
        except ValueError:
            return None

    if ioc_type == "URL":
        value = value.rstrip(".,;:!?)")
        try:
            parts = urlsplit(value)
            if parts.scheme.lower() not in {"http", "https"} or not parts.hostname:
                return None
            hostname = parts.hostname.lower()
            port = f":{parts.port}" if parts.port else ""
            # Deliberately omit userinfo from normalized output to avoid retaining
            # credentials accidentally embedded in a URL.
            return urlunsplit(
                (
                    parts.scheme.lower(),
                    f"{hostname}{port}",
                    parts.path,
                    parts.query,
                    parts.fragment,
                )
            )
        except (ValueError, UnicodeError):
            return None

    if ioc_type == "Domain":
        value = value.rstrip(".").lower()
        suffix = value.rsplit(".", 1)[-1]
        if suffix in _FILELIKE_SUFFIXES:
            return None
        if value.startswith(".") or ".." in value:
            return None
        return value

    if ioc_type == "Email":
        local, separator, domain = value.partition("@")
        if not separator or not local or not domain:
            return None
        return f"{local.lower()}@{domain.lower()}"

    if ioc_type in {"MD5", "SHA1", "SHA256"}:
        value = value.lower()
        # Common placeholders such as all-zero hashes are not actionable IOCs.
        if len(set(value)) <= 2:
            return None
        return value

    return value


def _classify_scope(value, ioc_type):
    if ioc_type == "IPv4":
        return _ip_scope(value)

    if ioc_type == "URL":
        try:
            host = urlsplit(value).hostname or ""
            try:
                return _ip_scope(host)
            except ValueError:
                return "internal" if host.endswith(_INTERNAL_SUFFIXES) else "public"
        except ValueError:
            return "unknown"

    if ioc_type == "Domain":
        return "internal" if value.endswith(_INTERNAL_SUFFIXES) else "public"

    if ioc_type == "Email":
        domain = value.rsplit("@", 1)[-1]
        return "internal" if domain.endswith(_INTERNAL_SUFFIXES) else "public"

    if ioc_type in {"MD5", "SHA1", "SHA256"}:
        return "artifact"

    return "unknown"


def _ip_scope(value):
    ip = ipaddress.ip_address(value)
    if ip.is_loopback:
        return "loopback"
    if ip.is_link_local:
        return "link-local"
    if ip.is_multicast:
        return "multicast"
    if ip.is_unspecified:
        return "unspecified"
    if ip.is_private:
        return "private"
    if ip.is_reserved:
        return "reserved"
    if not ip.is_global:
        return "non-global"
    return "public"


def _confidence_score(ioc_type, scope):
    base = {
        "URL": 95,
        "Email": 90,
        "IPv4": 95,
        "Domain": 85,
        "MD5": 98,
        "SHA1": 98,
        "SHA256": 99,
    }.get(ioc_type, 60)

    if scope in {"loopback", "link-local", "unspecified", "internal"}:
        base -= 20
    elif scope in {"private", "reserved", "non-global", "multicast"}:
        base -= 10

    return max(0, min(100, base))


def _risk_score(ioc_type, scope, context):
    score = {
        "URL": 35,
        "Domain": 25,
        "IPv4": 30,
        "Email": 20,
        "MD5": 35,
        "SHA1": 35,
        "SHA256": 40,
    }.get(ioc_type, 10)

    reasons = [f"{ioc_type} candidate", f"scope={scope}"]

    if scope in {
        "private", "internal", "loopback", "link-local", "reserved",
        "non-global", "multicast", "unspecified",
    }:
        score -= 20
        reasons.append("non-public indicator reduces standalone risk")

    lower_context = context.lower()
    suspicious = [term for term in _SUSPICIOUS_TERMS if term in lower_context]
    security_actions = [
        term for term in _SECURITY_ACTION_TERMS if term in lower_context
    ]
    benign = [term for term in _BENIGN_CONTEXT_TERMS if term in lower_context]

    if suspicious:
        score += min(35, 20 + (5 * len(set(suspicious))))
        reasons.append("suspicious context: " + ", ".join(sorted(set(suspicious))[:3]))

    if security_actions:
        score += min(20, 10 + (3 * len(set(security_actions))))
        reasons.append(
            "security-event context: "
            + ", ".join(sorted(set(security_actions))[:3])
        )

    if benign:
        score -= 20
        reasons.append("test/documentation context lowers priority")

    score = max(0, min(100, score))
    return score, "; ".join(reasons)


def _clean_context(line, limit=500):
    return " ".join(line.strip().split())[:limit]


def severity_for_score(score):
    if score >= 80:
        return "Critical"
    if score >= 60:
        return "High"
    if score >= 40:
        return "Medium"
    if score >= 20:
        return "Low"
    return "Informational"


def classify_ioc_type(ioc_value):
    for ioc_type, pattern in IOC_PATTERNS.items():
        if pattern.fullmatch(ioc_value):
            return ioc_type
    return "Unknown"


def count_ioc_types(iocs):
    counts = {
        "IPv4": 0,
        "Domain": 0,
        "URL": 0,
        "Email": 0,
        "MD5": 0,
        "SHA1": 0,
        "SHA256": 0,
    }
    for ioc in iocs:
        ioc_type = (
            ioc.ioc_type
            if hasattr(ioc, "ioc_type")
            else ioc.get("ioc_type", "Unknown")
        )
        if ioc_type in counts:
            counts[ioc_type] += 1
    return counts
