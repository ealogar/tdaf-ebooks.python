from django.db import models

from books.models import Book, Topic
from django.core.validators import MaxValueValidator, MinValueValidator


class User(models.Model):
    user_id = models.CharField(max_length=255, primary_key=True)
    name = models.CharField(max_length=300)
    books = models.ManyToManyField(Book)
    topics = models.ManyToManyField(Topic)

    def __unicode__(self):
        return u'%s' % self.user_id


class Rate(models.Model):
    rating = models.DecimalField(max_digits=4, decimal_places=2,
                                validators=[MinValueValidator(0), MaxValueValidator(5)])
    user_id = models.ForeignKey(User, related_name='ratings')
    book_id = models.ForeignKey(Book, related_name='ratings')

    class Meta:
        unique_together = ('user_id', 'book_id')

    def __unicode__(self):
        return u'%s -> %s (%d)' % (self.user_id.pk, self.book_id.pk, self.value)
