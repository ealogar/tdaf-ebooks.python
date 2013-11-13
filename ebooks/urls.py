'''
(c) Copyright 2013 Telefonica, I+D. Printed in Spain (Europe). All Rights
Reserved.

The copyright to the software program(s) is property of Telefonica I+D.
The program(s) may be used and or copied only with the express written
consent of Telefonica I+D or in accordance with the terms and conditions
stipulated in the agreement/contract under which the program(s) have
been supplied.
'''
from django.conf.urls.defaults import patterns, include, url
from books.views import TopicCollectionView

urlpatterns = patterns('',
    url(r'^ebucxop/books/?', include('books.urls')),
    url(r'^ebucxop/users/?', include('users.urls')),
    url(r'^ebucxop/topics/?$', TopicCollectionView.as_view())
)
