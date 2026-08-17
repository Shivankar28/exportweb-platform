from datetime import datetime
from re import sub
from models import db

def slugify(text):
    text = text.lower().strip()
    text = sub(r'[^\w\s-]', '', text)
    text = sub(r'[\s_-]+', '-', text)
    return text

class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    slug = db.Column(db.String(120), unique=True, nullable=False, index=True)
    description = db.Column(db.Text, nullable=True)
    icon_class = db.Column(db.String(50), default='bi-box-seam')  # Bootstrap Icon class
    image_url = db.Column(db.String(500), nullable=True)
    image_public_id = db.Column(db.String(255), nullable=True)
    is_featured = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    products = db.relationship('Product', backref='category', lazy='dynamic')

    def generate_slug(self):
        self.slug = slugify(self.name)
        return self.slug

    def __repr__(self):
        return f'<Category {self.name}>'
