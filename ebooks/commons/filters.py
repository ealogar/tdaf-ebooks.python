'''
(c) Copyright 2013 Telefonica, I+D. Printed in Spain (Europe). All Rights
Reserved.

The copyright to the software program(s) is property of Telefonica I+D.
The program(s) may be used and or copied only with the express written
consent of Telefonica I+D or in accordance with the terms and conditions
stipulated in the agreement/contract under which the program(s) have
been supplied.
'''
from django.db.models import Q
from django import forms
from django.core.validators import EMPTY_VALUES
import django_filters
import functools
from rest_framework.settings import api_settings


class MultipleElementsField(object):
    '''
    Mixed class for dealing with multi fields objects spllited by a given separator.
    The validations of each element (after splitting) are delegated to each filter class by multiple inheritance
    '''
    separator = ','

    def __init__(self, separator=None, *args, **kwargs):
        if separator:
            self.separator = separator
        # We don't need to call super
        super(MultipleElementsField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        '''
            Override forms.Field.to_python to return a list of Objects each one of field.to_python type or None
        '''
        if value in EMPTY_VALUES:
            return None
        _multi = []
        value = value or ()

        for i_value in value.split(self.separator):
            _multi.append(super(MultipleElementsField, self).to_python(i_value))
        return _multi

    def validate(self, value):
        '''
            Override forms.Field.validate to perform validation in each element of the multi list
        '''
        if value in EMPTY_VALUES:
            return
        value = value or ()

        for i_value in value:
            super(MultipleElementsField, self).validate(i_value)

    def run_validators(self, value):
        '''
            Override forms.Field.run_validators to perform validators in each element of the multi list
        '''
        if value in EMPTY_VALUES:
            return
        value = value or ()

        for i_value in value:
            super(MultipleElementsField, self).run_validators(i_value)


class MultipleCharElementsField(MultipleElementsField, forms.CharField):
    '''
    Use the behaviour of MultipleElementsField for a filter of multiple fields of char type.
    Only inheritance is needed
    '''


class MultipleDecimalElementsField(MultipleElementsField, forms.DecimalField):
    '''
    Use the behaviour of MultipleElementsField for a filter of multiple fields of decimal type.
    Only inheritance is needed
    '''


# definition of Filters which use upper forms
class MultipleElementsFilter(django_filters.Filter):
    '''
     Extends Filter for filtering several objects splitted by a separator.
     keyword argument field_class must be defined
         valid field_class:
             MultipleCharElementsField
             MultipleDecimalElementsField
    '''
    def __init__(self, field_class, **kwargs):
        self.field_class = MultipleCharElementsField
        super(MultipleElementsFilter, self).__init__(**kwargs)

    def filter(self, qs, value):
        if value in EMPTY_VALUES:
            return qs
        value = value or ()

        q = Q()
        for v in value:
            q |= Q(**{self.name: v})
        return qs.filter(q)


def filter_queryset(f):
    """
    Filter queryset result of function using filter_backend provided
    by rest_framework.

    It must be used in a get method returning a queryset as result.
    """
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        # Get object or object list calling the function
        called_object = args[0]
        queryset = f(*args, **kwargs)
        if not api_settings.FILTER_BACKEND:
            return queryset
        backend = api_settings.FILTER_BACKEND()
        return backend.filter_queryset(called_object.request, queryset, called_object)

    return wrapper
