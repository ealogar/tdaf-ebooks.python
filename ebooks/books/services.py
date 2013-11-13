'''
(c) Copyright 2013 Telefonica, I+D. Printed in Spain (Europe). All Rights
Reserved.

The copyright to the software program(s) is property of Telefonica I+D.
The program(s) may be used and or copied only with the express written
consent of Telefonica I+D or in accordance with the terms and conditions
stipulated in the agreement/contract under which the program(s) have
been supplied.
'''
from books.models import Book
from django.core.exceptions import ObjectDoesNotExist
from users.models import Rate
from commons.services import BaseModelService
from users.services import UserService
import logging


logger = logging.getLogger('ebooks')


class BookService(BaseModelService):
    """
    Service CRUD for book objects
    """
    model = Book
    user_service = UserService()

    def update_book_avg_rate(self, book, rate, existing_rate, previous_rating):
        """
        Update avg_rate of book with rate; rate could be new or update existing
        depending on the value of existing_rate

        :param book: book instance
        :param rate: rate instance
        :param existing_rate: whether rate is new or update existing value
        :param previous_rating: the previous value of the rating for the same user, if available.
                                When rate is new, this param is zero.
        """
        if existing_rate is False:
            book.num_ratings = book.num_ratings + 1

        # Consider the previous rating for this user, if applicable, when calculating the new totals
        book.total_rating += (rate.rating - previous_rating)
        book.total_sqrd_rating = book.total_sqrd_rating - previous_rating * previous_rating\
                                 + rate.rating * rate.rating
        book.save()

    def buy_book(self, book_id, user_id):
        """
        Add a new book to existing user (operation of purchase).

        :param book_id: isbn of the book
        :param user_id: user identifier who purchase the book
        """
        # book is default model in UserService
        book = self.get(book_id)
        user = self.user_service.get(user_id)

        logger.info("Add book %s to user %s", book_id, user_id)
        # TODO Add purchases to keep track of books purchased
        user.books.add(book)
        user.save()

    def create_book_with_topics(self, book_fields, topics):
        """
        Create a book with all fields and topics
        """
        logger.info("Creating book %s in database with topics %s", book_fields, topics)
        book = self.create(Book(**book_fields))

        # Add topics M2M relationships
        book.topics.clear()
        for topic in topics:
            book.topics.add(topic)

        return book

    def update_book_with_topics(self, isbn, book_fields):
        """
        Create a book with all fields and topics
        """
        # Get book
        book = self.get(isbn)

        logger.info("Updating the book %s to %s", isbn, book_fields)
        updated_fields = ('title', 'summary', 'price', 'author', 'image')
        for key in updated_fields:
            if key in book_fields:
                setattr(book, key, book_fields[key])
        self.update(book)

        if 'topics' in book_fields:
            # Add topics M2M relationships
            book.topics.clear()
            for topic in book_fields['topics']:
                book.topics.add(topic)
            logger.debug("Updated topics of book %s to %s", isbn, book_fields['topics'])

        return book


class RateService(BaseModelService):
    """
    Service logic for Rate, A rate can be done by an authenticated user
    and existing book.
    """
    # RateService base model
    model = Rate
    # Services for complex operations
    user_service = UserService()
    book_service = BookService()

    def add_or_update_rate(self, rating, book_id, user_id):
        """
        Add a new rate or update existing one in a book for an existing user.

        :param rating: rate value
        :param book_id: book isbn to make the rate
        :param user_id: user identifier who will make the rate
        """
        # Get existing rate (for update/create)
        rate = None
        book = self.book_service.get(book_id)
        user = self.user_service.get(user_id)

        try:
            rate = self.model.objects.get(book_id=book, user_id=user)
            logger.info("User %s is updating his rate of book %s from %s to %s",
                         user_id, book_id, rate.rating, rating)
        except ObjectDoesNotExist:
            # we don't have to propagate this exception
            logger.info("User %s is adding a new rate of %s to book %s", user_id, rating, book_id)

        if rate is None:
            # New rate will be created
            rate = Rate(rating=rating, book_id=book, user_id=user)
            created = True
            previous_rating = 0
        else:
            # We will update old rating of user
            created = False
            previous_rating = rate.rating

        # Update/Create new value
        rate.rating = rating
        rate.save()

        # Update global rate of book
        self.book_service.update_book_avg_rate(book, rate, not(created), previous_rating)

        return created
