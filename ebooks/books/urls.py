'''
(c) Copyright 2013 Telefonica, I+D. Printed in Spain (Europe). All Rights
Reserved.

The copyright to the software program(s) is property of Telefonica I+D.
The program(s) may be used and or copied only with the express written
consent of Telefonica I+D or in accordance with the terms and conditions
stipulated in the agreement/contract under which the program(s) have
been supplied.
'''
from django.conf.urls.defaults import patterns, url
from views import BookItemView, BookCollectionView, AddRateView

urlpatterns = patterns('',
    url(r'^(?P<pk>[0-9xX -]+)/?$', BookItemView.as_view()),
    url(r'^$', BookCollectionView.as_view()),
    url(r'^(?P<book_id>[0-9xX -]+)/ratings/me/?$', AddRateView.as_view()),
)
