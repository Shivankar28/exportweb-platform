from datetime import datetime
from re import sub
from models import db

def slugify(text):
    text = text.lower().strip()
    text = sub(r'[^\w\s-]', '', text)
    text = sub(r'[\s_-]+', '-', text)
    return text

class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    seller_id = db.Column(db.Integer, db.ForeignKey('sellers.id', ondelete='CASCADE'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id', ondelete='SET NULL'), nullable=True)
    
    name = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(220), nullable=False, index=True)
    description = db.Column(db.Text, nullable=True)
    moq = db.Column(db.String(100), nullable=True)  # Minimum Order Quantity
    price_range = db.Column(db.String(100), nullable=True)  # e.g., '$10 - $25 per Metric Ton'
    hs_code = db.Column(db.String(50), nullable=True)  # Harmonized System Code
    specifications = db.Column(db.Text, nullable=True)  # JSON string or text summary of specs
    is_featured = db.Column(db.Boolean, default=False)
    status = db.Column(db.String(20), default='active')  # 'active', 'inactive'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    images = db.relationship('ProductImage', backref='product', cascade='all, delete-orphan')
    enquiries = db.relationship('Enquiry', backref='product', lazy='dynamic')

    @property
    def primary_image(self):
        primary = ProductImage.query.filter_by(product_id=self.id, is_primary=True).first()
        if not primary:
            primary = ProductImage.query.filter_by(product_id=self.id).first()
        return primary.image_url if primary else None

    def generate_slug(self):
        base_slug = slugify(self.name)
        slug = base_slug
        counter = 1
        while Product.query.filter(Product.slug == slug, Product.id != self.id).first() is not None:
            slug = f"{base_slug}-{counter}"
            counter += 1
        self.slug = slug
        return slug

    def __repr__(self):
        return f'<Product {self.name} (Seller ID: {self.seller_id})>'


class ProductImage(db.Model):
    __tablename__ = 'product_images'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id', ondelete='CASCADE'), nullable=False)
    image_url = db.Column(db.String(500), nullable=False)
    public_id = db.Column(db.String(255), nullable=True)
    is_primary = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<ProductImage {self.id} for Product {self.product_id}>'
