from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models import db, Seller, SellerAddress, SellerContact, Product, ProductImage, Certification, SellerImage, Category, Country, SellerExportMarket, Enquiry
from services.cloudinary_service import upload_file, delete_file

seller_bp = Blueprint('seller', __name__, url_prefix='/seller')

@seller_bp.before_request
@login_required
def check_seller_role():
    if not current_user.is_seller and not current_user.is_admin:
        flash('Access restricted to exporter seller accounts.', 'danger')
        return redirect(url_for('main.index'))

def get_current_seller():
    if current_user.seller:
        return current_user.seller
    # Auto create seller profile if missing for seller user
    seller = Seller(user_id=current_user.id, company_name=current_user.email.split('@')[0].title())
    seller.generate_slug()
    db.session.add(seller)
    db.session.commit()
    return seller


@seller_bp.route('/dashboard')
def dashboard():
    seller = get_current_seller()
    seller.calculate_completion()
    db.session.commit()

    total_products = Product.query.filter_by(seller_id=seller.id).count()
    total_enquiries = Enquiry.query.filter_by(seller_id=seller.id).count()
    unread_enquiries = Enquiry.query.filter_by(seller_id=seller.id, status='unread').count()
    recent_enquiries = Enquiry.query.filter_by(seller_id=seller.id).order_by(Enquiry.created_at.desc()).limit(5).all()

    return render_template('seller_dashboard/index.html',
                           seller=seller,
                           total_products=total_products,
                           total_enquiries=total_enquiries,
                           unread_enquiries=unread_enquiries,
                           recent_enquiries=recent_enquiries)


@seller_bp.route('/profile', methods=['GET', 'POST'])
def profile():
    seller = get_current_seller()
    address = SellerAddress.query.filter_by(seller_id=seller.id, address_type='registered').first()
    contact = SellerContact.query.filter_by(seller_id=seller.id).first()

    if request.method == 'POST':
        seller.company_name = request.form.get('company_name', '').strip()
        seller.business_type = request.form.get('business_type', '')
        seller.year_established = request.form.get('year_established', type=int)
        seller.registration_number = request.form.get('registration_number', '').strip()
        seller.gst_number = request.form.get('gst_number', '').strip()
        seller.iec_code = request.form.get('iec_code', '').strip()
        seller.pan_number = request.form.get('pan_number', '').strip()
        seller.employee_count = request.form.get('employee_count', '')
        seller.annual_turnover = request.form.get('annual_turnover', '')
        seller.website = request.form.get('website', '').strip()
        seller.description = request.form.get('description', '').strip()

        # Update Slug if company name changed
        seller.generate_slug()

        # Handle Logo Upload
        logo_file = request.files.get('logo')
        if logo_file and logo_file.filename:
            if seller.logo_public_id:
                delete_file(seller.logo_public_id)
            res = upload_file(logo_file, seller.id, 'logo')
            if res:
                seller.logo_url = res['url']
                seller.logo_public_id = res['public_id']

        # Handle Cover Upload
        cover_file = request.files.get('cover')
        if cover_file and cover_file.filename:
            if seller.cover_public_id:
                delete_file(seller.cover_public_id)
            res = upload_file(cover_file, seller.id, 'cover')
            if res:
                seller.cover_url = res['url']
                seller.cover_public_id = res['public_id']

        # Address update
        if not address:
            address = SellerAddress(seller_id=seller.id, address_type='registered')
            db.session.add(address)
        address.address_line1 = request.form.get('address_line1', '').strip()
        address.address_line2 = request.form.get('address_line2', '').strip()
        address.city = request.form.get('city', '').strip()
        address.state = request.form.get('state', '').strip()
        address.postal_code = request.form.get('postal_code', '').strip()
        address.country = request.form.get('country', 'India')

        # Contact update
        if not contact:
            contact = SellerContact(seller_id=seller.id)
            db.session.add(contact)
        contact.contact_person = request.form.get('contact_person', '').strip()
        contact.designation = request.form.get('designation', '').strip()
        contact.phone = request.form.get('phone', '').strip()
        contact.whatsapp = request.form.get('whatsapp', '').strip()
        contact.email = request.form.get('contact_email', current_user.email).strip()

        seller.calculate_completion()
        db.session.commit()

        flash('Company profile updated successfully!', 'success')
        return redirect(url_for('seller.profile'))

    countries = Country.query.order_by(Country.name).all()
    return render_template('seller_dashboard/profile.html', seller=seller, address=address, contact=contact, countries=countries)


