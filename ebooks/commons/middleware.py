'''
(c) Copyright 2013 Telefonica, I+D. Printed in Spain (Europe). All Rights
Reserved.

The copyright to the software program(s) is property of Telefonica I+D.
The program(s) may be used and or copied only with the express written
consent of Telefonica I+D or in accordance with the terms and conditions
stipulated in the agreement/contract under which the program(s) have
been supplied.
'''
import uuid
from django.conf import settings
from commons import local_context


class RequestTransactionIDMiddleware(object):
    """
    Middleware class to add to local thread a unique transaction id to be used
    in logging.
    REQUEST_TRANSACTION_ID_HEADER value can be set in settings, by default is HTTP_X_TRANSACTION_ID.
    When the REQUEST_TRANSACTION_ID_HEADER is provided in request, that value is used, otherwise a unique
    identifier is generated.
    """

    def __init__(self):
        self.request_transaction_id_header = getattr(settings, 'REQUEST_TRANSACTION_ID_HEADER',
                                                               'HTTP_X_TRANSACTION_ID')

    def process_request(self, request):
        request_transaction_id = self._get_request_transaction_id(request)
        local_context.transaction_id = request_transaction_id
        return None

    def _get_request_transaction_id(self, request):
        meta = request.META
        return getattr(meta, self.request_transaction_id_header, self._generate_id())

    def _generate_id(self):
        return uuid.uuid4().hex
