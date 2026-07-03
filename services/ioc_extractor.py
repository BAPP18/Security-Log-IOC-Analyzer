import re
from datetime import datetime

IOC_PATTERNS = {
    'IPv4': re.compile(
        r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b'
    ),
    'Domain': re.compile(
        r'\b(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}\b'
    ),
    'URL': re.compile(
        r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+[^\s<>"\'(){}|\\^`[\]]*'
    ),
    'Email': re.compile(
        r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    ),
    'MD5': re.compile(
        r'\b[a-fA-F0-9]{32}\b'
    ),
    'SHA1': re.compile(
        r'\b[a-fA-F0-9]{40}\b'
    ),
    'SHA256': re.compile(
        r'\b[a-fA-F0-9]{64}\b'
    ),
}

def extract_iocs(content_lines, source_filename):
    iocs_found = []
    seen_iocs = set()

    for line_number, line in enumerate(content_lines, 1):
        for ioc_type, pattern in IOC_PATTERNS.items():
            matches = pattern.findall(line)
            for match in matches:
                normalized = _normalize_ioc(match, ioc_type)
                if normalized and normalized not in seen_iocs:
                    seen_iocs.add(normalized)
                    iocs_found.append({
                        'value': normalized,
                        'ioc_type': ioc_type,
                        'source_file': source_filename,
                        'line_number': line_number,
                        'detection_time': datetime.utcnow()
                    })
                elif normalized and normalized in seen_iocs:
                    iocs_found.append({
                        'value': normalized,
                        'ioc_type': ioc_type,
                        'source_file': source_filename,
                        'line_number': line_number,
                        'detection_time': datetime.utcnow()
                    })

    return iocs_found

def _normalize_ioc(value, ioc_type):
    value = value.strip()

    if ioc_type == 'IPv4':
        if value.startswith('0') and len(value) > 1 and value[1] != '.':
            return None
        parts = value.split('.')
        if all(0 <= int(p) <= 255 for p in parts):
            return value
        return None

    if ioc_type == 'URL':
        value = value.rstrip('/.,;:!?)')
        return value.lower()

    if ioc_type == 'Domain':
        if value.startswith('www.') and value.count('.') < 2:
            return None
        if value.startswith('.'):
            return None
        return value.lower()

    if ioc_type == 'Email':
        return value.lower()

    if ioc_type in ('MD5', 'SHA1', 'SHA256'):
        return value.lower()

    return value

def classify_ioc_type(ioc_value):
    for ioc_type, pattern in IOC_PATTERNS.items():
        if pattern.fullmatch(ioc_value):
            return ioc_type
    for ioc_type, pattern in IOC_PATTERNS.items():
        if pattern.match(ioc_value):
            return ioc_type
    return 'Unknown'

def count_ioc_types(iocs):
    counts = {
        'IPv4': 0,
        'Domain': 0,
        'URL': 0,
        'Email': 0,
        'MD5': 0,
        'SHA1': 0,
        'SHA256': 0
    }
    for ioc in iocs:
        ioc_type = ioc.ioc_type if hasattr(ioc, 'ioc_type') else ioc.get('ioc_type', 'Unknown')
        if ioc_type in counts:
            counts[ioc_type] += 1
    return counts
