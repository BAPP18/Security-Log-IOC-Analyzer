# SOC Analyst Workflow

BlueLens is designed as an IOC triage utility, not as a replacement for a SIEM.

## Intended workflow

### 1. Intake

An analyst receives a firewall, proxy, web, endpoint, email, or other security log extract.

Before upload:

- remove data that is not required for the investigation;
- avoid uploading secrets or credentials;
- use a controlled/private deployment for operational logs.

### 2. Integrity

BlueLens calculates SHA-256 for the uploaded file. This provides a stable reference for the exact analyzed input.

### 3. Parsing

The parser applies limits to reduce excessive memory/CPU use and reports whether content was truncated.

### 4. IOC extraction

Supported candidate types:

- IPv4;
- domain;
- URL;
- email;
- MD5;
- SHA-1;
- SHA-256.

### 5. Normalization and deduplication

Equivalent normalized indicators are stored once per analysis, with occurrence count retained.

This prevents a noisy log from making the dashboard look like thousands of independent threats when the same indicator is repeated.

### 6. Local triage

Each indicator receives:

- scope;
- extraction confidence;
- local risk score;
- severity;
- representative line;
- representative context;
- triage reason.

### 7. Analyst validation

Recommended review order:

1. High/Critical public indicators;
2. indicators repeated across the file;
3. indicators in explicit security-alert context;
4. lower-priority public indicators;
5. private/internal/noise candidates.

Analysts should validate against the original incident evidence and external sources before escalation.

### 8. Export

CSV/XLSX output includes the triage metadata needed for case notes or downstream review. Spreadsheet formula prefixes are neutralized for untrusted text.

## Recommended next SOC capabilities

### Detection engineering

- Sigma rule support;
- normalized event fields;
- ATT&CK technique mapping;
- deterministic detection-rule tests;
- sample benign/adversarial fixtures.

### Threat intelligence

- provider adapters;
- request caching;
- rate-limit handling;
- source timestamps;
- confidence reconciliation;
- STIX 2.1 export;
- TAXII ingestion/export where useful.

### SIEM integration

- JSON/API export;
- Splunk HEC adapter;
- Elastic/OpenSearch ingestion;
- Microsoft Sentinel-compatible output;
- webhook/case-system integration.

### SOC operations

- analyst disposition: true positive / benign / false positive / needs review;
- case ID and investigation notes;
- suppression/allowlist with expiry;
- recurring-indicator correlation;
- SLA timestamps;
- evidence retention policy;
- RBAC beyond Admin/Analyst.
