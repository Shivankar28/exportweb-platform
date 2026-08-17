from models import db

class Country(db.Model):
    __tablename__ = 'countries'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    code = db.Column(db.String(10), nullable=True)  # ISO 2-letter code e.g. US, IN, DE, AE
    flag_emoji = db.Column(db.String(10), nullable=True)
    region = db.Column(db.String(50), nullable=True)  # North America, Europe, Middle East, Asia Pacific, etc.

    # Relationships
    export_sellers = db.relationship('SellerExportMarket', backref='country', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Country {self.name} ({self.code})>'


class SellerExportMarket(db.Model):
    __tablename__ = 'seller_export_markets'

    id = db.Column(db.Integer, primary_key=True)
    seller_id = db.Column(db.Integer, db.ForeignKey('sellers.id', ondelete='CASCADE'), nullable=False)
    country_id = db.Column(db.Integer, db.ForeignKey('countries.id', ondelete='CASCADE'), nullable=False)
    market_share = db.Column(db.String(50), nullable=True)  # e.g., '25%', 'Major Market'
    notes = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return f'<SellerExportMarket Seller:{self.seller_id} Country:{self.country_id}>'
