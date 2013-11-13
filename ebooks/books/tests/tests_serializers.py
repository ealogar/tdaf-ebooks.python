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
from books.serializers import BookSerializer, BookRateSerializer, RateSerializer
from books.models import Book
from users.models import Topic, Rate, User
from rest_framework.request import Request
from django.http import HttpRequest
from decimal import Decimal


class BookSerializerTests(TestCase):
    def setUp(self):
        bookModelRequiredData = {'isbn': '0-306-40615-2', 'title': 'title', 'price': 10, 'author': 'author',
                                 'image': 'test.jpg', 'num_ratings': 0}
        # Adding serializer extra fields that not required in model
        self.expected = {'avg_rate': Decimal('0.00'), 'ratings': [], 'topics': [], 'summary': ''}
        # we add as expected what it should be in model
        self.expected.update(bookModelRequiredData)
        self.book = Book(**bookModelRequiredData)
        self.user = User(user_id=2, name='admin')
        self.user.save()

    def test_retrieve_book_should_work(self):
        """
        We check that serialization an existing model is working
        """
        serializer = BookSerializer(self.book)
        # Check we have a correct dictionary serialized with python datatypes
        self.assertEquals(serializer.data, self.expected)

    def test_retrieve_book_with_topics_should_use_topic_value(self):
        """
        We check that serialization an existing model is working and topic
        display name follows our custom representation
        """
        # Creating a topic in database to relate with book
        self.book.save()
        topic = Topic(value='aventuras')
        topic.save()
        self.book.topics.add(topic)
        self.book.save()
        serializer = BookSerializer(self.book)
        self.expected['topics'] = ['aventuras']
        self.assertEquals(serializer.data, self.expected)
        # Update pattern in class definition, a little bit tricky
        _base_fields = getattr(BookSerializer, 'base_fields')

    def test_retrieve_book_with_ratings_should_return_avg_rate(self):
        """
        We check that serialization an existing model is working and topic
        display name follows our custom representation
        """
        # Creating a topic in database to relate with book
        self.book.save()
        topic = Topic(value='aventuras')
        topic.save()
        self.book.topics.add(topic)
        rating = Rate(user_id=self.user, book_id=self.book, rating=3)
        self.book.ratings.add(rating)
        self.book.num_ratings = 1
        self.book.total_rating = 3
        self.book.save()
        serializer = BookSerializer(self.book)
        self.expected['topics'] = ['aventuras']
        self.expected['ratings'] = [{'user_id': '2', 'rating': Decimal('3')}]
        self.expected['avg_rate'] = Decimal('3')
        self.expected['num_ratings'] = 1
        self.assertEquals(serializer.data, self.expected)
        # Update pattern in class definition, a little bit tricky
        _base_fields = getattr(BookSerializer, 'base_fields')

    def test_create_valid_book_should_work(self):
        """
        We check deserialization process of a dictionary where we get a valid object model with validations succeded
        """
        serializer = BookSerializer(data=self.expected)
        # Check validations works
        self.assertEquals(serializer.is_valid(), True)
        # Check object created is what we expect
        self.assertEquals(serializer.object, self.book)
        self.assertEquals(serializer.data['author'], 'author')

    def test_update_valid_book_should_work(self):
        """
        We check deserialization process of a dictionary where we update an existing object model.
        Validations must work
        """
        serializer = BookSerializer(self.book, data=self.expected)
        # Check validations works
        self.assertEquals(serializer.is_valid(), True)
        # Check object updated is what we expect
        self.assertEquals(serializer.object, self.book)
        self.assertEquals(serializer.data['author'], 'author')

    def test_update_partial_book_should_work(self):
        """
        We check deserialization process of a dictionary where we update some values of an existing object model
        We check both with partial True and False
        """
        partial_data = {'author': 'partial'}
        serializer = BookSerializer(self.book, data=partial_data)
        # Check validations fails
        self.assertEquals(serializer.is_valid(), False)

        serializer = BookSerializer(self.book, data=partial_data, partial=True)
        self.assertEquals(serializer.is_valid(), True)
        # Check object created is what we expect
        self.assertEquals(serializer.object, self.book)
        self.assertEquals(serializer.data['author'], 'partial')
        # Notice that self.book is updated when serializing
        self.assertEquals(serializer.object.author, 'partial')

    def test_model_fiels_are_loaded(self):
        """
        As we use model serializer we want to make sure all fields in model are included in serializer,
        even read_only methods
        """
        serializer = BookSerializer(self.book)
        self.assertEquals(set(serializer.data.keys()), set(['isbn', 'title', 'price', 'author', 'image', 'summary',
                                                            'avg_rate', 'topics', 'ratings', 'num_ratings']))

    def test_read_only_fields_should_not_being_altered(self):
        """
        We check that read only fields of serializers are not altered
        """
        serializer = BookSerializer(self.book, data={'total_rating': 5}, partial=True)
        self.assertEquals(serializer.is_valid(), True)
        instance = serializer.save()
        self.assertEquals(serializer.errors, {})
        # Avg_rate should be unchanged
        self.assertEquals(instance.total_rating, Decimal('0.00'))

    def test_filtering_from_request_should_return_expected_values(self):
        """
        Check that when we define filtes in request, serializer fields are updated and only required fields
        and those selected in filters are returned
        """
        # setattr(BookSerializer, 'context', _base_fields)
        request = Request(HttpRequest())
        setattr(request, '_method', 'GET')
        request.QUERY_PARAMS.update({'filter': 'author'})
        _context = {'request': request}
        serializer = BookSerializer(self.book, context=_context)
        # Only required parameters (pk) and author given as filter are included in serialization
        self.assertEquals(set(serializer.data.keys()), set(['isbn', 'author']))


class BookRateSerializerTests(TestCase):
    def setUp(self):
        bookModel = {'isbn': '0-306-40615-2', 'title': 'title', 'price': 10, 'author': 'author',
                                 'image': 'test.jpg'}
        # Adding serializer extra fields that not required in model
        self.book = Book(**bookModel)
        self.user = User(user_id='3', name='test')
        self.book.save()
        self.user.save()
        self.expectedRateData = {'user_id': self.user.pk, 'rating': 4}
        self.fullRateData = {'book_id': self.book, 'user_id': self.user, 'rating': 4}
        # Adding serializer extra fields that not required in model
        self.rate = Rate(**self.fullRateData)

    def test_retrieve_rate_should_work(self):
        """
        We check that serialization an existing model is working
        """
        serializer = BookRateSerializer(self.rate)
        # Check we have a correct dictionary serialized with python datatypes
        # book_id is excluded from serialization
        self.assertEquals(serializer.data, self.expectedRateData)

    def test_create_valid_rate_should_work(self):
        """
        We check deserialization process of a dictionary where we get a valid object model with validations succeded
        """
        serializer = RateSerializer(data={'rating': 4, 'user_id': self.user.pk, 'book_id': self.book.pk})
        # Check validations works
        self.assertEquals(serializer.is_valid(), True)
        # Check object created is what we expect
        self.assertEquals(serializer.object, self.rate)
        self.assertEquals(serializer.data['rating'], 4)
