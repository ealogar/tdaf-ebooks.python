"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
import base64
from users.models import User, Topic
from books.models import Book


class UsersView(TestCase):

    def setUp(self):
        # Every test needs a default user
        User.objects.create(user_id=1, name='Aladdin')
        Topic.objects.create(value='aventuras')
        book = Book(isbn='99921-58-10-7', price=10, title='T', author='a', summary='Su', image='file.png')
        book.save()

    def test_user_collection(self):
        """
        Tests that we get something from default collection view
        """
        resp = self.client.get('/ebucxop/users/')
        self.assertEqual(resp.status_code, 200)

    def test_get_current_user_unauntheticated_fails(self):
        """
        Tests that we get 401 status code when no credentials supplied to access /me resource
        """
        resp = self.client.get('/ebucxop/users/me/')
        self.assertEqual(resp.status_code, 401)

    def test_get_current_user(self):
        """
        Tests that we get current user info when supplying valid credentials
        """
        resp = self.client.get('/ebucxop/users/me/',
                HTTP_AUTHORIZATION='Basic ' + base64.b64encode('%s:%s' % ('Aladdin', 'open sesame')))
        self.assertEqual(resp.status_code, 200)

    def test_update_user_info_should_work(self):
        """
        Tests that we can update current user info when supplying valid credentials
        """

        resp = self.client.post('/ebucxop/users/me/', data={'name': 'test', 'topics': ['aventuras']},
                HTTP_AUTHORIZATION='Basic ' + base64.b64encode('%s:%s' % ('Aladdin', 'open sesame')))
        self.assertEqual(resp.status_code, 200)
        self.assertEquals('test', resp.data['name'])
        self.assertEquals(['aventuras'], resp.data['topics'])
        self.assertEquals([], resp.data['books'])

    def test_update_user_info_with_put_should_return_not_allowed(self):
        """
        Tests that we can update current user info when supplying valid credentials
        """

        resp = self.client.put('/ebucxop/users/me/', data={'name': 'test', 'topics': ['aventuras']},
                HTTP_AUTHORIZATION='Basic ' + base64.b64encode('%s:%s' % ('Aladdin', 'open sesame')))
        self.assertEqual(resp.status_code, 405)

    def test_update_tags_user_info_should_work(self):
        """
        Tests that we can update partial user info: same as patch method
        """

        resp = self.client.post('/ebucxop/users/me/', data={'topics': ['aventuras']},
                HTTP_AUTHORIZATION='Basic ' + base64.b64encode('%s:%s' % ('Aladdin', 'open sesame')))
        self.assertEqual(resp.status_code, 200)
        # name is not altered
        self.assertEquals('Aladdin', resp.data['name'])
        # topics are changed
        self.assertEquals(['aventuras'], resp.data['topics'])
        self.assertEquals([], resp.data['books'])

    def test_update_books_user_should_not_update_books(self):
        """
        Tests that we can not modify books when altering user
        """

        resp = self.client.post('/ebucxop/users/me/', data={'books': ['isbn']},
                HTTP_AUTHORIZATION='Basic ' + base64.b64encode('%s:%s' % ('Aladdin', 'open sesame')))
        self.assertEqual(resp.status_code, 200)
        # name is not altered
        self.assertEquals('Aladdin', resp.data['name'])
        # topics are not changed
        self.assertEquals([], resp.data['topics'])
        # books are not taken into account
        self.assertEquals([], resp.data['books'])
