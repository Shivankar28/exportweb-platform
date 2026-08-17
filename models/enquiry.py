from datetime import datetime
from models import db

class Enquiry(db.Model):
    __tablename__ = 'enquiries'

    id = db.Column(db.Integer, primary_key=True)
    seller_id = db.Column(db.Integer, db.ForeignKey('sellers.id', ondelete='CASCADE'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id', ondelete='SET NULL'), nullable=True)

    buyer_name = db.Column(db.String(100), nullable=False)
    company = db.Column(db.String(150), nullable=True)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(30), nullable=True)
    country = db.Column(db.String(100), nullable=True)
    quantity = db.Column(db.String(100), nullable=True)
    message = db.Column(db.Text, nullable=False)
    
    status = db.Column(db.String(20), default='unread')  # 'unread', 'read', 'replied'
    admin_notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Enquiry #{self.id} from {self.buyer_name} for Seller {self.seller_id}>'
