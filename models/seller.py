from datetime import datetime
from re import sub
from models import db

def slugify(text):
    text = text.lower().strip()
    text = sub(r'[^\w\s-]', '', text)
    text = sub(r'[\s_-]+', '-', text)
    return text

class Seller(db.Model):
    __tablename__ = 'sellers'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True)
    
    # Company Overview
    company_name = db.Column(db.String(150), nullable=False)
    slug = db.Column(db.String(180), unique=True, nullable=False, index=True)
    business_type = db.Column(db.String(50), nullable=True)  # Manufacturer, Merchant Exporter, Trading Company, etc.
    year_established = db.Column(db.Integer, nullable=True)
    registration_number = db.Column(db.String(100), nullable=True)
    gst_number = db.Column(db.String(50), nullable=True)
    iec_code = db.Column(db.String(50), nullable=True)  # Import Export Code
    pan_number = db.Column(db.String(50), nullable=True)
    employee_count = db.Column(db.String(50), nullable=True)  # e.g., '10-50', '50-200'
    annual_turnover = db.Column(db.String(50), nullable=True)  # e.g., '$1M - $5M'
    website = db.Column(db.String(255), nullable=True)
    description = db.Column(db.Text, nullable=True)
    
    # Media
    logo_url = db.Column(db.String(500), nullable=True)
    logo_public_id = db.Column(db.String(255), nullable=True)
    cover_url = db.Column(db.String(500), nullable=True)
    cover_public_id = db.Column(db.String(255), nullable=True)

    # Export Information
    export_experience = db.Column(db.Text, nullable=True)
    years_experience = db.Column(db.Integer, nullable=True, default=0)
    export_countries = db.Column(db.Text, nullable=True)  # Comma separated or description
    moq = db.Column(db.String(100), nullable=True)  # Minimum Order Quantity
    production_capacity = db.Column(db.String(100), nullable=True)
    packaging_details = db.Column(db.Text, nullable=True)
    payment_terms = db.Column(db.String(150), nullable=True)  # L/C, T/T, Advance, etc.
    shipping_terms = db.Column(db.String(150), nullable=True)   # FOB, CIF, EXW, CFR, etc.
    port_of_loading = db.Column(db.String(150), nullable=True)
    lead_time = db.Column(db.String(100), nullable=True)

    # Status & Management
    status = db.Column(db.String(20), default='pending', nullable=False)  # 'pending', 'approved', 'rejected', 'suspended'
    rejection_reason = db.Column(db.Text, nullable=True)
    is_featured = db.Column(db.Boolean, default=False)
    completion_percentage = db.Column(db.Integer, default=20)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    addresses = db.relationship('SellerAddress', backref='seller', cascade='all, delete-orphan')
    contacts = db.relationship('SellerContact', backref='seller', cascade='all, delete-orphan')
    products = db.relationship('Product', backref='seller', cascade='all, delete-orphan')
    certifications = db.relationship('Certification', backref='seller', cascade='all, delete-orphan')
    gallery_images = db.relationship('SellerImage', backref='seller', cascade='all, delete-orphan')
    export_markets = db.relationship('SellerExportMarket', backref='seller', cascade='all, delete-orphan')
    enquiries = db.relationship('Enquiry', backref='seller', cascade='all, delete-orphan')

    def calculate_completion(self):
        score = 0
        total_checks = 10
        if self.company_name and self.business_type: score += 1
        if self.gst_number or self.iec_code or self.registration_number: score += 1
        if self.description and len(self.description) > 20: score += 1
        if self.logo_url: score += 1
        if self.cover_url: score += 1
        if self.addresses and len(self.addresses) > 0: score += 1
        if self.contacts and len(self.contacts) > 0: score += 1
        if self.export_countries or self.export_markets: score += 1
        if self.products and len(self.products) > 0: score += 1
        if self.certifications and len(self.certifications) > 0: score += 1
        
        self.completion_percentage = int((score / total_checks) * 100)
        return self.completion_percentage

    def generate_slug(self):
        base_slug = slugify(self.company_name)
        slug = base_slug
        counter = 1
        while Seller.query.filter(Seller.slug == slug, Seller.id != self.id).first() is not None:
            slug = f"{base_slug}-{counter}"
            counter += 1
        self.slug = slug
        return slug

    def __repr__(self):
        return f'<Seller {self.company_name} ({self.status})>'


class SellerAddress(db.Model):
    __tablename__ = 'seller_addresses'

    id = db.Column(db.Integer, primary_key=True)
    seller_id = db.Column(db.Integer, db.ForeignKey('sellers.id', ondelete='CASCADE'), nullable=False)
    address_type = db.Column(db.String(30), default='registered')  # 'registered', 'factory', 'warehouse'
    address_line1 = db.Column(db.String(255), nullable=False)
    address_line2 = db.Column(db.String(255), nullable=True)
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100), nullable=False)
    postal_code = db.Column(db.String(30), nullable=True)
    country = db.Column(db.String(100), default='India')

    def __repr__(self):
        return f'<SellerAddress {self.address_type}: {self.city}, {self.country}>'


class SellerContact(db.Model):
    __tablename__ = 'seller_contacts'

    id = db.Column(db.Integer, primary_key=True)
    seller_id = db.Column(db.Integer, db.ForeignKey('sellers.id', ondelete='CASCADE'), nullable=False)
    contact_person = db.Column(db.String(100), nullable=False)
    designation = db.Column(db.String(100), nullable=True)
    phone = db.Column(db.String(30), nullable=False)
    whatsapp = db.Column(db.String(30), nullable=True)
    email = db.Column(db.String(120), nullable=True)

    def __repr__(self):
        return f'<SellerContact {self.contact_person} ({self.designation})>'


class Certification(db.Model):
    __tablename__ = 'certifications'

    id = db.Column(db.Integer, primary_key=True)
    seller_id = db.Column(db.Integer, db.ForeignKey('sellers.id', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.String(150), nullable=False)  # ISO 9001, HACCP, Halal, CE, GMP, etc.
    issuing_authority = db.Column(db.String(150), nullable=True)
    certificate_number = db.Column(db.String(100), nullable=True)
    valid_until = db.Column(db.String(50), nullable=True)
    document_url = db.Column(db.String(500), nullable=False)
    document_public_id = db.Column(db.String(255), nullable=True)
    document_type = db.Column(db.String(20), default='image')  # 'image', 'pdf'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Certification {self.title}>'


class SellerImage(db.Model):
    __tablename__ = 'seller_images'

    id = db.Column(db.Integer, primary_key=True)
    seller_id = db.Column(db.Integer, db.ForeignKey('sellers.id', ondelete='CASCADE'), nullable=False)
    image_url = db.Column(db.String(500), nullable=False)
    public_id = db.Column(db.String(255), nullable=True)
    caption = db.Column(db.String(200), nullable=True)
    image_type = db.Column(db.String(30), default='gallery')  # 'gallery', 'factory', 'infrastructure'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<SellerImage {self.image_type} - {self.id}>'
