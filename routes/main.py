from flask import Blueprint, render_template, request, redirect, url_for, flash, abort, jsonify
from flask_login import current_user
from models import db, Seller, Product, Category, Country, Certification, Enquiry
from services.email_service import send_enquiry_notification

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    featured_sellers = Seller.query.filter_by(status='approved', is_featured=True).limit(6).all()
    if not featured_sellers:
        featured_sellers = Seller.query.filter_by(status='approved').limit(6).all()

    featured_products = Product.query.filter_by(status='active', is_featured=True).limit(8).all()
    if not featured_products:
        featured_products = Product.query.filter_by(status='active').limit(8).all()

    categories = Category.query.order_by(Category.name).all()
    countries = Country.query.order_by(Country.name).all()

    total_sellers = Seller.query.filter_by(status='approved').count()
    total_products = Product.query.filter_by(status='active').count()
    total_countries = Country.query.count()

    return render_template('index.html',
                           featured_sellers=featured_sellers,
                           featured_products=featured_products,
                           categories=categories,
                           countries=countries,
                           stats={
                               'sellers': total_sellers or 12,
                               'products': total_products or 45,
                               'countries': total_countries or 28,
                               'enquiries': 150
                           })


@main_bp.route('/about')
def about():
    return render_template('about.html')


@main_bp.route('/contact')
def contact():
    return render_template('contact.html')


@main_bp.route('/sellers')
def sellers_directory():
    search_q = request.args.get('q', '').strip()
    category_id = request.args.get('category', type=int)
    country_name = request.args.get('country', '').strip()
    certification_title = request.args.get('certification', '').strip()

    # Base query: only approved sellers in public directory
    query = Seller.query.filter_by(status='approved')

    if search_q:
        query = query.filter(
            (Seller.company_name.ilike(f'%{search_q}%')) |
            (Seller.description.ilike(f'%{search_q}%')) |
            (Seller.business_type.ilike(f'%{search_q}%')) |
            (Seller.export_countries.ilike(f'%{search_q}%'))
        )

    if category_id:
        query = query.join(Product).filter(Product.category_id == category_id).distinct()

    if country_name:
        query = query.filter(
            (Seller.export_countries.ilike(f'%{country_name}%')) |
            (Seller.addresses.any(country=country_name))
        )

    if certification_title:
        query = query.join(Certification).filter(Certification.title.ilike(f'%{certification_title}%')).distinct()

    sellers = query.order_by(Seller.is_featured.desc(), Seller.company_name.asc()).all()

    categories = Category.query.order_by(Category.name).all()
    countries = Country.query.order_by(Country.name).all()
    certifications = db.session.query(Certification.title).distinct().all()
    cert_list = [c[0] for c in certifications if c[0]]

    return render_template('sellers/directory.html',
                           sellers=sellers,
                           categories=categories,
                           countries=countries,
                           certifications=cert_list,
                           search_q=search_q,
                           selected_category=category_id,
                           selected_country=country_name,
                           selected_cert=certification_title)


@main_bp.route('/sellers/<seller_slug>')
def seller_portfolio(seller_slug):
    """
    DYNAMIC SINGLE TEMPLATE FOR ALL SELLERS
    Route: /sellers/<seller-slug>
    Renders templates/sellers/portfolio.html
    """
    seller = Seller.query.filter_by(slug=seller_slug).first_or_404()

    # Authorization check for unapproved sellers
    is_owner = current_user.is_authenticated and current_user.seller and current_user.seller.id == seller.id
    is_admin = current_user.is_authenticated and current_user.is_admin

    if seller.status != 'approved' and not (is_owner or is_admin):
        flash('This exporter profile is currently under review or not publicly available.', 'warning')
        return redirect(url_for('main.sellers_directory'))

    # Load seller relations for dynamic rendering
    products = Product.query.filter_by(seller_id=seller.id, status='active').all()
    certifications = Certification.query.filter_by(seller_id=seller.id).all()
    gallery = seller.gallery_images
    contacts = seller.contacts
    addresses = seller.addresses
    export_markets = seller.export_markets

    return render_template('sellers/portfolio.html',
                           seller=seller,
                           products=products,
                           certifications=certifications,
                           gallery=gallery,
                           contacts=contacts,
                           addresses=addresses,
                           export_markets=export_markets,
                           is_preview=seller.status != 'approved')


@main_bp.route('/products')
def products_directory():
    search_q = request.args.get('q', '').strip()
    category_id = request.args.get('category', type=int)

    query = Product.query.join(Seller).filter(Product.status == 'active', Seller.status == 'approved')

    if search_q:
        query = query.filter(
            (Product.name.ilike(f'%{search_q}%')) |
            (Product.description.ilike(f'%{search_q}%')) |
            (Product.hs_code.ilike(f'%{search_q}%'))
        )

    if category_id:
        query = query.filter(Product.category_id == category_id)

    products = query.order_by(Product.is_featured.desc(), Product.created_at.desc()).all()
    categories = Category.query.order_by(Category.name).all()

    return render_template('products/directory.html',
                           products=products,
                           categories=categories,
                           search_q=search_q,
                           selected_category=category_id)


@main_bp.route('/products/<product_slug>')
def product_detail(product_slug):
    product = Product.query.filter_by(slug=product_slug).first_or_404()
    seller = product.seller

    if seller.status != 'approved':
        is_owner = current_user.is_authenticated and current_user.seller and current_user.seller.id == seller.id
        is_admin = current_user.is_authenticated and current_user.is_admin
        if not (is_owner or is_admin):
            abort(404)

    related_products = Product.query.filter(
        Product.category_id == product.category_id,
        Product.id != product.id,
        Product.status == 'active'
    ).limit(4).all()

    return render_template('products/detail.html',
                           product=product,
                           seller=seller,
                           related_products=related_products)


@main_bp.route('/categories')
def categories():
    categories_list = Category.query.order_by(Category.name).all()
    return render_template('categories.html', categories=categories_list)


@main_bp.route('/send-enquiry', methods=['POST'])
def send_enquiry():
    seller_id = request.form.get('seller_id', type=int)
    product_id = request.form.get('product_id', type=int)
    buyer_name = request.form.get('buyer_name', '').strip()
    company = request.form.get('company', '').strip()
    email = request.form.get('email', '').strip().lower()
    phone = request.form.get('phone', '').strip()
    country = request.form.get('country', '').strip()
    quantity = request.form.get('quantity', '').strip()
    message = request.form.get('message', '').strip()

    if not seller_id or not buyer_name or not email or not message:
        flash('Please fill in all required fields (Name, Email, Message).', 'danger')
        return redirect(request.referrer or url_for('main.sellers_directory'))

    seller = Seller.query.get_or_404(seller_id)

    try:
        enquiry = Enquiry(
            seller_id=seller.id,
            product_id=product_id,
            buyer_name=buyer_name,
            company=company,
            email=email,
            phone=phone,
            country=country,
            quantity=quantity,
            message=message,
            status='unread'
        )
        db.session.add(enquiry)
        db.session.commit()

        # Send Email Notification
        send_enquiry_notification(enquiry, seller)

        flash('Your inquiry has been successfully sent to the exporter! They will contact you shortly.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Failed to submit inquiry: {str(e)}', 'danger')

    return redirect(request.referrer or url_for('main.seller_portfolio', seller_slug=seller.slug))