@seller_bp.route('/export-info', methods=['GET', 'POST'])
def export_info():
    seller = get_current_seller()

    if request.method == 'POST':
        seller.export_experience = request.form.get('export_experience', '').strip()
        seller.years_experience = request.form.get('years_experience', type=int, default=0)
        seller.export_countries = request.form.get('export_countries', '').strip()
        seller.moq = request.form.get('moq', '').strip()
        seller.production_capacity = request.form.get('production_capacity', '').strip()
        seller.packaging_details = request.form.get('packaging_details', '').strip()
        seller.payment_terms = request.form.get('payment_terms', '').strip()
        seller.shipping_terms = request.form.get('shipping_terms', '').strip()
        seller.port_of_loading = request.form.get('port_of_loading', '').strip()
        seller.lead_time = request.form.get('lead_time', '').strip()

        seller.calculate_completion()
        db.session.commit()
        flash('Export information updated successfully!', 'success')
        return redirect(url_for('seller.export_info'))

    return render_template('seller_dashboard/export_info.html', seller=seller)


@seller_bp.route('/products')
def products():
    seller = get_current_seller()
    products_list = Product.query.filter_by(seller_id=seller.id).order_by(Product.created_at.desc()).all()
    categories = Category.query.order_by(Category.name).all()
    return render_template('seller_dashboard/products.html', seller=seller, products=products_list, categories=categories)


@seller_bp.route('/products/add', methods=['POST'])
def add_product():
    seller = get_current_seller()
    name = request.form.get('name', '').strip()
    category_id = request.form.get('category_id', type=int)
    description = request.form.get('description', '').strip()
    moq = request.form.get('moq', '').strip()
    price_range = request.form.get('price_range', '').strip()
    hs_code = request.form.get('hs_code', '').strip()
    specifications = request.form.get('specifications', '').strip()

    if not name:
        flash('Product name is required.', 'danger')
        return redirect(url_for('seller.products'))

    product = Product(
        seller_id=seller.id,
        category_id=category_id,
        name=name,
        description=description,
        moq=moq,
        price_range=price_range,
        hs_code=hs_code,
        specifications=specifications,
        status='active'
    )
    product.generate_slug()
    db.session.add(product)
    db.session.flush()

    # Product Images Upload to Cloudinary folder: sellers/{seller_id}/products
    images = request.files.getlist('images')
    for index, img_file in enumerate(images):
        if img_file and img_file.filename:
            res = upload_file(img_file, seller.id, 'products')
            if res:
                p_img = ProductImage(
                    product_id=product.id,
                    image_url=res['url'],
                    public_id=res['public_id'],
                    is_primary=(index == 0)
                )
                db.session.add(p_img)

    seller.calculate_completion()
    db.session.commit()
    flash('New product added to catalog successfully!', 'success')
    return redirect(url_for('seller.products'))


