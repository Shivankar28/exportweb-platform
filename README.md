# GlobalExportHub - Exporter B2B Platform & Dynamic Seller Portfolios

A full-stack, production-grade B2B export marketplace platform connecting global buyers with verified exporters and sellers. Built with Python Flask, SQLAlchemy, MySQL (with SQLite fallback), Bootstrap 5, Cloudinary asset storage, and SMTP email notifications.

---

## Key Features

- **Dynamic Exporter Portfolios (`/sellers/<seller-slug>`)**:
  - Automatically renders dynamic seller details, products, quality certifications, plant gallery, export logistics terms, and contact info using a single Jinja2 template (`templates/sellers/portfolio.html`).
  - Supports custom slugs (e.g. `/sellers/sharma-agro-foods`, `/sellers/global-textile-exports`).
- **Multi-Step Exporter Registration Wizard**:
  - 4-Step onboarding form (Account -> Company Info & Government Identifiers GST/IEC/PAN -> Address & Contact -> Export Logistics & Branding Uploads).
- **Cloudinary Integration**:
  - Secure asset management for logos, cover banners, product photos, plant gallery, and compliance document PDFs/images organized in folder structures (`sellers/{id}/logo`, `sellers/{id}/products`, `sellers/{id}/certificates`).
  - Safe zero-break local storage fallback if Cloudinary API keys are not supplied.
- **Admin Approval Pipeline**:
  - Audit queue for pending exporters. Admins can review GST/IEC data, products, certifications, and approve, reject (with custom feedback note), or suspend seller accounts.
- **Multi-faceted Directory & Filters**:
  - Buyer search by keywords, industry categories, target export destination countries, and quality certifications.
- **Direct Buyer Enquiry / RFQ System**:
  - Interactive "Send Enquiry" modal on exporter portfolios and product detail pages, persisting leads in MySQL/SQLAlchemy and dispatching email notifications.

---

## Tech Stack

- **Backend**: Python Flask, Flask-SQLAlchemy, Flask-Login, Flask-WTF
- **Database**: MySQL (PyMySQL) with automatic SQLite fallback (`exportweb.db`)
- **Frontend**: HTML5, Vanilla CSS3 (Custom B2B Design System), JavaScript, Bootstrap 5.3, Bootstrap Icons
- **Image & File Storage**: Cloudinary Python SDK
- **Email Service**: SMTP (with console logger fallback)

---

## Local Setup & Quickstart Guide

### 1. Prerequisites
- Python 3.10+
- MySQL Server (Optional - if MySQL is not running, the application automatically uses local SQLite)

### 2. Installation
Clone or navigate to the project directory:
```bash
cd c:\Users\lenovo\Desktop\exportweb
```

Install required dependencies:
```bash
pip install -r requirements.txt
```

### 3. Environment Configuration (`.env`)
Copy `.env.example` to `.env` or edit `.env` directly:
```env
SECRET_KEY=exportweb_secret_key_2026
FLASK_ENV=development
DEBUG=True

# MySQL connection string (Defaults to SQLite fallback if MySQL server is unreachable)
DATABASE_URL=mysql+pymysql://root:root@localhost:3306/exportweb_db
USE_SQLITE_FALLBACK=True

# Cloudinary Storage Configuration (Optional)
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret

# SMTP Email Configuration (Optional)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_app_password
```

### 4. Database Seeding
Initialize the database with default categories, global export destination countries, default admin account, and demo verified exporters:
```bash
python seed.py
```

### 5. Running the Application
Launch the Flask development server:
```bash
python app.py
```
Open your browser and navigate to: [http://127.0.0.1:5000](http://127.0.0.1:5000)

---

## Pre-Configured Demo Accounts

- **Admin Account**:
  - Email: `admin@exportweb.com`
  - Password: `admin123`
  - Control Panel: `/admin/dashboard`

- **Verified Exporter 1 (Sharma Agro Foods)**:
  - Email: `export@sharmaagro.com`
  - Password: `seller123`
  - Dynamic Portfolio URL: `/sellers/sharma-agro-foods`

- **Verified Exporter 2 (Global Textile Exporters)**:
  - Email: `sales@globaltextiles.com`
  - Password: `seller123`
  - Dynamic Portfolio URL: `/sellers/global-textile-exports`

- **Pending Exporter (Apex Engineering)**:
  - Email: `info@apexengineering.com`
  - Password: `seller123`
  - Appears in Admin pending review queue.

---

## Verification & Sanity Test

Run the test suite to verify route resolution, slug matching, database relationships, and template rendering:
```bash
python test_app.py
```
