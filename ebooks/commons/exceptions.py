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
from rest_framework.exceptions import APIException


class EbooksException(APIException):
    """
    Generic Exception for ebooks. It's used when an unexpected error appears
    when dealing with any request.
    We use this exception to return inmediately a Response of error and avoid
    further processing in rest_framework.
    Arguments:
          - detail: Description of error to be returned
          - status_code: Http code of response
    """

    def __init__(self, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                       detail='Error processing request. Try again later',
                       error_code=None):
        self.detail = detail or self.default_detail
        self.status_code = status_code or self.default_status_code
        self.error_code = error_code


class NotFoundException(EbooksException):
    """
    Particular case of EbooksException when no object is found.
    """

    def __init__(self, detail='Requested object not found', error_code=None):
        super(NotFoundException, self).__init__(status_code=status.HTTP_404_NOT_FOUND,
                                                detail=detail, error_code=error_code)


class AlreadyExistingException(EbooksException):
    """
    Particular case of EbooksException when object is already created.
    """

    def __init__(self, detail='Requested object not found', error_code=None):
        super(AlreadyExistingException, self).__init__(status_code=status.HTTP_400_BAD_REQUEST,
                                                       detail=detail, error_code=error_code)
