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
from users.views import UserCollectionView, CurrentUserView
from books.views import PurchaseBookView

urlpatterns = patterns('',
    url(r'^$', UserCollectionView.as_view()),
    url(r'^me/?$', CurrentUserView.as_view(), name='me'),
    url(r'^me/books/(?P<isbn>[0-9xX -]+)/?$', PurchaseBookView.as_view(), name='purchase'),
)
