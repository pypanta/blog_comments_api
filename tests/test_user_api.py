import unittest

from app import create_app, db
from app.auth.tokens import create_token
from app.models import User
from settings import TestConfig


class TestUserAPI(unittest.TestCase):
    def setUp(self):
        self.base_url = 'http://127.0.0.1:5000'
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        self.user = User(username='test', email='test@email.com')
        self.user.set_password('testpassword')
        db.session.add(self.user)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def _login_user(self):
        payload = {'email': self.user.email, 'password': 'testpassword'}
        response = self.client.post('/login', json=payload)
        return response

    def test_user_register(self):
        payload = {
            'username': 'john',
            'email': 'john@email.com',
            'password': 'test123',
            'password_confirm': 'test123'
        }
        response = self.client.post('/register', json=payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(User.query.count(), 2)

    def test_user_login(self):
        response = self._login_user()
        self.assertEqual(response.status_code, 200)

    def test_user_logout(self):
        self._login_user()
        response = self.client.get(f"{self.base_url}/logout")
        self.assertEqual(response.status_code, 200)

    def test_user_info(self):
        self._login_user()
        response = self.client.get(f"{self.base_url}/user")
        self.assertEqual(response.status_code, 200)

    def test_user_update(self):
        self._login_user()
        payload = {
            'username': 'testupdated',
            'email': 'testupdated@email.com',
            'about': 'I am test user'
        }
        response = self.client.patch(f"{self.base_url}/user-update",
                                     json=payload)
        self.assertEqual(response.status_code, 200)

    def test_user_update_email_is_required(self):
        self._login_user()
        payload = {
            'username': 'testupdated',
            'about': 'I am test user'
        }
        response = self.client.patch(f"{self.base_url}/user-update",
                                     json=payload)
        self.assertEqual(response.status_code, 400)

    def test_user_update_password(self):
        self._login_user()
        payload = {
            'username': 'testupdated',
            'email': 'testupdated@email.com',
            'about': 'I am test user',
            'password': 'test123updated',
            'password_confirm': 'test123updated'
        }
        response = self.client.patch(f"{self.base_url}/user-update",
                                     json=payload)
        self.assertEqual(response.status_code, 200)

        login_with_new_password_response = self.client.post(
            '/login',
            json={'email': 'testupdated', 'password':'test123updated'}
        )
        self.assertEqual(login_with_new_password_response.status_code, 200)
