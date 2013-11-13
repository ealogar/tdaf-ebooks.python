'''
(c) Copyright 2013 Telefonica, I+D. Printed in Spain (Europe). All Rights
Reserved.

The copyright to the software program(s) is property of Telefonica I+D.
The program(s) may be used and or copied only with the express written
consent of Telefonica I+D or in accordance with the terms and conditions
stipulated in the agreement/contract under which the program(s) have
been supplied.
'''
from django.test import TestCase
from books.models import Book, Topic
from users.models import User, Rate
import base64
import json


class RateViewTests(TestCase):
    def setUp(self):
        self.book = Book(isbn='85-359-0277-5', title='title', price=10, author='author',
                    image='test.jpg')
        self.book.save()
        self.user = User(user_id=1, name='test')
        self.user.save()
        self.book2 = Book(isbn='0-306-40615-2', title='title', price=10, author='author',
                    image='test.jpg')
        self.book2.save()
        rate = Rate(rating=1, book_id=self.book2, user_id=self.user)
        rate.save()

    def test_put_new_rate_should_return_201(self):
        """
        When non existing rate, new one is added
        """
        resp = self.client.put('/ebucxop/books/85-359-0277-5/ratings/me?format=json', {'rating': 3},
                    HTTP_AUTHORIZATION='Basic ' + base64.b64encode('%s:%s' % ('Aladdin', 'open sesame')))
        response_content = json.loads(resp.content)
        self.assertEqual(resp.status_code, 201)
        self.assertEquals('3', response_content['rating'])

    def test_put_existing_rate_should_return_200(self):
        """
        When existing rate, old rate is updated and 200 returned
        """
        resp = self.client.put('/ebucxop/books/0-306-40615-2/ratings/me?format=json', {'rating': u'3'},
                    HTTP_AUTHORIZATION='Basic ' + base64.b64encode('%s:%s' % ('Aladdin', 'open sesame')))
        self.assertEqual(resp.status_code, 200)
        response_content = json.loads(resp.content)
        # Ensure that 1 is changed to 3
        self.assertEquals('3', response_content['rating'])


class PurchaseBookViewTests(TestCase):
    def setUp(self):
        # Every test needs a default user
        User.objects.create(user_id=1, name='Aladdin')
        Topic.objects.create(value='aventuras')
        book = Book(isbn='99921-58-10-7', price=10, title='T', author='a', summary='Su', image='file.png')
        book.save()

    def test_purchase_books_user_should_return_isbn(self):
        """
        Tests that we can not modify user when purchasing a books and book is added to user info
        """

        resp = self.client.put('/ebucxop/users/me/books/99921-58-10-7/', data={},
                HTTP_AUTHORIZATION='Basic ' + base64.b64encode('%s:%s' % ('Aladdin', 'open sesame')))
        self.assertEqual(resp.status_code, 201)

        self.assertEquals('99921-58-10-7', resp.data['isbn'])

    def test_purchase_book_invalid_isbn_user_should_fail(self):
        """
        Tests that we can not modify user when purchasing a books and book is added to user info
        """

        resp = self.client.put('/ebucxop/users/me/books/99921-58-1/', data={},
                HTTP_AUTHORIZATION='Basic ' + base64.b64encode('%s:%s' % ('Aladdin', 'open sesame')))
        self.assertEqual(resp.status_code, 400)


