# OpenREM User Guide
## Comprehensive Guide to Radiation Exposure Monitoring

### Table of Contents
1. [Introduction](#introduction)
2. [System Overview](#system-overview)
3. [Installation Guide](#installation-guide)
4. [Configuration](#configuration)
5. [User Management](#user-management)
6. [Using the Web Interface](#using-the-web-interface)
7. [Data Import and Processing](#data-import-and-processing)
8. [Exporting Data](#exporting-data)
9. [Administration Tasks](#administration-tasks)
10. [Troubleshooting](#troubleshooting)
11. [System Maintenance](#system-maintenance)

---

## Introduction

OpenREM (Open Radiation Exposure Monitoring) is a Django-based web application designed to extract, store, and export radiation exposure monitoring information, primarily from DICOM files. It provides comprehensive dose tracking capabilities for medical physics departments and healthcare facilities.

### Key Features
- **Multi-modality support**: CT, Fluoroscopy, and Mammography
- **DICOM data extraction**: Automated processing of Radiation Dose Structured Reports (RDSR)
- **Web-based interface**: User-friendly browsing, filtering, and study management
- **Data export capabilities**: CSV and Excel (XLSX) formats
- **User authentication**: Role-based access control
- **Background processing**: Celery task queue for imports and exports
- **Patient size data import**: CSV-based height/weight data integration

### Supported Equipment
- **CT**: Siemens, Philips, and GE RDSR and Enhanced SR
- **Fluoroscopy**: Siemens Artis Zee RDSR
- **Mammography**: GE Senographe DS (specific software versions)
- **Philips CT**: Dedicated support for Philips dose reports

---

## System Overview

### Architecture
OpenREM is built on the Django web framework and consists of several key components:

- **Django Web Application**: Main application logic and web interface
- **Database**: Stores radiation dose data (SQLite, MySQL, or PostgreSQL)
- **Celery Task Queue**: Handles background processing (requires RabbitMQ)
- **DICOM Extractors**: Modules for processing different DICOM formats
- **Web Interface**: User-friendly interface for data viewing and management

### Directory Structure
```
OpenREM/
├── openrem/
│   ├── openremproject/          # Django project settings
│   │   ├── settings.py          # Main configuration
│   │   ├── local_settings.py    # Local/environment-specific settings
│   │   └── urls.py              # URL routing
│   ├── remapp/                  # Main application
│   │   ├── models.py            # Database models
│   │   ├── views.py             # Web interface logic
│   │   ├── extractors/          # DICOM processing modules
│   │   ├── exports/             # Data export functionality
│   │   ├── templates/           # HTML templates
│   │   └── static/              # CSS, JavaScript, images
│   └── scripts/                 # Command-line import tools
├── docs/                        # Documentation
└── requirements.txt             # Python dependencies
```

---

## Installation Guide

### Prerequisites

#### 1. Python 2.7.x
- **Linux**: Usually pre-installed
- **Windows**: Download from https://www.python.org/downloads
- Add Python and Scripts folder to system PATH (Windows)

#### 2. Setuptools and pip
**Linux:**
```bash
sudo apt-get install python-pip
```

**Windows:**
1. Download [get-pip.py](https://bootstrap.pypa.io/get-pip.py)
2. Run: `python get-pip.py`

#### 3. RabbitMQ Message Broker
Required for exports and background tasks. Install according to your operating system documentation.

### Installation Steps

#### 1. Install OpenREM
```bash
pip install OpenREM
```

#### 2. Create Database
**SQLite (for testing):**
```bash
python manage.py syncdb --migrate
```

**MySQL/PostgreSQL:**
Configure database settings in `local_settings.py` first, then run syncdb.

#### 3. Create Superuser
```bash
python manage.py createsuperuser
```

#### 4. Collect Static Files
```bash
python manage.py collectstatic
```

### Database Configuration Options

#### SQLite (Development/Testing)
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': '/path/to/openrem.db',
    }
}
```

#### MySQL (Production)
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'openrem_db',
        'USER': 'openrem_user',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

#### PostgreSQL (Production)
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'openrem_db',
        'USER': 'openrem_user',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

---

## Configuration

### Essential Configuration Files

#### 1. local_settings.py
This file contains environment-specific settings that override defaults in `settings.py`:

```python
LOCAL_SETTINGS = True
from settings import *

# Database configuration
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': '/path/to/openrem.db',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}

# Media files (exports, uploads)
MEDIA_ROOT = '/path/to/media/'

# Static files collection directory
STATIC_ROOT = '/path/to/static/'

# Security key (generate a unique one)
SECRET_KEY = 'your-unique-secret-key-here'

# Debug mode (set to False in production)
DEBUG = False

# Allowed hosts (required when DEBUG=False)
ALLOWED_HOSTS = [
    'your-server-domain.com',
    '127.0.0.1',
    'localhost',
]
```

#### 2. Celery Configuration
In `settings.py`, Celery is configured for background tasks:

```python
# RabbitMQ broker settings
BROKER_URL = 'amqp://guest:guest@localhost//'
CELERY_RESULT_BACKEND = 'amqp'

# Serialization settings
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
```

### Web Server Configuration

#### Development Server
```bash
python manage.py runserver 8000
```
Access at: http://localhost:8000/openrem

#### Apache Production Setup (Windows)
1. Install Apache and mod_wsgi
2. Configure Apache `httpd.conf`:
```apache
LoadModule wsgi_module modules/mod_wsgi.so

WSGIScriptAlias / "c:/Python27/Lib/site-packages/openrem/openrem/wsgi.py"
WSGIPythonPath "c:/Python27/Lib/site-packages/openrem"

<Directory "c:/Python27/Lib/site-packages/openrem">
    <Files wsgi.py>
        Require all granted
    </Files>
</Directory>
```

---

## User Management

### User Groups and Permissions

OpenREM uses Django's built-in authentication system with custom permission groups:

#### 1. admingroup
- Full system access
- User management
- System configuration
- Data import/export
- Study deletion

#### 2. exportgroup  
- Data export capabilities
- Study viewing and filtering
- Cannot delete studies or manage users

#### 3. Regular Users
- Study viewing and filtering only
- No export or administrative capabilities

### Creating Users

#### Via Django Admin Interface
1. Navigate to `/admin/` (requires superuser login)
2. Go to **Users** section
3. Click **Add user**
4. Set username and password
5. Add user to appropriate groups

#### Via Command Line
```bash
python manage.py createsuperuser
```

### Managing User Permissions

#### Add User to Export Group
```python
# In Django shell (python manage.py shell)
from django.contrib.auth.models import User, Group

user = User.objects.get(username='username')
export_group = Group.objects.get(name='exportgroup')
user.groups.add(export_group)
```

#### Add User to Admin Group
```python
user = User.objects.get(username='username')
admin_group = Group.objects.get(name='admingroup')
user.groups.add(admin_group)
```

---

## Using the Web Interface

### Navigation

#### Home Page
- Overview of all studies by modality
- Quick access to recent imports
- Summary statistics
- Links to detailed views

#### Main Navigation Menu
- **Home**: Overview dashboard
- **CT**: CT study listing and filtering
- **Fluoroscopy**: Fluoroscopy study management
- **Mammography**: Mammography study access
- **Exports**: Export management (requires permissions)
- **Admin**: Administrative functions (requires permissions)

### Study Browsing and Filtering

#### Available Filters
All modality views support filtering by:
- **Date Range**: From/to dates (format: YYYY-MM-DD)
- **Station Name**: Equipment identifier
- **Study Description**: Procedure description
- **Accession Number**: Study identifier
- **Patient Age**: Age-based filtering
- **Modality Model**: Equipment model
- **Patient Size**: Height/weight data (if available)

#### Filter Usage
1. Navigate to desired modality view (CT, Fluoroscopy, Mammography)
2. Use filter panel on the right side
3. Enter search terms (case-insensitive, partial matching)
4. Multiple filters can be used simultaneously
5. Results update automatically

#### Study Details
Click on any study description (blue link) to view:
- **Study Information**: Date, time, description, accession number
- **Patient Information**: Age, size data (anonymized)
- **Equipment Details**: Station name, model, software version
- **Dose Information**: Modality-specific dose metrics
- **Series Details**: Individual acquisition parameters
- **Test Patient Indicators**: Automatic detection of test/QA procedures

### Study Management

#### Deleting Studies
1. Navigate to study detail view
2. Click **Delete Study** button (requires admin permissions)
3. Confirm deletion in popup dialog
4. Study and all associated data will be permanently removed

---

## Data Import and Processing

### Supported File Types

#### 1. DICOM Radiation Dose Structured Reports (RDSR)
- **CT**: Siemens, Philips, GE RDSR and Enhanced SR
- **Fluoroscopy**: Siemens Artis Zee RDSR
- Primary source for dose information

#### 2. DICOM Image Files
- **Mammography**: GE Senographe DS images
- **Philips CT**: Dose report images

#### 3. CSV Files
- **Patient Size Data**: Height and weight information
- **Study Imports**: Bulk study information

### Command Line Import Tools

#### 1. openrem_rdsr.py
Import DICOM Radiation Dose Structured Reports:
```bash
openrem_rdsr.py /path/to/dicom/file.dcm
openrem_rdsr.py /path/to/dicom/folder/*.dcm
```

**Supported Modalities:**
- CT: Siemens, Philips, GE RDSR and Enhanced SR
- Fluoroscopy: Siemens Artis Zee RDSR

#### 2. openrem_mg.py
Import mammography DICOM images:
```bash
openrem_mg.py /path/to/mammography/image.dcm
```

**Supported Equipment:**
- GE Senographe DS (software versions ADS_43.10.1 and ADS_53.10.10)

#### 3. openrem_ctphilips.py
Import Philips CT dose reports:
```bash
openrem_ctphilips.py /path/to/philips/dose/report.dcm
```

**Supported Equipment:**
- Philips Gemini TF PET-CT v2.3.0
- Brilliance BigBore v3.5.4.17001

#### 4. openrem_ptsizecsv.py
Import patient size data from CSV:
```bash
openrem_ptsizecsv.py /path/to/patient/size/data.csv
```

### Batch Processing

#### Importing Multiple Files
```bash
# Import all RDSR files in a directory
openrem_rdsr.py /path/to/dicom/directory/*.dcm

# Import specific file types
openrem_rdsr.py /path/to/studies/CT*.dcm
openrem_mg.py /path/to/mammography/MG*.dcm
```

#### Automated Import Scripts
Create shell scripts for regular imports:

**Linux/Mac:**
```bash
#!/bin/bash
# daily_import.sh
cd /path/to/openrem
source venv/bin/activate
openrem_rdsr.py /incoming/dicom/*.dcm
```

**Windows:**
```cmd
REM daily_import.bat
cd C:\path\to\openrem
openrem_rdsr.py C:\incoming\dicom\*.dcm
```

### Web-Based Import

#### Patient Size Data Import
1. Navigate to **Admin** → **Size Upload**
2. Select CSV file with patient size data
3. Configure column mapping:
   - Height field
   - Weight field
   - Patient ID field
   - ID type (Accession Number or Study Instance UID)
4. Process file and monitor progress
5. Review import logs for errors

#### CSV File Format
```csv
AccessionNumber,Height,Weight
12345,175,70
67890,165,55
```

---

## Exporting Data

### Export Types

#### 1. CT Exports
**Basic CSV Export:**
- Single sheet with essential dose metrics
- Study-level summaries
- Compatible with statistical software

**Advanced XLSX Export:**
- Multiple sheets with detailed information
- Summary sheet with protocol frequency
- Individual sheets per protocol
- Comprehensive dose and technical parameters

#### 2. Fluoroscopy Export
**Basic CSV Export:**
- Procedure summaries
- Dose area product and cumulative dose
- Equipment and technique parameters

#### 3. Mammography Exports
**Standard CSV Export:**
- Basic mammography dose information
- View-specific data
- Equipment parameters

**NHSBSP CSV Export:**
- Specialized format for NHS Breast Screening Programme
- Compliance with NHSBSP reporting requirements
- Additional quality metrics

### Export Process

#### Web Interface Export
1. Navigate to desired modality view (CT, Fluoroscopy, Mammography)
2. Apply filters if needed to limit export scope
3. Click appropriate export link (requires export permissions)
4. Monitor export progress on **Exports** page
5. Download completed file when ready
6. Clean up old exports when no longer needed

#### Export Management
The **Exports** page shows:
- **Active Exports**: Currently processing
- **Completed Exports**: Ready for download
- **Export Details**: Date, type, record count, processing time
- **Download Links**: Direct file access
- **Delete Options**: Cleanup old exports

#### Export File Locations
Completed exports are stored in:
```
MEDIA_ROOT/exports/YYYY/MM/DD/
```

### Large Export Considerations

#### Memory Limitations
- Large exports (>5000 studies) may exhaust system memory
- Consider filtering by date ranges for large datasets
- XLSX exports are more memory-intensive than CSV

#### Performance Optimization
- Export during off-peak hours
- Use database indexing for better performance
- Monitor disk space for export storage

---

## Administration Tasks

### Database Maintenance

#### Regular Backups
**SQLite:**
```bash
cp /path/to/openrem.db /backup/location/openrem_$(date +%Y%m%d).db
```

**MySQL:**
```bash
mysqldump -u openrem_user -p openrem_db > openrem_backup_$(date +%Y%m%d).sql
```

**PostgreSQL:**
```bash
pg_dump -U openrem_user openrem_db > openrem_backup_$(date +%Y%m%d).sql
```

#### Database Migrations
When upgrading OpenREM versions:
```bash
python manage.py syncdb --migrate
```

### System Monitoring

#### Log Files
Monitor Django and Celery logs:
- Django logs: Configured in `settings.py` LOGGING section
- Celery logs: Use `celery worker --loglevel=info`
- Import logs: Stored in `MEDIA_ROOT/sizelogs/`

#### Background Tasks
Start Celery worker for background processing:
```bash
celery -A openremproject worker --loglevel=info
```

#### System Health Checks
- Monitor disk space in `MEDIA_ROOT`
- Check database connection and performance
- Verify RabbitMQ message broker status
- Review user access logs

### Configuration Management

#### Settings Version Control
- Keep `local_settings.py` in version control (without sensitive data)
- Use environment variables for sensitive settings
- Document configuration changes

#### Security Considerations
- Change default SECRET_KEY
- Use HTTPS in production
- Implement proper firewall rules
- Regular security updates for dependencies

---

## Troubleshooting

### Common Issues

#### 1. Import Failures
**Symptoms:**
- Files not appearing in web interface
- Error messages during import
- Incomplete dose data

**Solutions:**
- Check file permissions and paths
- Verify DICOM file integrity
- Review import script output for errors
- Check database connection

#### 2. Web Interface Access Issues
**Symptoms:**
- 500 Internal Server Error
- Static files not loading
- Login problems

**Solutions:**
- Check `DEBUG = True` in `local_settings.py` for detailed errors
- Verify `ALLOWED_HOSTS` configuration
- Run `python manage.py collectstatic`
- Check web server configuration

#### 3. Export Problems
**Symptoms:**
- Exports stuck in processing
- Memory errors during large exports
- Empty export files

**Solutions:**
- Restart Celery worker: `celery -A openremproject worker --loglevel=info`
- Check available memory and disk space
- Reduce export scope with filters
- Monitor Celery logs for errors

#### 4. Database Issues
**Symptoms:**
- Slow query performance
- Database connection errors
- Data inconsistencies

**Solutions:**
- Optimize database indexes
- Check database server status
- Run `python manage.py syncdb --migrate`
- Review database configuration

### Error Diagnosis

#### Django Debug Mode
Enable debug mode for detailed error information:
```python
# In local_settings.py
DEBUG = True
```

#### Log Analysis
Check Django logs for error details:
```python
# In settings.py, modify LOGGING configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': '/path/to/django.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
```

#### Database Query Analysis
Use Django shell for direct database access:
```bash
python manage.py shell

# In shell:
from remapp.models import General_study_module_attributes
studies = General_study_module_attributes.objects.all()
print(f"Total studies: {studies.count()}")
```

### Performance Optimization

#### Database Optimization
- Add indexes to frequently queried fields
- Regular database maintenance (VACUUM, ANALYZE)
- Monitor query performance

#### Application Tuning
- Use database connection pooling
- Implement caching for frequently accessed data
- Optimize static file serving

---

## System Maintenance

### Regular Maintenance Tasks

#### Daily
- Monitor system logs for errors
- Check disk space usage
- Verify backup completion

#### Weekly
- Review user access patterns
- Clean up old export files
- Update system documentation

#### Monthly
- Database performance analysis
- Security update review
- Capacity planning assessment

### Upgrade Procedures

#### Minor Version Updates
1. Backup database and configuration
2. Update OpenREM: `pip install --upgrade OpenREM`
3. Run migrations: `python manage.py syncdb --migrate`
4. Collect static files: `python manage.py collectstatic`
5. Restart web server and Celery

#### Major Version Updates
1. Review release notes for breaking changes
2. Test upgrade in development environment
3. Plan maintenance window
4. Follow standard update procedure
5. Verify functionality post-upgrade

### Backup and Recovery

#### Backup Strategy
- Daily database backups
- Weekly full system backups
- Monthly offsite backup verification
- Configuration file version control

#### Recovery Procedures
1. Stop all OpenREM services
2. Restore database from backup
3. Restore configuration files
4. Restart services
5. Verify system functionality

### Capacity Planning

#### Growth Monitoring
- Track database size growth
- Monitor user activity patterns
- Assess storage requirements
- Plan hardware upgrades

#### Performance Metrics
- Response time monitoring
- Database query performance
- Export processing times
- System resource utilization

---

## Conclusion

This comprehensive guide covers all aspects of OpenREM installation, configuration, and operation. For additional support and updates, refer to the official documentation at http://docs.openrem.org and the project repository.

### Additional Resources
- **Official Documentation**: http://docs.openrem.org
- **Project Website**: http://openrem.org
- **Issue Tracker**: https://bitbucket.org/openrem/openrem/issues
- **Community Support**: http://openrem.org/getinvolved

### Version Information
This guide is based on OpenREM version 0.4.3 and includes features and functionality available in that release. Always consult the official documentation for the most current information.
