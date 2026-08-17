from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models import db, User, Seller, Product, Category, Certification, Enquiry, Country
from services.email_service import send_approval_status_email
from services.cloudinary_service import upload_file

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.before_request
@login_required
def check_admin_role():
    if not current_user.is_admin:
        flash('Admin authorization required to access control panel.', 'danger')
        return redirect(url_for('main.index'))


@admin_bp.route('/dashboard')
def dashboard():
    pending_sellers = Seller.query.filter_by(status='pending').order_by(Seller.created_at.desc()).all()
    approved_count = Seller.query.filter_by(status='approved').count()
    rejected_count = Seller.query.filter_by(status='rejected').count()
    suspended_count = Seller.query.filter_by(status='suspended').count()
    
    total_products = Product.query.count()
    total_enquiries = Enquiry.query.count()
    total_categories = Category.query.count()

    return render_template('admin_dashboard/index.html',
                           pending_sellers=pending_sellers,
                           stats={
                               'pending': len(pending_sellers),
                               'approved': approved_count,
                               'rejected': rejected_count,
                               'suspended': suspended_count,
                               'products': total_products,
                               'enquiries': total_enquiries,
                               'categories': total_categories
                           })


@admin_bp.route('/sellers')
def sellers():
    status_filter = request.args.get('status', 'all')
    search_q = request.args.get('q', '').strip()

    query = Seller.query
    if status_filter in ['pending', 'approved', 'rejected', 'suspended']:
        query = query.filter_by(status=status_filter)

    if search_q:
        query = query.filter(
            (Seller.company_name.ilike(f'%{search_q}%')) |
            (Seller.gst_number.ilike(f'%{search_q}%')) |
            (Seller.iec_code.ilike(f'%{search_q}%'))
        )

    sellers_list = query.order_by(Seller.created_at.desc()).all()
    return render_template('admin_dashboard/sellers.html', sellers=sellers_list, status_filter=status_filter, search_q=search_q)


@admin_bp.route('/sellers/<int:seller_id>')
def seller_detail(seller_id):
    seller = Seller.query.get_or_404(seller_id)
    products = Product.query.filter_by(seller_id=seller.id).all()
    certifications = Certification.query.filter_by(seller_id=seller.id).all()
    return render_template('admin_dashboard/seller_detail.html', seller=seller, products=products, certifications=certifications)


@admin_bp.route('/sellers/<int:seller_id>/status', methods=['POST'])
def update_seller_status(seller_id):
    seller = Seller.query.get_or_404(seller_id)
    status = request.form.get('status', '').strip().lower()
    reason = request.form.get('reason', '').strip()

    if status not in ['approved', 'rejected', 'suspended', 'pending']:
        flash('Invalid status provided.', 'danger')
        return redirect(url_for('admin.sellers'))

    seller.status = status
    if reason:
        seller.rejection_reason = reason

    db.session.commit()

    # Trigger Email Notification
    send_approval_status_email(seller, status, reason)

    flash(f"Seller '{seller.company_name}' status successfully updated to {status.upper()}.", 'success')
    return redirect(request.referrer or url_for('admin.sellers'))


@admin_bp.route('/sellers/<int:seller_id>/toggle-featured', methods=['POST'])
def toggle_seller_featured(seller_id):
    seller = Seller.query.get_or_404(seller_id)
    seller.is_featured = not seller.is_featured
    db.session.commit()
    flash(f"Featured status for '{seller.company_name}' updated to {seller.is_featured}.", 'success')
    return redirect(request.referrer or url_for('admin.sellers'))


@admin_bp.route('/categories', methods=['GET', 'POST'])
def categories():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        icon_class = request.form.get('icon_class', 'bi-box-seam').strip()
        is_featured = bool(request.form.get('is_featured'))
        img_file = request.files.get('image')

        if not name:
            flash('Category name is required.', 'danger')
            return redirect(url_for('admin.categories'))

        category = Category(name=name, description=description, icon_class=icon_class, is_featured=is_featured)
        category.generate_slug()

        if img_file and img_file.filename:
            res = upload_file(img_file, 0, 'categories')
            if res:
                category.image_url = res['url']
                category.image_public_id = res['public_id']

        db.session.add(category)
        db.session.commit()
        flash(f"Category '{name}' created successfully.", 'success')
        return redirect(url_for('admin.categories'))

    categories_list = Category.query.order_by(Category.name).all()
    return render_template('admin_dashboard/categories.html', categories=categories_list)


@admin_bp.route('/categories/delete/<int:cat_id>', methods=['POST'])
def delete_category(cat_id):
    category = Category.query.get_or_404(cat_id)
    db.session.delete(category)
    db.session.commit()
    flash('Category deleted.', 'info')
    return redirect(url_for('admin.categories'))


@admin_bp.route('/products')
def products():
    products_list = Product.query.order_by(Product.created_at.desc()).all()
    return render_template('admin_dashboard/products.html', products=products_list)


@admin_bp.route('/products/<int:prod_id>/toggle-featured', methods=['POST'])
def toggle_product_featured(prod_id):
    product = Product.query.get_or_404(prod_id)
    product.is_featured = not product.is_featured
    db.session.commit()
    flash(f"Product '{product.name}' featured status set to {product.is_featured}.", 'success')
    return redirect(url_for('admin.products'))


@admin_bp.route('/enquiries')
def enquiries():
    enquiries_list = Enquiry.query.order_by(Enquiry.created_at.desc()).all()
    return render_template('admin_dashboard/enquiries.html', enquiries=enquiries_list)
