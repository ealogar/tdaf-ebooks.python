'''
(c) Copyright 2013 Telefonica, I+D. Printed in Spain (Europe). All Rights
Reserved.

The copyright to the software program(s) is property of Telefonica I+D.
The program(s) may be used and or copied only with the express written
consent of Telefonica I+D or in accordance with the terms and conditions
stipulated in the agreement/contract under which the program(s) have
been supplied.
'''
from django.http import QueryDict


def get_value_from_request_DATA(input_dict, key, multi_value=False):
    """
    Utility function to retrieve the value of a key in request.DATA in django.
    request.DATA may be a QueryDict or a simple dict depending on content-type.
    """
    if isinstance(input_dict, QueryDict):
        return get_value_from_querydict(input_dict, key, multi_value=multi_value)
    elif isinstance(input_dict, dict):
        return input_dict.get(key)
    else:
        raise Exception("this function must be called with a django QueryDict or dictionary")


def get_value_from_querydict(input_dict, key, multi_value=False):
    """
    Utility function to retrieve the value of a key in a queryDict.
    If querydict has not key, None is returned.
    If multi_value is true, the key is supposed to have multiple values
    and a list is returned, otherwise the get is used to retrieve the firs value.
        See also:
           https://docs.djangoproject.com/en/dev/ref/request-response/#querydict-objects
    """
    if not isinstance(input_dict, QueryDict) and not isinstance(input_dict, dict):
        raise Exception("this function must be called with a django QueryDict instance or dictionary")
    if key in input_dict:
        if multi_value:
            return input_dict.getlist(key)
        else:
            return input_dict.get(key)
    else:
        return None
