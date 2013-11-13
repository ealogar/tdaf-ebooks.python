'''
(c) Copyright 2013 Telefonica, I+D. Printed in Spain (Europe). All Rights
Reserved.

The copyright to the software program(s) is property of Telefonica I+D.
The program(s) may be used and or copied only with the express written
consent of Telefonica I+D or in accordance with the terms and conditions
stipulated in the agreement/contract under which the program(s) have
been supplied.
'''
from rest_framework import status
from filters import BookFilter
from serializers import BookSerializer, RateSerializer
from services import RateService
from rest_framework.response import Response
from commons.serializers import deserialize_input, serialize_output
from commons.filters import filter_queryset
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from users.serializers import BookPurchasedSerializer, TopicSerializer
from books.services import BookService
from users.services import TopicService
from books.models import Book
from commons.views import CustomGenericAPIView
from commons.authentication.permissions import IsAdminOrReadOnly
from books.serializers import BookUpdatedSerializer


class BookItemView(CustomGenericAPIView):
    service = BookService()
    serializer_class = BookSerializer
    serializer_class_post = BookUpdatedSerializer

    permission_classes = (IsAdminOrReadOnly,)

    @serialize_output(many=False)
    def get(self, request, *args, **kwargs):
        return self.service.get(kwargs['pk'])

    @transaction.commit_on_success
    @serialize_output(many=False)
    @deserialize_input(partial=True)
    def post(self, request, *args, **kwargs):
        # partial input validated and full data is in request.DATA
        return self.service.update_book_with_topics(kwargs['pk'], request.DATA)

    def delete(self, request, *args, **kwargs):

        self.service.delete(kwargs['pk'])

        return Response(status=status.HTTP_204_NO_CONTENT)


class BookCollectionView(CustomGenericAPIView):
    # BookSerializer can dynamically exclude fields from output based on a input
    # parameter coming in request
    serializer_class = BookSerializer
    service = BookService()
    # We use filter of rest_framework, filter_class must be defined and a model in view too
    filter_class = BookFilter
    model = Book

    permission_classes = (IsAdminOrReadOnly,)

    # decorators are applied from innermost to outermost
    @serialize_output(many=True, page_limit=10)
    @filter_queryset
    def get(self, request, *args, **kwargs):
        """
        Get the list of books, filtering the result and excluding custom fields in output
        """
        return self.service.get_all()

    @transaction.commit_on_success
    @serialize_output(many=False, status=status.HTTP_201_CREATED)
    @deserialize_input(partial=False)
    def post(self, request, *args, **kwargs):
        # Get required fields and topics
        book_required_keys = ('isbn', 'title', 'summary', 'price', 'author', 'image')
        book_required_fields = dict([(key, request.DATA[key]) for key in book_required_keys])

        return self.service.create_book_with_topics(book_required_fields, request.DATA['topics'])


class TopicCollectionView(CustomGenericAPIView):

    service = TopicService()
    serializer_class = TopicSerializer

    permission_classes = (IsAdminOrReadOnly,)

    def get(self, request, *args, **kwargs):
        """
        Return all topic values in a custom ouput : ['topic1', 'topic2',...]
        """
        data = [topic.value for topic in self.service.get_all()]

        return Response(data, status=status.HTTP_200_OK)

    @serialize_output(many=False, status=status.HTTP_201_CREATED)
    @deserialize_input(partial=False)
    def post(self, request, *args, **kwargs):
        return self.service.create(request.DATA['value'])


class AddRateView(CustomGenericAPIView):
    """
    View for rating an existing book by a given authenticated user
    """
    serializer_class = RateSerializer
    rate_service = RateService()

    # only authenticated users may access this view
    permission_classes = (IsAuthenticated,)

    # instead of using Transaction Middleware globally we include transaction only in required views
    @transaction.commit_on_success
    # validate input data and create a serializer with valid data
    @deserialize_input(partial=True)
    def put(self, request, *args, **kwargs):
        """
        Updates/creates a rate in a book by authenticated user.
        As user and book are informed in url, we treat this put
        method as post if rate doesn't exist.
        After saving rate, average rate of book will be updated.
        """

        # Use service for create rate and related operations, rating and book_id are mandatory in serializer
        created = self.rate_service.add_or_update_rate(request.DATA['rating'], request.DATA['book_id'],
                                                       request.user.id)

        # Check if new object will be created or not to return appropiate response code
        success_status_code = {True: status.HTTP_201_CREATED, False: status.HTTP_200_OK}

        # We only return value in serialized data, We don't use serializer
        return Response({'rating': request.DATA['rating'], 'user_id': request.user.id},
                        status=success_status_code[created])


class PurchaseBookView(CustomGenericAPIView):
    """
    View for purchasing a book.
    """
    serializer_class = BookPurchasedSerializer
    service = BookService()

    # only authenticated users may access this view
    permission_classes = (IsAuthenticated,)

    @serialize_output(many=False, status=status.HTTP_201_CREATED)
    @deserialize_input(partial=True)
    def put(self, request, *args, **kwargs):
        """
        Buy a new book for a given user. Same book can be purchased several times.
        """
        self.service.buy_book(request.DATA['isbn'], request.user.id)
        # Return request.DATA with isbn, serializer will return appropiate values
        return request.DATA