@seller_bp.route('/products/delete/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    seller = get_current_seller()
    product = Product.query.filter_by(id=product_id, seller_id=seller.id).first_or_404()

    # Delete product images from Cloudinary / Disk
    for img in product.images:
        delete_file(img.public_id)

    db.session.delete(product)
    seller.calculate_completion()
    db.session.commit()
    flash('Product deleted successfully.', 'info')
    return redirect(url_for('seller.products'))


@seller_bp.route('/certifications', methods=['GET', 'POST'])
def certifications():
    seller = get_current_seller()

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        issuing_authority = request.form.get('issuing_authority', '').strip()
        certificate_number = request.form.get('certificate_number', '').strip()
        valid_until = request.form.get('valid_until', '').strip()
        doc_file = request.files.get('document')

        if not title or not doc_file or not doc_file.filename:
            flash('Certificate title and document file are required.', 'danger')
            return redirect(url_for('seller.certifications'))

        res = upload_file(doc_file, seller.id, 'certificates')
        if res:
            ext = doc_file.filename.split('.')[-1].lower()
            doc_type = 'pdf' if ext == 'pdf' else 'image'
            
            cert = Certification(
                seller_id=seller.id,
                title=title,
                issuing_authority=issuing_authority,
                certificate_number=certificate_number,
                valid_until=valid_until,
                document_url=res['url'],
                document_public_id=res['public_id'],
                document_type=doc_type
            )
            db.session.add(cert)
            seller.calculate_completion()
            db.session.commit()
            flash('Certification uploaded successfully!', 'success')

        return redirect(url_for('seller.certifications'))

    certs = Certification.query.filter_by(seller_id=seller.id).all()
    return render_template('seller_dashboard/certifications.html', seller=seller, certs=certs)


@seller_bp.route('/certifications/delete/<int:cert_id>', methods=['POST'])
def delete_certification(cert_id):
    seller = get_current_seller()
    cert = Certification.query.filter_by(id=cert_id, seller_id=seller.id).first_or_404()
    
    delete_file(cert.document_public_id)
    db.session.delete(cert)
    seller.calculate_completion()
    db.session.commit()
    flash('Certification deleted.', 'info')
    return redirect(url_for('seller.certifications'))


@seller_bp.route('/gallery', methods=['GET', 'POST'])
def gallery():
    seller = get_current_seller()

    if request.method == 'POST':
        caption = request.form.get('caption', '').strip()
        image_type = request.form.get('image_type', 'gallery')
        img_files = request.files.getlist('images')

        uploaded_count = 0
        for img_file in img_files:
            if img_file and img_file.filename:
                res = upload_file(img_file, seller.id, 'gallery')
                if res:
                    s_img = SellerImage(
                        seller_id=seller.id,
                        image_url=res['url'],
                        public_id=res['public_id'],
                        caption=caption,
                        image_type=image_type
                    )
                    db.session.add(s_img)
                    uploaded_count += 1

        if uploaded_count > 0:
            db.session.commit()
            flash(f'{uploaded_count} image(s) uploaded to company gallery.', 'success')

        return redirect(url_for('seller.gallery'))

    images = SellerImage.query.filter_by(seller_id=seller.id).all()
    return render_template('seller_dashboard/gallery.html', seller=seller, images=images)


@seller_bp.route('/gallery/delete/<int:img_id>', methods=['POST'])
def delete_gallery_image(img_id):
    seller = get_current_seller()
    img = SellerImage.query.filter_by(id=img_id, seller_id=seller.id).first_or_404()

    delete_file(img.public_id)
    db.session.delete(img)
    db.session.commit()
    flash('Image removed from gallery.', 'info')
    return redirect(url_for('seller.gallery'))


@seller_bp.route('/enquiries')
def enquiries():
    seller = get_current_seller()
    enquiry_list = Enquiry.query.filter_by(seller_id=seller.id).order_by(Enquiry.created_at.desc()).all()
    return render_template('seller_dashboard/enquiries.html', seller=seller, enquiries=enquiry_list)


@seller_bp.route('/enquiries/<int:enquiry_id>/status', methods=['POST'])
def update_enquiry_status(enquiry_id):
    seller = get_current_seller()
    enquiry = Enquiry.query.filter_by(id=enquiry_id, seller_id=seller.id).first_or_404()
    status = request.form.get('status', 'read')
    enquiry.status = status
    db.session.commit()
    flash(f'Enquiry status updated to {status}.', 'success')
    return redirect(url_for('seller.enquiries'))


@seller_bp.route('/submit-approval', methods=['POST'])
def submit_approval():
    seller = get_current_seller()
    seller.calculate_completion()
    
    if seller.completion_percentage < 40:
        flash('Please complete at least 40% of your profile (Company name, description, address, contact, products) before submitting for approval.', 'warning')
        return redirect(url_for('seller.dashboard'))

    seller.status = 'pending'
    db.session.commit()
    flash('Your portfolio has been submitted for admin verification and approval!', 'success')
    return redirect(url_for('seller.dashboard'))
