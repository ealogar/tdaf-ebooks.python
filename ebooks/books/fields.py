from django.db import models
from django.core.exceptions import ValidationError


class ISBNField(models.CharField):
    """
    Custom Field for using in models representing an isbn character.
    It behaves like a standard CharField but performs validation of isbn10 and isbn13.
    """
    __metaclass__ = models.SubfieldBase

    def __init__(self, *args, **kwargs):
        # Max lenght is required in char field 13 digits + 5 hyphens is maximun size
        if 'max_length' not in kwargs:
            kwargs['max_length'] = 18
        super(ISBNField, self).__init__(self, *args, **kwargs)

    def validate(self, value, model_instance):
        # Remove hyphen or spaces (separating parts if given)
        if ISBNField.is_isbn10(value) is False and ISBNField.is_isbn13(value) is False:
            raise ValidationError('Non valid ISBN format')

    @staticmethod
    def is_isbn10(isbn10):
        """
        Check a given string is a valid isbn10 format
        See http://en.wikipedia.org/wiki/International_Standard_Book_Number
        """
        # Remove hyphens and space (valid in isbn format)
        isbn10 = isbn10.rstrip().upper().replace(' ', '').replace('-', '')
        if len(isbn10) != 10:
            return False
        try:
            r = sum((10 - i) * (int(x) if x != 'X' else 10) for i, x in enumerate(isbn10))
            return r % 11 == 0
        except ValueError:
            return False

    @staticmethod
    def is_isbn13(isbn13):
        """
        Check a given string is a valid isbn13 format
        See http://en.wikipedia.org/wiki/International_Standard_Book_Number
        """
        # Remove hyphens and space (valid in isbn format)
        isbn13 = isbn13.rstrip().upper().replace(' ', '').replace('-', '')
        if isbn13.isdigit() is False:
            return False
        total = sum(int(num) * weight for num, weight in zip(isbn13, (1, 3) * 6))
        ck = (10 - total) % 10
        return ck == int(isbn13[-1])
