from django.db import models
from fields import ISBNField
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal


class Topic(models.Model):
    value = models.CharField(max_length=255, primary_key=True)

    def __unicode__(self):
        return u'%s' % self.value


class Book(models.Model):
    isbn = ISBNField(primary_key=True, error_messages={'unique': 'Already existing Book'})
    title = models.CharField(max_length=255)
    summary = models.TextField(blank=True)
    # decimal field will be rendered as string in json for avoiding lose precisions
    # https://github.com/tomchristie/django-rest-framework/issues/508
    price = models.DecimalField(max_digits=6, decimal_places=2)
    author = models.CharField(max_length=200)
    image = models.FilePathField(path="/ebooks/images", match="*.png$", recursive=True)
    topics = models.ManyToManyField(Topic)
    avg_rate = models.DecimalField(max_digits=4, decimal_places=2, default=Decimal('0.00'),
                                validators=[MinValueValidator(0), MaxValueValidator(5)])
    total_rating = models.DecimalField(max_digits=7, decimal_places=2, default=Decimal('0.00'))
    total_sqrd_rating = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    num_ratings = models.IntegerField(default=0)

    def __unicode__(self):
        return u'%s - %s' % (self.isbn, self.title)

    @property
    def has_low_price(self):
        """
        We define low price to be less than 5
        """
        return self.price <= 5

class Language(models.Model):
    name = models.CharField(max_length=200)

    def __unicode__(self):
        return u'%s' % self.name


class Error(models.Model):
    description = models.CharField(max_length=800)
    language = models.ForeignKey(Language)

    def __unicode__(self):
        return u'%s' % self.description
