'''
(c) Copyright 2013 Telefonica, I+D. Printed in Spain (Europe). All Rights
Reserved.

The copyright to the software program(s) is property of Telefonica I+D.
The program(s) may be used and or copied only with the express written
consent of Telefonica I+D or in accordance with the terms and conditions
stipulated in the agreement/contract under which the program(s) have
been supplied.
'''
from rest_framework import serializers
from models import Book
from users.models import Rate
from commons.serializers import ExcludeFieldMixing
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404


class RateSerializer(serializers.ModelSerializer):
    """
    Read-Write Serializer class for put operations with rates.
    """

    class Meta:
        model = Rate
        exclude = ('id', 'user_id')


class BookRateSerializer(serializers.ModelSerializer):
    """
    Read-Only Serializer class for book request.
    book_id field is excluded.
    """

    class Meta:
        model = Rate
        exclude = ('id', 'book_id')


class BookSerializer(ExcludeFieldMixing, serializers.ModelSerializer):
    """
    Serializer class for books, including isbn (pk in model) and ratings from Rate model
    """
    # We include ratings of a book for listings (foreign key not inside model). This is a read_only field by default
    # ratings must be the name of foreign key in related model
    ratings = BookRateSerializer(many=True)

    # avg_rate is not a model field, but a convenience field, calculated based on current model information.
    # It is calculated using the method given as a parameter for the SerializerMethodField constructor.
    avg_rate = serializers.SerializerMethodField('calc_avg_rating')

    class Meta:
        model = Book
        mandatory_fields = ('isbn',)
        # avg_rate and num_ratings are read-only fields, calculated and updated on every rating by users
        # total_rating and total_sqrd_rating are also read_only
        read_only_fields = ('num_ratings', 'total_rating', 'total_sqrd_rating',)
        # total rating and squared total rating are only for internal purposes, and must not be sent to the user
        exclude = ('total_rating', 'total_sqrd_rating',)

    def calc_avg_rating(self, book):
        # Take advantage of the current model information to obtain the average rating and return it to the user,
        # even when it is not present in the database.
        if book.num_ratings > 0:
            return book.total_rating / book.num_ratings
        return 0


class BookUpdatedSerializer(BookSerializer):
    """
    Serializer class for update books. special case of BookSerializer
    when we get object for update in restore_object as not provided
    """
    def restore_object(self, attrs, instance=None):
        try:
            # Recover service from view, inside context
            view = self.context.get('view')
            instance = view.service.get(view.kwargs['pk'])
        except ObjectDoesNotExist:
            raise Http404
        return BookSerializer.restore_object(self, attrs, instance=instance)
