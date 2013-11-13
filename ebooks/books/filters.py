'''
Created on 13/02/2013

@author: eag
'''
from models import Book
from commons.filters import MultipleElementsFilter, MultipleCharElementsField
import django_filters


class BookFilter(django_filters.FilterSet):
    topics = MultipleElementsFilter(field_class=MultipleCharElementsField, name='topics')
    price = django_filters.NumberFilter(lookup_type='exact')
    isbns = MultipleElementsFilter(field_class=MultipleCharElementsField, name='isbn')

    class Meta:
        model = Book
        fields = ['author', 'price', 'isbns', 'title', 'topics']

    def __init__(self, *args, **kwargs):
        super(BookFilter, self).__init__(*args, **kwargs)