class BookViewsTests(TestCase):
    def setUp(self):
        self.book = Book(isbn='85-359-0277-5', title='title', price=10, author='author',
                    image='test.jpg')
        self.book.save()
        self.user = User(user_id=2, name='admin')
        self.user.save()
        self.book2 = Book(isbn='0-306-40615-2', title='title', price=20, author='author',
                    image='test.jpg')
        self.book2.save()
        rate = Rate(rating=1, book_id=self.book2, user_id=self.user)
        rate.save()

    def test_get_existing_book_should_return_200(self):
        """
        When non existing rate, new one is added
        """
        resp = self.client.get('/ebucxop/books/85-359-0277-5?format=json', {},
                    HTTP_AUTHORIZATION='Basic ' + base64.b64encode('%s:%s' % ('admin', 'admin')))
        response_content = json.loads(resp.content)
        self.assertEqual(resp.status_code, 200)
        self.assertEquals('10', response_content['price'])

    def test_get_existing_books_should_return_all_books(self):
        """
        When non existing rate, new one is added
        """
        resp = self.client.get('/ebucxop/books/?format=json', {},
                    HTTP_AUTHORIZATION='Basic ' + base64.b64encode('%s:%s' % ('admin', 'admin')))
        response_content = json.loads(resp.content)
        self.assertEqual(resp.status_code, 200)
        self.assertEquals('10', response_content['results'][0]['price'])
        self.assertEquals('20', response_content['results'][1]['price'])

    def test_update_existing_book_price_should_return_200(self):
        """
        When non existing rate, new one is added
        """
        resp = self.client.post('/ebucxop/books/85-359-0277-5?format=json', {'price': 30},
                    HTTP_AUTHORIZATION='Basic ' + base64.b64encode('%s:%s' % ('admin', 'admin')))
        response_content = json.loads(resp.content)
        self.assertEqual(resp.status_code, 200)
        self.assertEquals('30', response_content['price'])

    def test_update_existing_book_with_invalid_credentials_should_return_200(self):
        """
        When non existing rate, new one is added
        """
        user = User(user_id=1, name='Aladdin')
        user.save()
        resp = self.client.put('/ebucxop/books/85-359-0277-5?format=json', {'price': 30},
                    HTTP_AUTHORIZATION='Basic ' + base64.b64encode('%s:%s' % ('Aladdin', 'open sesame')))
        self.assertEqual(resp.status_code, 403)


class AdminBookViewTests(TestCase):
    def setUp(self):
        self.bookData = {'isbn': '85-359-0277-5', 'title': 'title', 'price': '10', 'author': 'author',
                    'image': 'test.jpg'}
        # We put user_id 2 as this would be the identifier of admin returned by TDA
        self.user = User(user_id=2, name='admin')
        self.user.save()
        self.book2 = Book(isbn='0-306-40615-2', title='title', price=10, author='author',
                    image='test.jpg')
        self.book2.save()

    def test_create_new_book_return_201(self):
        resp = self.client.post('/ebucxop/books/', data=self.bookData,
                HTTP_AUTHORIZATION='Basic ' + base64.b64encode('%s:%s' % ('admin', 'admin')))
        self.assertEqual(resp.status_code, 201)
        self.assertEquals('85-359-0277-5', resp.data['isbn'])

    def test_update_existing_book_return_200(self):
        resp = self.client.post('/ebucxop/books/0-306-40615-2/', data={'title': 'titleUpdated'},
                HTTP_AUTHORIZATION='Basic ' + base64.b64encode('%s:%s' % ('admin', 'admin')))
        self.assertEqual(resp.status_code, 200)
        self.assertEquals('titleUpdated', resp.data['title'])

    def test_create_new_book_without_credentials_return_403(self):
        resp = self.client.post('/ebucxop/books/', data=self.bookData,
                HTTP_AUTHORIZATION='Basic ' + base64.b64encode('%s:%s' % ('Aladdin', 'open sesame')))
        self.assertEqual(resp.status_code, 403)


class FilteringBookViewTests(TestCase):
    def setUp(self):
        self.book = Book(isbn='0-306-40615-2', title='title', price=10, author='author',
                    image='test.jpg')
        self.book.save()
        self.book2 = Book(isbn='85-359-0277-5', title='title2', price=10, author='author2',
                    image='test.jpg')
        self.book2.save()

    def test_get_books_by_author_should_return_one_book(self):
        resp = self.client.get('/ebucxop/books?author=author')
        self.assertEqual(resp.status_code, 200)
        self.assertEquals(1, len(resp.data['results']))
        self.assertEquals('author', resp.data['results'][0]['author'])

    def test_get_book_title_by_author_should_return_only_title(self):
        resp = self.client.get('/ebucxop/books?author=author&filter=title')
        self.assertEqual(resp.status_code, 200)
        self.assertEquals(1, len(resp.data['results']))
        self.assertEquals('title', resp.data['results'][0]['title'])
        # Ensure that only requested keys are in response
        self.assertTrue('author' not in resp.data['results'][0], 'Author returned in filtered output and it shouldnt')
        self.assertTrue('isbn' in resp.data['results'][0], 'Mandatory key isbn not returned')
