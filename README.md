# BlueLens - Security Log & IOC Analyzer

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Flask](https://img.shields.io/badge/Flask-3.0-green)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple)
![License](https://img.shields.io/badge/License-MIT-yellow)

**BlueLens** is a web-based security log analysis tool designed for SOC Analysts, Blue Teams, and Incident Responders. It automates the extraction of Indicators of Compromise (IOCs) from various security log formats, helping security professionals quickly identify and analyze potential threats.

---

## Features

**Multi-Format File Support**
- Upload and analyze TXT, LOG, CSV, XLSX, PDF, and DOCX files

**Automated IOC Extraction**
- IP Addresses (IPv4)
- Domain Names
- URLs
- Email Addresses
- File Hashes (MD5, SHA1, SHA256)

**Dashboard & Analytics**
- Real-time statistics with interactive charts
- IOC distribution by type
- Upload activity tracking
- Recent analysis overview

**Search & Filter**
- Search IOCs by keyword, type, or source file
- Paginated results with filtering capabilities

**Analysis History**
- Complete history of all uploaded files and analysis results
- Role-based deletion (Admin only)

**Export Capabilities**
- Export IOCs to Excel (.xlsx) or CSV format
- Export specific analysis or all data

**Reporting**
- Comprehensive IOC summary reports
- IOC type distribution charts
- Recently detected IOCs list

**Activity Logging**
- Track all user activities (login, upload, export, delete)
- Filterable activity history

**Role-Based Access Control**
- **Admin**: Full access including history deletion
- **Analyst**: Upload, analyze, search, and export

---

## Folder Structure

```
bluelens/
├── app.py                  # Application entry point
├── config.py               # Configuration settings
├── requirements.txt        # Python dependencies
├── README.md               # Project documentation
├── database/               # SQLite database storage
│   └── bluelens.db
├── uploads/                # Uploaded files storage
├── exports/                # Exported reports storage
├── reports/                # Generated report files
├── logs/                   # Application logs
├── sample_logs/            # Sample log files for testing
│   ├── apache.log
│   ├── windows_log.txt
│   ├── firewall.log
│   ├── phishing_email.txt
│   └── suspicious_urls.csv
├── screenshots/            # Application screenshots
├── static/
│   ├── css/
│   │   └── style.css       # Custom styles
│   └── js/
│       └── main.js         # Custom JavaScript
├── templates/              # Jinja2 HTML templates
│   ├── base.html
│   ├── login.html
│   ├── dashboard.html
│   ├── upload.html
│   ├── search.html
│   ├── ioc_detail.html
│   ├── history.html
│   ├── report.html
│   ├── export.html
│   ├── activity_log.html
│   ├── 404.html
│   └── 500.html
├── models/                 # SQLAlchemy ORM models
│   ├── __init__.py
│   ├── user.py
│   ├── analysis.py
│   ├── ioc.py
│   └── activity.py
├── routes/                 # Flask route blueprints
│   ├── __init__.py
│   ├── auth.py
│   ├── dashboard.py
│   ├── upload.py
│   ├── ioc_routes.py
│   ├── export.py
│   ├── report.py
│   └── activity_log.py
├── services/               # Business logic services
│   ├── __init__.py
│   ├── file_parser.py      # File parsing (TXT, CSV, XLSX, PDF, DOCX)
│   └── ioc_extractor.py    # IOC extraction using regex
└── utils/                  # Utility functions
    ├── __init__.py
    └── helpers.py           # Database helpers and statistics
```

---

## Technology Stack

| Category       | Technology            |
|----------------|-----------------------|
| Backend        | Python 3, Flask 3.0   |
| Frontend       | HTML5, Bootstrap 5.3  |
| Database       | SQLite                |
| ORM            | SQLAlchemy            |
| Authentication | Flask-Login           |
| Forms          | Flask-WTF             |
| Charts         | Chart.js 4.4          |
| Icons          | Bootstrap Icons       |
| File Parsing   | Pandas, PyPDF2, python-docx, openpyxl |
| Data Export    | Pandas, openpyxl      |

---

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/bluelens.git
cd bluelens
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python app.py
```

4. Open your browser and navigate to:
```
http://127.0.0.1:5000
```

### Default Credentials

| Role     | Username | Password   |
|----------|----------|------------|
| Admin    | admin    | admin123   |
| Analyst  | analyst  | analyst123 |

---

## Usage

1. **Login** using the default credentials
2. **Upload** a security log file (TXT, LOG, CSV, XLSX, PDF, or DOCX)
3. **Review** the automatically extracted IOCs displayed in a table
4. **Search** for specific IOCs using keywords, type, or source file filters
5. **Export** results to Excel or CSV for further analysis
6. **Monitor** activity through the dashboard and activity log

### Testing with Sample Logs

The `sample_logs/` folder contains pre-made security log files you can use to test the application:

- `apache.log` - Web server access logs with brute force and exploit attempts
- `windows_log.txt` - Windows security event logs with various attack patterns
- `firewall.log` - Firewall traffic logs showing blocked malicious connections
- `phishing_email.txt` - Simulated phishing email with malicious indicators
- `suspicious_urls.csv` - CSV file containing categorized malicious URLs

---

## Screenshots

Screenshots should be placed in the `screenshots/` directory. Recommended screenshots to capture:

1. **Login Page** - BlueLens login interface with demo credentials
![Uploading image.png…]()
2. **Dashboard** - Main dashboard showing statistics and charts
3. **Upload & Analyze** - File upload page with analysis results
4. **Search IOCs** - Search interface with filtered results
5. **IOC Detail** - Detailed view of a single IOC
6. **Analysis History** - History page showing all analyses
7. **Reports** - Report page with IOC distribution charts
8. **Export** - Export page with format selection
9. **Activity Log** - Activity monitoring page
10. **Mobile View** - Responsive design demonstration

---

## Future Improvements

- [ ] VirusTotal/AbuseIPDB API integration for IOC enrichment
- [ ] PDF report generation (python-pptx, ReportLab)
- [ ] YARA rule integration for advanced malware detection
- [ ] Real-time log monitoring with WebSocket support
- [ ] Multi-user registration with email verification
- [ ] Dark mode / light mode toggle
- [ ] API endpoints for third-party integration
- [ ] IOC whitelisting/blacklisting
- [ ] Graph visualization of IOC relationships
- [ ] Integration with SIEM systems (Splunk, ELK)
- [ ] Email alerting for critical IOC detections
- [ ] File quarantine and sandbox analysis integration

---

## Security Considerations

- All passwords are hashed using Werkzeug's secure hashing
- File uploads are restricted to allowed types and size limits
- User authentication required for all operations
- Role-based access control for sensitive operations
- Activity logging for audit trail

---

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## Author
BAP & OC
