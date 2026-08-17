import os
from app import create_app
from models import (
    db, User, Seller, SellerAddress, SellerContact, Certification,
    SellerImage, Category, Product, ProductImage, Country, SellerExportMarket, Enquiry
)

def seed_database():
    app = create_app()
    with app.app_context():
        print("Clearing existing data...")
        db.drop_all()
        db.create_all()

        print("Seeding Countries...")
        countries_data = [
            {'name': 'India', 'code': 'IN', 'flag_emoji': '🇮🇳', 'region': 'South Asia'},
            {'name': 'United States', 'code': 'US', 'flag_emoji': '🇺🇸', 'region': 'North America'},
            {'name': 'United Arab Emirates', 'code': 'AE', 'flag_emoji': '🇦🇪', 'region': 'Middle East'},
            {'name': 'Germany', 'code': 'DE', 'flag_emoji': '🇩🇪', 'region': 'Europe'},
            {'name': 'United Kingdom', 'code': 'GB', 'flag_emoji': '🇬🇧', 'region': 'Europe'},
            {'name': 'Vietnam', 'code': 'VN', 'flag_emoji': '🇻🇳', 'region': 'Southeast Asia'},
            {'name': 'Saudi Arabia', 'code': 'SA', 'flag_emoji': '🇸🇦', 'region': 'Middle East'},
            {'name': 'Japan', 'code': 'JP', 'flag_emoji': '🇯🇵', 'region': 'East Asia'},
            {'name': 'Australia', 'code': 'AU', 'flag_emoji': '🇦🇺', 'region': 'Oceania'},
            {'name': 'Netherlands', 'code': 'NL', 'flag_emoji': '🇳🇱', 'region': 'Europe'},
            {'name': 'Singapore', 'code': 'SG', 'flag_emoji': '🇸🇬', 'region': 'Southeast Asia'},
            {'name': 'Canada', 'code': 'CA', 'flag_emoji': '🇨🇦', 'region': 'North America'},
        ]
        
        country_objs = {}
        for c in countries_data:
            country = Country(**c)
            db.session.add(country)
            country_objs[c['name']] = country
        db.session.flush()

        print("Seeding Categories...")
        categories_data = [
            {'name': 'Agro & Food Products', 'icon_class': 'bi-wheat', 'description': 'Organic spices, Basmati rice, pulses, processed food, tea & coffee.', 'is_featured': True},
            {'name': 'Textiles & Garments', 'icon_class': 'bi-scissors', 'description': 'Cotton fabrics, finished apparel, silk scarves, home textiles & upholstery.', 'is_featured': True},
            {'name': 'Engineering & Machinery', 'icon_class': 'bi-gear-wide-connected', 'description': 'CNC machine tools, auto components, industrial valves & pumps.', 'is_featured': True},
            {'name': 'Chemicals & Pharma', 'icon_class': 'bi-capsule', 'description': 'Active pharmaceutical ingredients (APIs), organic dyes, agrochemicals.', 'is_featured': True},
            {'name': 'Handicrafts & Decor', 'icon_class': 'bi-palette', 'description': 'Brassware, marble artifacts, wooden furniture & handcrafted items.', 'is_featured': False},
            {'name': 'Leather & Footwear', 'icon_class': 'bi-bag', 'description': 'Finished leather goods, safety footwear, belts & fashion accessories.', 'is_featured': False},
        ]

        cat_objs = {}
        for cat in categories_data:
            c_obj = Category(**cat)
            c_obj.generate_slug()
            db.session.add(c_obj)
            cat_objs[cat['name']] = c_obj
        db.session.flush()

        print("Creating Admin Account...")
        admin_user = User(email='admin@exportweb.com', role='admin')
        admin_user.set_password('admin123')
        db.session.add(admin_user)

        print("Seeding Exporters & Sellers...")

        # 1. Approved Seller 1: Sharma Agro Foods Pvt Ltd
        seller1_user = User(email='export@sharmaagro.com', role='seller')
        seller1_user.set_password('seller123')
        db.session.add(seller1_user)
        db.session.flush()

        seller1 = Seller(
            user_id=seller1_user.id,
            company_name='Sharma Agro Foods',
            business_type='Manufacturer & Exporter',
            year_established=1998,
            registration_number='REG-IN-1998-AG9842',
            gst_number='07AAACS1420P1Z4',
            iec_code='0502014920',
            pan_number='AAACS1420P',
            employee_count='100-250',
            annual_turnover='$10 Million - $25 Million',
            website='https://sharmaagrofoods.example.com',
            description='Sharma Agro Foods is a premier Govt. Recognized Star Export House specializing in 100% Organic Traditional Indian Basmati Rice, Spices, Oilseeds, and Dried Herbs. With 25+ years of export excellence, we supply over 40 countries worldwide with APEDA & ISO certified agricultural produce.',
            logo_url='https://images.unsplash.com/photo-1542838132-92c53300491e?auto=format&fit=crop&w=400&q=80',
            cover_url='https://images.unsplash.com/photo-1500937386664-56d1dfef3854?auto=format&fit=crop&w=1400&q=80',
            export_experience='25 years of global agricultural commodity exports across USA, Middle East, and EU.',
            years_experience=25,
            export_countries='United States, United Arab Emirates, Saudi Arabia, Germany, United Kingdom, Netherlands',
            moq='1 Container (20 MT)',
            production_capacity='5,000 Metric Tons / Month',
            packaging_details='Vacuum Sealed Poly Bags, Jute Bags, Custom Private Labeling (1kg to 50kg)',
            payment_terms='Confirmed Irrevocable L/C at sight, 30% Advance T/T',
            shipping_terms='FOB Mundra Port, CIF Jebel Ali, CIF Hamburg, CFR Houston',
            port_of_loading='Mundra Port / Kandla Port, Gujarat, India',
            lead_time='10 - 14 Days upon L/C receipt',
            status='approved',
            is_featured=True
        )
        seller1.generate_slug()
        db.session.add(seller1)
        db.session.flush()

        # Addresses & Contact for Seller 1
        db.session.add(SellerAddress(
            seller_id=seller1.id,
            address_type='registered',
            address_line1='Plot 45, APEDA Industrial Agro Zone, GT Road',
            address_line2='Karnal',
            city='Karnal',
            state='Haryana',
            postal_code='132001',
            country='India'
        ))
        db.session.add(SellerAddress(
            seller_id=seller1.id,
            address_type='factory',
            address_line1='Processing Plant 3, Port Industrial Estate',
            city='Mundra',
            state='Gujarat',
            postal_code='370421',
            country='India'
        ))
        db.session.add(SellerContact(
            seller_id=seller1.id,
            contact_person='Rajesh Sharma',
            designation='Managing Director & Head of International Sales',
            phone='+91 98765 43210',
            whatsapp='+91 98765 43210',
            email='export@sharmaagro.com'
        ))

        # Certifications for Seller 1
        db.session.add(Certification(
            seller_id=seller1.id,
            title='ISO 22000:2018 Food Safety Management',
            issuing_authority='Bureau Veritas Certification',
            certificate_number='BV-IN-98742',
            valid_until='2028-12-31',
            document_url='https://images.unsplash.com/photo-1589829545856-d10d557cf95f?auto=format&fit=crop&w=600&q=80',
            document_type='image'
        ))
        db.session.add(Certification(
            seller_id=seller1.id,
            title='HACCP & USDA Organic Certification',
            issuing_authority='OneCert International',
            certificate_number='USDA-ORG-2024-55',
            valid_until='2027-06-30',
            document_url='https://images.unsplash.com/photo-1607604276583-eef5d076aa5f?auto=format&fit=crop&w=600&q=80',
            document_type='image'
        ))

        # Gallery Images for Seller 1
        db.session.add(SellerImage(
            seller_id=seller1.id,
            image_url='https://images.unsplash.com/photo-1595855759920-8658239e7302?auto=format&fit=crop&w=800&q=80',
            caption='Automated Processing & Sorting Plant',
            image_type='factory'
        ))
        db.session.add(SellerImage(
            seller_id=seller1.id,
            image_url='https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?auto=format&fit=crop&w=800&q=80',
            caption='Container Logistics & Port Dispatch',
            image_type='gallery'
        ))

        # Export Markets for Seller 1
        db.session.add(SellerExportMarket(seller_id=seller1.id, country_id=country_objs['United States'].id, market_share='35%', notes='Bulk Organic Rice & Spices'))
        db.session.add(SellerExportMarket(seller_id=seller1.id, country_id=country_objs['United Arab Emirates'].id, market_share='25%', notes='Super Basmati 1121 Rice'))
        db.session.add(SellerExportMarket(seller_id=seller1.id, country_id=country_objs['Germany'].id, market_share='20%', notes='EU Compliant Sesame Seeds'))

        # Products for Seller 1
        p1 = Product(
            seller_id=seller1.id,
            category_id=cat_objs['Agro & Food Products'].id,
            name='Premium 1121 Steam Basmati Rice (Extra Long Grain)',
            description='Aged 2 years, extra long grain (8.35mm average grain length) with rich aroma and flawless white appearance. 100% pure, double polished and optical sorter cleaned.',
            moq='20 Metric Tons (1 Container)',
            price_range='$1,150 - $1,300 / MT FOB',
            hs_code='1006.30.20',
            specifications='Grain Length: 8.35mm min\nMoisture: 12% max\nBroken: 0.5% max\nAroma: Natural Basmati Fragrance',
            is_featured=True,
            status='active'
        )
        p1.generate_slug()
        db.session.add(p1)
        db.session.flush()

        db.session.add(ProductImage(
            product_id=p1.id,
            image_url='https://images.unsplash.com/photo-1586201375761-83865001e31c?auto=format&fit=crop&w=800&q=80',
            is_primary=True
        ))

        p2 = Product(
            seller_id=seller1.id,
            category_id=cat_objs['Agro & Food Products'].id,
            name='Organic Malabar Black Pepper Whole (550 GL)',
            description='Sun-dried premium quality Tellicherry extra bold black pepper. High piperine content (5.5% min), intense pungency and ASTA quality benchmark.',
            moq='5 Metric Tons',
            price_range='$5,400 - $5,800 / MT FOB',
            hs_code='0904.11.30',
            specifications='Bulk Density: 550 GL min\nMoisture: 11% max\nExtraneous Matter: 0.2% max',
            is_featured=True,
            status='active'
        )
        p2.generate_slug()
        db.session.add(p2)
        db.session.flush()

        db.session.add(ProductImage(
            product_id=p2.id,
            image_url='https://images.unsplash.com/photo-1599940824399-b87987ceb72a?auto=format&fit=crop&w=800&q=80',
            is_primary=True
        ))

        # 2. Approved Seller 2: Global Textile Exporters
        seller2_user = User(email='sales@globaltextiles.com', role='seller')
        seller2_user.set_password('seller123')
        db.session.add(seller2_user)
        db.session.flush()

        seller2 = Seller(
            user_id=seller2_user.id,
            company_name='Global Textile Exporters',
            business_type='Manufacturer & Merchant Exporter',
            year_established=2008,
            registration_number='REG-TN-2008-TX104',
            gst_number='33AABCG9012K1ZX',
            iec_code='0408019910',
            pan_number='AABCG9012K',
            employee_count='250-500',
            annual_turnover='$25 Million - $50 Million',
            website='https://globaltextiles.example.com',
            description='Global Textile Exporters is a OEKO-TEX certified manufacturer of premium organic combed cotton yarns, knitted fabrics, home towels, and high-thread-count bed linens.',
            logo_url='https://images.unsplash.com/photo-1607082348824-0a96f2a4b9da?auto=format&fit=crop&w=400&q=80',
            cover_url='https://images.unsplash.com/photo-1604176354204-9268737828e4?auto=format&fit=crop&w=1400&q=80',
            export_experience='16 years exporting fashion fabrics & towels to UK, Germany, USA, Australia.',
            years_experience=16,
            export_countries='United Kingdom, Germany, Australia, United States, Japan',
            moq='1,000 Kilograms / 500 Sets',
            production_capacity='200 Tons Cotton Fabric / Month',
            packaging_details='Bale Packaging, Waterproof Carton Boxes, Custom Barcoded Polybags',
            payment_terms='Irrevocable L/C, 30% TT advance balance 70% against B/L copy',
            shipping_terms='FOB Tuticorin / FOB Chennai Port',
            port_of_loading='Tuticorin Port / Chennai Port, Tamil Nadu, India',
            lead_time='15 - 20 Days',
            status='approved',
            is_featured=True
        )
        seller2.generate_slug()
        db.session.add(seller2)
        db.session.flush()

        db.session.add(SellerAddress(
            seller_id=seller2.id,
            address_type='registered',
            address_line1='124 Textile Park Road, Tirupur Sector 4',
            city='Tirupur',
            state='Tamil Nadu',
            postal_code='641603',
            country='India'
        ))
        db.session.add(SellerContact(
            seller_id=seller2.id,
            contact_person='Karthik Sundaram',
            designation='VP International Exports',
            phone='+91 94433 11223',
            whatsapp='+91 94433 11223',
            email='sales@globaltextiles.com'
        ))

        p3 = Product(
            seller_id=seller2.id,
            category_id=cat_objs['Textiles & Garments'].id,
            name='100% Organic Combed Cotton Ring Spun Yarn (30s & 40s)',
            description='GOTS certified 100% organic cotton yarn suitable for circular knitting and weaving. High tensile strength, minimum imperfections, excellent luster.',
            moq='2 Metric Tons',
            price_range='$3.80 - $4.40 / Kg FOB',
            hs_code='5205.23.00',
            specifications='Count: 30s/1 & 40s/1\nCSP: 2900+\nUster %: 9.5%',
            is_featured=True,
            status='active'
        )
        p3.generate_slug()
        db.session.add(p3)
        db.session.flush()

        db.session.add(ProductImage(
            product_id=p3.id,
            image_url='https://images.unsplash.com/photo-1579684385127-1ef15d508118?auto=format&fit=crop&w=800&q=80',
            is_primary=True
        ))

        # 3. Pending Seller: Apex Engineering Tools
        seller3_user = User(email='info@apexengineering.com', role='seller')
        seller3_user.set_password('seller123')
        db.session.add(seller3_user)
        db.session.flush()

        seller3 = Seller(
            user_id=seller3_user.id,
            company_name='Apex Engineering & Machinery Tools',
            business_type='Manufacturer',
            year_established=2015,
            registration_number='REG-MH-2015-ENG88',
            gst_number='27AAACA5544J1Z2',
            iec_code='0315088210',
            pan_number='AAACA5544J',
            employee_count='50-100',
            annual_turnover='$5 Million - $10 Million',
            website='https://apexengineering.example.com',
            description='Apex Engineering manufactures high precision CNC lathe components, industrial steel valves, gearboxes, and custom machinery parts.',
            export_experience='Exporting machine components to UAE and Vietnam.',
            years_experience=8,
            export_countries='United Arab Emirates, Vietnam, Saudi Arabia',
            status='pending',  # Test pending state for admin review
            is_featured=False
        )
        seller3.generate_slug()
        db.session.add(seller3)
        db.session.flush()

        db.session.add(SellerAddress(
            seller_id=seller3.id,
            address_type='registered',
            address_line1='MIDC Industrial Area, Phase II',
            city='Pune',
            state='Maharashtra',
            postal_code='411026',
            country='India'
        ))
        db.session.add(SellerContact(
            seller_id=seller3.id,
            contact_person='Vikram Deshmukh',
            designation='Export Manager',
            phone='+91 98220 55443',
            whatsapp='+91 98220 55443',
            email='info@apexengineering.com'
        ))

        seller1.calculate_completion()
        seller2.calculate_completion()
        seller3.calculate_completion()

        db.session.commit()
        print("Database seeded successfully with demo exporters, categories, countries, and products!")

if __name__ == '__main__':
    seed_database()
