# Security Policy

BlueLens processes untrusted security logs and documents. Treat uploaded content as potentially sensitive and malformed.

## Production baseline

For any internet-facing deployment:

- set `APP_ENV=production`;
- provide a strong random `SECRET_KEY`;
- keep `SEED_DEMO_USERS=false`;
- use HTTPS and `SESSION_COOKIE_SECURE=true`;
- place the service behind authentication and network controls appropriate for SOC data;
- do not expose raw customer or production logs in a public demo.

The application refuses to use its development fallback secret in production mode.

## Data handling

Uploaded files are used as temporary staging input:

1. the file is saved with a randomized staging name;
2. SHA-256 is calculated for integrity/reference;
3. the parser extracts text needed for IOC analysis;
4. the staged upload is deleted in a `finally` block.

The database stores normalized IOC candidates and a representative context line. Representative context can still contain sensitive log data, so database access must be protected.

## Implemented controls

- password hashing through Werkzeug;
- Flask-Login authentication;
- CSRF protection for state-changing requests;
- HTTP-only / SameSite session cookies;
- production secure-cookie mode;
- randomized upload staging names;
- file-size and parser-work limits;
- file extension allow-list;
- non-root Docker runtime;
- generated production secret on Render;
- CSV/Excel formula-injection neutralization;
- activity logging;
- CI smoke tests and IOC extraction tests.

## Important limitations

BlueLens does not currently provide:

- malware sandboxing;
- antivirus scanning of uploaded files;
- external IOC reputation confirmation;
- MFA/SSO;
- distributed login rate limiting;
- database migrations;
- tenant isolation;
- enterprise secrets management;
- SIEM-grade retention or immutability.

Do not interpret a BlueLens severity score as proof that an indicator is malicious.

## Reporting a security issue

Avoid posting sensitive exploit details, credentials, real log samples, or customer data in a public GitHub issue. Contact the repository owner privately when appropriate.
