import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'exportweb-secret-key-default-2026')
    
    # Database Configuration
    DATABASE_URL = os.getenv('DATABASE_URL', 'mysql+pymysql://root:root@localhost:3306/exportweb_db')
    USE_SQLITE_FALLBACK = os.getenv('USE_SQLITE_FALLBACK', 'True').lower() in ('true', '1', 't')
    
    # Default to SQLite if specified or fallback enabled
    if USE_SQLITE_FALLBACK:
        SQLALCHEMY_DATABASE_URI = os.getenv('OVERRIDE_DB_URI', 'sqlite:///exportweb.db')
    else:
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
        
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Cloudinary Configuration
    CLOUDINARY_CLOUD_NAME = os.getenv('CLOUDINARY_CLOUD_NAME', '')
    CLOUDINARY_API_KEY = os.getenv('CLOUDINARY_API_KEY', '')
    CLOUDINARY_API_SECRET = os.getenv('CLOUDINARY_API_SECRET', '')
    
    # SMTP Mail Configuration
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'True').lower() in ('true', '1', 't')
    MAIL_USERNAME = os.getenv('MAIL_USERNAME', '')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', '')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', 'noreply@exportweb.com')
    
    # Upload folder for local storage fallback
    UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload size
