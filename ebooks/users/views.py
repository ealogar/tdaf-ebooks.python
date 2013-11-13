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
from serializers import UserSerializer
from commons.serializers import deserialize_input, serialize_output
from users.services import UserService
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from commons.utils import get_value_from_request_DATA
from commons.views import CustomGenericAPIView


class UserCollectionView(CustomGenericAPIView):
    serializer_class = UserSerializer
    service = UserService()

    @serialize_output(many=True, page_limit=10)
    def get(self, request, *args, **kwargs):
        return self.service.get_all()

    @serialize_output(many=False, status=status.HTTP_201_CREATED)
    @deserialize_input(partial=False)
    def post(self, request, *args, **kwargs):
        # As topics is many2many relation, values in m2m_data
        return self.service.create_user_with_topics(request.DATA['name'],
                                                    request.DATA['topics'])


class CurrentUserView(CustomGenericAPIView):
    """
    Operations for authenticated user: retrieve, update and destroy.
    Only authenticated users are allowed to use this view.
    """
    serializer_class = UserSerializer
    service = UserService()

    # only authenticated users may access this view
    permission_classes = (IsAuthenticated,)

    @serialize_output(many=False)
    def get(self, request, *args, **kwargs):
        return self.service.get(request.user.id)

    @transaction.commit_on_success
    @serialize_output(many=False)
    def post(self, request, *args, **kwargs):
        # We don't use UserSerializer for validate input as input does not fit User model:
        #        name and topics may be informed or not.
        # We use serializer just for returning output

        return self.service.update_name_or_topics(request.user.id,
                                             get_value_from_request_DATA(request.DATA, 'name'),
                                             get_value_from_request_DATA(request.DATA, 'topics', True))

    def delete(self, request, *args, **kwargs):

        self.service.delete(request.user.id)

        return Response(status=status.HTTP_204_NO_CONTENT)
