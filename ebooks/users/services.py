'''
(c) Copyright 2013 Telefonica, I+D. Printed in Spain (Europe). All Rights
Reserved.

The copyright to the software program(s) is property of Telefonica I+D.
The program(s) may be used and or copied only with the express written
consent of Telefonica I+D or in accordance with the terms and conditions
stipulated in the agreement/contract under which the program(s) have
been supplied.
'''
from commons.services import BaseModelService
from users.models import User
from commons.exceptions import AlreadyExistingException
from books.models import Topic
import logging

logger = logging.getLogger('ebooks')


class TopicService(BaseModelService):
    """
    Service CRUD for Topic objects
    """
    model = Topic

    def create(self, topic_name):

        return BaseModelService.create(self, Topic(value=topic_name))


class UserService(BaseModelService):
    """
    Service logic for Rate, A rate can be done by an authenticated user
    and existing book.
    """
    # default model for userservice
    model = User
    # we need more models for complex operations
    topic_service = TopicService()

    def create_user_with_topics(self, name, topics):
        """
        Create a user with given name and topics[]
        """
        # TODO get user from TDA
        if name == 'Aladdin':
            tda_id = '1'
        elif name == 'admin':
            tda_id = '2'
        else:
            tda_id = '10'

        # Check user not already created
        if self.model.objects.filter(user_id=tda_id).exists():
            raise AlreadyExistingException(detail='User with name %s already created' % name, error_code=1)

        logger.info("Creating user %s in database with TDA id %s", name, tda_id)
        user = self.create(User(user_id=tda_id, name=name))

        logger.debug("Adding topics %s to user" % topics)
        for topic in topics:
            user.topics.add(topic)

        return user

    def update_name_or_topics(self, user_id, name, topics):
        """
        update user name or topics
        """
        # Get user
        user = self.get(user_id)

        if name is not None:
            logger.info("Updating name of user from %s to %s", user.name, name)
            user.name = name
            self.update(user)

        if topics is not None:
            logger.info("Updating topics of user to %s", topics)
            user.topics.clear()
            for topic_value in topics:
                topic = self.topic_service.get(topic_value)
                user.topics.add(topic)

        return user
