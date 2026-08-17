import unittest
from app import create_app
from seed import seed_database
from models import db, User, Seller, Product, Category, Enquiry

class ExportWebTestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

        with self.app.app_context():
            seed_database()

    def test_database_models_and_slugs(self):
        with self.app.app_context():
            # Check Admin User
            admin = User.query.filter_by(email='admin@exportweb.com').first()
            self.assertIsNotNone(admin)
            self.assertTrue(admin.is_admin)
            self.assertTrue(admin.check_password('admin123'))

            # Check Dynamic Seller Slug
            seller = Seller.query.filter_by(slug='sharma-agro-foods').first()
            self.assertIsNotNone(seller)
            self.assertEqual(seller.status, 'approved')
            self.assertGreater(seller.completion_percentage, 50)

            # Check Products
            products = Product.query.filter_by(seller_id=seller.id).all()
            self.assertGreater(len(products), 0)
            self.assertIsNotNone(products[0].primary_image)

    def test_public_routes(self):
        # 1. Home Page
        res = self.client.get('/')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'GlobalExport', res.data)

        # 2. Exporters Directory
        res = self.client.get('/sellers')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Sharma Agro Foods', res.data)

        # 3. Dynamic Portfolio Page (/sellers/<seller-slug>)
        res = self.client.get('/sellers/sharma-agro-foods')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Sharma Agro Foods', res.data)
        self.assertIn(b'Verified Exporter', res.data)

        # 4. Products Catalog Page
        res = self.client.get('/products')
        self.assertEqual(res.status_code, 200)

        # 5. Login & Register Pages
        self.assertEqual(self.client.get('/login').status_code, 200)
        self.assertEqual(self.client.get('/register').status_code, 200)

    def test_enquiry_submission(self):
        with self.app.app_context():
            seller = Seller.query.filter_by(slug='sharma-agro-foods').first()

            res = self.client.post('/send-enquiry', data={
                'seller_id': seller.id,
                'buyer_name': 'Global Trading Corp',
                'company': 'Global Trading Corp USA',
                'email': 'buyer@globaltrading.com',
                'phone': '+1 555 999 8888',
                'country': 'United States',
                'quantity': '2 Containers',
                'message': 'Requesting bulk pricing for 1121 Steam Basmati Rice.'
            }, follow_redirects=True)

            self.assertEqual(res.status_code, 200)

            # Check Enquiry in Database
            enquiry = Enquiry.query.filter_by(email='buyer@globaltrading.com').first()
            self.assertIsNotNone(enquiry)
            self.assertEqual(enquiry.seller_id, seller.id)
            self.assertEqual(enquiry.status, 'unread')

if __name__ == '__main__':
    unittest.main()
