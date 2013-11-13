'''
(c) Copyright 2013 Telefonica, I+D. Printed in Spain (Europe). All Rights
Reserved.

The copyright to the software program(s) is property of Telefonica I+D.
The program(s) may be used and or copied only with the express written
consent of Telefonica I+D or in accordance with the terms and conditions
stipulated in the agreement/contract under which the program(s) have
been supplied.
'''
import functools
from rest_framework.response import Response
from rest_framework import status
from rest_framework.serializers import Field
from rest_framework.pagination import BasePaginationSerializer


def deserialize_input(partial=False, validate=True):
    """
    Validate request.DATA and extra values provided in view using serializer class
    defined in view.
    If validation is not correct a Response error is thrown.
    If validation succeded, view method will be called.

    By default all serializer fields are required for validation; this can be changed
    using partial = True (for put methods when we don't want all validations).

    :param partial: Validate only informed fields in serializer
    :param validate: Don't run serializer validations

    """
    # Decorator defined inside to receive input params
    def applyDecorator(f):

        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            called_view = args[0]
            request = args[1]
            # include fields not coming in request for validation
            compose_data = request.DATA.copy()
            # TODO complex json
            compose_data.update(kwargs)

            # Get serializer and check data is valid
            serializer = called_view.get_serializer(data=compose_data, partial=partial)
            if validate and not serializer.is_valid():
                # Default validation error is 2
                return Response({'error_code': 2, 'description': serializer.errors},
                                status=status.HTTP_400_BAD_REQUEST)

            # validation succed, we update request.DATA with input already validated
            validated_data = serializer.data
            # Include m2m data and related data if available
            if getattr(serializer, 'm2m_data', None):
                validated_data.update(serializer.m2m_data)
            if getattr(serializer, 'related_data', None):
                validated_data.update(serializer.related_data)

            # update request.DATA and call the view
            request._data = validated_data
            return f(called_view, request, **kwargs)
        return wrapper
    return applyDecorator


class Page(object):
    """
    A base class to allow offset and limit when listing a queryset.
    This will be used in PaginatorSerializer
    """
    def __init__(self, queryset, offset=0, limit=10):
        self.count = queryset.count()
        self.object_list = queryset[offset:offset + limit]


class PaginationSerializer(BasePaginationSerializer):
    """
    An implementation of BasePaginationSerializer to use only
    count and results field (defined in BasePaginationSerializer
    """
    total_results = Field(source='count')


def serialize_output(many=False, status=status.HTTP_200_OK, page_limit=None):
    """
    Serialize and object or a queryset (many=True) using serializer class and returns a valid
    representation of the object/queryset.
    If the view already returns a response, anything is done.
    """
    def applyDecorator(f):

        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            called_object = args[0]
            request = args[1]
            # Get object or object list by calling the function
            obj = f(*args, **kwargs)

            if not isinstance(obj, Response):
                # Serialize data and return Response
                if page_limit and many:
                    # return paginated data using offset and limit
                    offset = request.GET.get('offset') or 0
                    limit = request.GET.get('limit') or page_limit

                    # offset and limit must be integer
                    serializer = called_object.get_pagination_serializer(obj, int(offset), int(limit))
                else:
                    serializer = called_object.get_serializer(obj, many=many)
                return Response(serializer.data, status=status)
            else:
                # We have a Response already...
                return obj
        return wrapper
    return applyDecorator


class ExcludeFieldMixing(object):
    """
    Mixer utility for excluding fields in serialization based on request parameter for GET Method.
    It will take a comma separated values of fields given in a request parameter and
    would exclude then from serialization output.

    Request parameter is 'filter' by default, but can be overriden in meta serializer options.
    Mandatory fields can be defined too. It should be mixed with a Serializer.

    For example, when defining Meta Serializer options:
        class SerializerExcluded(ExcludeFieldMixing, ModelSerializer)
            class Meta:
                model = MyModel
                request_filter = 'filter'
                mandatory_fields = ['mandatory_field']

    """

    def __init__(self, *args, **kwargs):
        self.request_filter = getattr(self.Meta, 'request_filter', 'filter')
        self.mandatory_fields = getattr(self.Meta, 'mandatory_fields', ())
        super(ExcludeFieldMixing, self).__init__(*args, **kwargs)

    def get_fields(self, *args, **kwargs):
        """
        Override default for excluding fields based on filter parameter (if given)
        """
        # Check meta for override defaults

        if 'request' in getattr(self, 'context', None):
            request = self.context['request']
            if self.request_filter in getattr(request, 'QUERY_PARAMS', None)\
                and getattr(request, 'method', None) == 'GET':
                # Add mandatory fields
                _included = list(self.mandatory_fields)
                for including_fields in request.QUERY_PARAMS[self.request_filter].split(','):
                    _included.append(including_fields)
                # Update required fields of serializer
                self.opts.fields = tuple(_included)
        return super(ExcludeFieldMixing, self).get_fields(*args, **kwargs)
