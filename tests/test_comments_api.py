import unittest

from app import create_app, db
from app.models import Comment, User
from settings import TestConfig


class TestCommentsAPI(unittest.TestCase):
    def setUp(self):
        self.base_url = 'http://127.0.0.1:5000'
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        # create comment
        self.post_id = 'test-post-id'
        self.comment = Comment(post_id=self.post_id, body='Test comment')
        db.session.add(self.comment)
        db.session.commit()

        # create user
        self.user = User(username='admin',
                         email='admin@email.com',
                         is_admin=True)
        self.user.set_password('admin_password')
        db.session.add(self.user)
        db.session.commit()

    def _login_user(self, email='admin@email.com', password='admin_password'):
        payload = {'email': email, 'password': password}
        response = self.client.post('/login', json=payload)
        return response

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_post_comments(self):
        response = self.client.get(f'/${self.post_id}')
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data), 1)

    def test_create_new_comment(self):
        payload = {'post_id': self.post_id, 'body': 'Test comment 2'}
        response = self.client.post('/new', json=payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Comment.query.count(), 2)

    def test_create_new_comment_reply(self):
        payload = {'post_id': self.post_id, 'body': 'Test comment 2',
                   'parent_id': self.comment.id
        }
        response = self.client.post('/new', json=payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Comment.query.count(), 2)
        self.assertEqual(len(self.comment.replies), 1)

    def test_update_comment(self):
        self._login_user()
        payload = {'body': 'Test comment updated'}
        response = self.client.put(
            f'{self.base_url}/{self.comment.id}/update', json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.comment.body, payload['body'])

    def test_delete_comment(self):
        self._login_user()
        response = self.client.delete(
            f'{self.base_url}/{self.comment.id}/delete',)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Comment.query.count(), 0)
