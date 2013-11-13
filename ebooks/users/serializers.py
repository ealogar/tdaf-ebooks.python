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
from models import User
from books.fields import ISBNField
from django.core.exceptions import ValidationError
from books.models import Topic


class UserSerializer(serializers.ModelSerializer):
    # We use SlugRelatedField to return just isbn value
    # books not allowed to be modified in user operations, by default read_only is true
    books = serializers.SlugRelatedField(slug_field='isbn', many=True, read_only=True)

    class Meta:
        model = User
        read_only_fields = ('user_id',)


class BookPurchasedSerializer(serializers.Serializer):
    """
    Serialize the purchase operation, as we don't have a model to represent
    the purchase, we don't use ModelSerializer
    """

    isbn = serializers.CharField()

    def validate_isbn(self, attrs, source):
        value = attrs[source]
        if ISBNField.is_isbn10(value) is False and ISBNField.is_isbn13(value) is False:
            raise ValidationError('Non valid ISBN format : %s' % value)
        return attrs

    def restore_object(self, attrs, instance=None):
        """
        Control how deserialized object should work.
        For this serializer we only want a dict with validated params
        """
        return dict(attrs)


class TopicSerializer(serializers.ModelSerializer):

    class Meta:
        model = Topic
