from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User, Seller, SellerAddress, SellerContact, Country
from services.cloudinary_service import upload_file

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('admin.dashboard'))
        elif current_user.is_seller:
            return redirect(url_for('seller.dashboard'))
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        remember = bool(request.form.get('remember'))

        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            flash('Invalid email address or password.', 'danger')
            return render_template('auth/login.html')

        if not user.is_active:
            flash('Your account has been deactivated. Please contact support.', 'warning')
            return render_template('auth/login.html')

        login_user(user, remember=remember)
        flash(f'Welcome back, {user.email}!', 'success')

        next_page = request.args.get('next')
        if next_page:
            return redirect(next_page)
        
        if user.is_admin:
            return redirect(url_for('admin.dashboard'))
        elif user.is_seller:
            return redirect(url_for('seller.dashboard'))
        return redirect(url_for('main.index'))

    return render_template('auth/login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    countries = Country.query.order_by(Country.name).all()

    if request.method == 'POST':
        # 1. Account Info
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        if not email or not password:
            flash('Email and password are required.', 'danger')
            return render_template('auth/register.html', countries=countries)

        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('auth/register.html', countries=countries)

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email is already registered. Please login.', 'danger')
            return render_template('auth/register.html', countries=countries)

        # 2. Company Info
        company_name = request.form.get('company_name', '').strip()
        if not company_name:
            flash('Company name is required.', 'danger')
            return render_template('auth/register.html', countries=countries)

        business_type = request.form.get('business_type', '')
        year_established = request.form.get('year_established', type=int)
        registration_number = request.form.get('registration_number', '').strip()
        gst_number = request.form.get('gst_number', '').strip()
        iec_code = request.form.get('iec_code', '').strip()
        pan_number = request.form.get('pan_number', '').strip()
        employee_count = request.form.get('employee_count', '')
        annual_turnover = request.form.get('annual_turnover', '')
        website = request.form.get('website', '').strip()
        description = request.form.get('description', '').strip()

        # 3. Address & Contact Info
        reg_address_line1 = request.form.get('reg_address_line1', '').strip()
        reg_city = request.form.get('reg_city', '').strip()
        reg_state = request.form.get('reg_state', '').strip()
        reg_postal_code = request.form.get('reg_postal_code', '').strip()
        reg_country = request.form.get('reg_country', 'India')

        contact_person = request.form.get('contact_person', '').strip()
        designation = request.form.get('designation', '').strip()
        phone = request.form.get('phone', '').strip()
        whatsapp = request.form.get('whatsapp', '').strip()

        # 4. Export Information
        export_experience = request.form.get('export_experience', '').strip()
        years_experience = request.form.get('years_experience', type=int, default=0)
        export_countries = request.form.get('export_countries', '').strip()
        moq = request.form.get('moq', '').strip()
        production_capacity = request.form.get('production_capacity', '').strip()
        packaging_details = request.form.get('packaging_details', '').strip()
        payment_terms = request.form.get('payment_terms', '').strip()
        shipping_terms = request.form.get('shipping_terms', '').strip()
        port_of_loading = request.form.get('port_of_loading', '').strip()
        lead_time = request.form.get('lead_time', '').strip()

        try:
            # Create User
            user = User(email=email, role='seller')
            user.set_password(password)
            db.session.add(user)
            db.session.flush()

            # Create Seller
            seller = Seller(
                user_id=user.id,
                company_name=company_name,
                business_type=business_type,
                year_established=year_established,
                registration_number=registration_number,
                gst_number=gst_number,
                iec_code=iec_code,
                pan_number=pan_number,
                employee_count=employee_count,
                annual_turnover=annual_turnover,
                website=website,
                description=description,
                export_experience=export_experience,
                years_experience=years_experience,
                export_countries=export_countries,
                moq=moq,
                production_capacity=production_capacity,
                packaging_details=packaging_details,
                payment_terms=payment_terms,
                shipping_terms=shipping_terms,
                port_of_loading=port_of_loading,
                lead_time=lead_time,
                status='pending'
            )
            seller.generate_slug()
            db.session.add(seller)
            db.session.flush()

            # Handle Logo & Cover Uploads if present
            logo_file = request.files.get('logo')
            if logo_file and logo_file.filename:
                logo_result = upload_file(logo_file, seller.id, 'logo')
                if logo_result:
                    seller.logo_url = logo_result['url']
                    seller.logo_public_id = logo_result['public_id']

            cover_file = request.files.get('cover')
            if cover_file and cover_file.filename:
                cover_result = upload_file(cover_file, seller.id, 'cover')
                if cover_result:
                    seller.cover_url = cover_result['url']
                    seller.cover_public_id = cover_result['public_id']

            # Create Address
            if reg_address_line1 and reg_city:
                address = SellerAddress(
                    seller_id=seller.id,
                    address_type='registered',
                    address_line1=reg_address_line1,
                    city=reg_city,
                    state=reg_state,
                    postal_code=reg_postal_code,
                    country=reg_country
                )
                db.session.add(address)

            # Create Contact Person
            if contact_person and phone:
                contact = SellerContact(
                    seller_id=seller.id,
                    contact_person=contact_person,
                    designation=designation,
                    phone=phone,
                    whatsapp=whatsapp or phone,
                    email=email
                )
                db.session.add(contact)

            seller.calculate_completion()
            db.session.commit()

            login_user(user)
            flash('Registration successful! Your seller account is pending admin approval. You can now build your portfolio.', 'success')
            return redirect(url_for('seller.dashboard'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error creating account: {str(e)}', 'danger')
            return render_template('auth/register.html', countries=countries)

    return render_template('auth/register.html', countries=countries)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))
