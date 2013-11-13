'''
(c) Copyright 2013 Telefonica, I+D. Printed in Spain (Europe). All Rights
Reserved.

The copyright to the software program(s) is property of Telefonica I+D.
The program(s) may be used and or copied only with the express written
consent of Telefonica I+D or in accordance with the terms and conditions
stipulated in the agreement/contract under which the program(s) have
been supplied.
'''
from rest_framework.generics import GenericAPIView
from commons.exceptions import EbooksException
from commons.serializers import Page, PaginationSerializer


class CustomGenericAPIView(GenericAPIView):
    """
    Overrides GenericAPIView to implement this extra logic:
        - avoid handle exceptions. This will bedone in another separate layer.
        - allow serializer class by method
        - allow pagination
    """
    pagination_serializer_class = PaginationSerializer

    def handle_exception(self, exc):
        # Call super method to handle_exception
        resp = super(CustomGenericAPIView, self).handle_exception(exc)
        # Change default key value detail and use description instead
        # TODO localize message
        custom_data = {'description': resp.data['detail']}

        # Add error_code to response error depending on exc
        if isinstance(exc, EbooksException):
            if exc.error_code:
                custom_data['error_code'] = exc.error_code

        # Update Error response with custom and localized data
        resp.data = custom_data
        return resp

    def get_serializer_class(self):
        """
        Override default to allow serializer class per method.
        For example, to use a different serializer in post you should define:
               serializer_class_post = MyPostSerializer
        """
        serializer_class = getattr(self, 'serializer_class_%s' % self.request.method.lower(), None)
        if serializer_class is None:
            serializer_class = GenericAPIView.get_serializer_class(self)
        return serializer_class

    def get_pagination_serializer(self, obj, offset, limit):
        """
        Return a serializer instance to use with paginated data.
        """

        class SerializerClass(self.pagination_serializer_class):
            class Meta:
                object_serializer_class = self.get_serializer_class()

        pagination_serializer_class = SerializerClass
        context = self.get_serializer_context()
        page = Page(obj, offset, limit)
        return pagination_serializer_class(instance=page, context=context)
