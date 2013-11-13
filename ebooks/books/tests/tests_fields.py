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
from django.core.exceptions import ValidationError
from books.models import Book


class BooksFieldsTest(TestCase):

    book = Book(isbn='99921-58-10-7', price=10, title='T', author='a', summary='Su', image='file.png')

    def test_isbn_field_with_alphanumerics_should_fail(self):
        self.book.isbn = 'aaabbbcccd'
        self.assertRaises(ValidationError, self.book.full_clean)

    def test_isbn_field_empty_should_fail(self):
        self.book.isbn = ''
        self.assertRaises(ValidationError, self.book.full_clean)

    def test_isbn_field10_short_should_fail(self):
        self.book.isbn = '99921-58-10'
        self.assertRaises(ValidationError, self.book.full_clean)

    def test_isbn_field13_short_should_fail(self):
        self.book.isbn = '978-0-306-4061-7'
        self.assertRaises(ValidationError, self.book.full_clean)

    def test_isbn10_field_valid_should_work(self):
        self.book.isbn = '0-306-40615-2'
        self.book.full_clean()

    def test_isbn10_field_invalid_checksum_should_fail(self):
        self.book.isbn = '0-306-40615-X'
        self.assertRaises(ValidationError, self.book.full_clean)

    def test_isbn13_field_valid_should_work(self):
        self.book.isbn = '978-0-306-40615-7'
        self.book.full_clean()

    def test_isbn13_invalid_checksum_should_fail(self):
        self.book.isbn = '978-0-306-40615-5'
        self.assertRaises(ValidationError, self.book.full_clean)
