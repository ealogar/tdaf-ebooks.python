'''
(c) Copyright 2013 Telefonica, I+D. Printed in Spain (Europe). All Rights
Reserved.

The copyright to the software program(s) is property of Telefonica I+D.
The program(s) may be used and or copied only with the express written
consent of Telefonica I+D or in accordance with the terms and conditions
stipulated in the agreement/contract under which the program(s) have
been supplied.
'''
from django.core.exceptions import ObjectDoesNotExist
from commons.exceptions import NotFoundException


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class BaseModelService(object):
    """
    Implement common utilities for services using django models; it also implements singleton pattern
    """
    __metaclass__ = Singleton

    def __init__(self, *args, **kwargs):
        # ensure model is defined
        if getattr(self, 'model') is None:
            raise ValueError("BaseModelService requires a valid django model class defined")
        super(BaseModelService, self).__init__(*args, **kwargs)

    def get(self, element_id):
        """
        Retrieve a single element with id from default model of service.

        :param id: Primary key of the element
        :rtype: Element retrieved
        :raises: NotFoundException, if no element found
        """
        try:
            element = self.model.objects.get(pk=element_id)
        except ObjectDoesNotExist:
            raise NotFoundException('Object with pk %s not found' % element_id)
        except (AttributeError, TypeError):
            raise ValueError("Model class of service doesn't seem to be a valid Model: objects.get not existing")
        else:
            return element

    def get_all(self):
        """
        Retrieve all elements

        :param id: Primary key of the element
        :rtype: queryset of results
        """
        try:
            qs = self.model.objects.all()
        except (AttributeError, TypeError):
            raise ValueError("Model class of service doesn't seem to be a valid Model: objects.get not existing")
        else:
            return qs

    def create(self, element):
        """
        Create a new element and return pk
        """
        try:
            element.save()
        except (AttributeError, TypeError):
            raise ValueError("Element %s doesn't seem to be a valid Model instance" % element)
        else:
            return element

    def update(self, element):
        """
        update a element calling create as django model update works in that way
        """
        return self.create(element)

    def delete(self, element_id):
        """
        Delete the element with given element_id
        """
        try:
            obj = self.model.objects.get(pk=element_id)
            obj.delete()
        except ObjectDoesNotExist:
            raise NotFoundException('Object with pk %s not found' % element_id)
