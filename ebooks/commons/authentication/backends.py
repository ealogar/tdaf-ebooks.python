'''
(c) Copyright 2013 Telefonica, I+D. Printed in Spain (Europe). All Rights
Reserved.

The copyright to the software program(s) is property of Telefonica I+D.
The program(s) may be used and or copied only with the express written
consent of Telefonica I+D or in accordance with the terms and conditions
stipulated in the agreement/contract under which the program(s) have
been supplied.
'''
from django.contrib.auth.models import User
from rest_framework.exceptions import NotAuthenticated
import functools
from rest_framework.request import Request


class TdaBackend(object):
    """
    authenticate a user in TDAccount with login provided.
    This should configured as a backend authentication in django.
    Rest_framework will delegate authentication to this backend
    """
    supports_inactive_user = True
    supports_object_permissions = False
    supports_anonymous_user = False

    def authenticate(self, username=None, password=None):
        if username is None:
            return None
        user = User(username, password)
        # TODO Perform authentication against TDA
        if username == 'Aladdin' and password == 'open sesame':
            user.id = 1
            user.is_staff = False
        elif username == 'admin' and password == 'admin':
            user.id = 2
            user.is_staff = True
        else:
            user = None
        return user


def add_authenticated_user(f):
    """
    Add identifier of authenticated user as pk argument for rest framework
    """
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        called_object = args[0]
        request = args[1]
        if isinstance(request, Request):
            if request.user and request.user.id:
                called_object.kwargs['pk'] = unicode(request.user.id)
            else:
                raise NotAuthenticated
        else:
            raise Exception("decorator must be used in rest_framework views methods")

        return f(*args, **kwargs)
    return wrapper
