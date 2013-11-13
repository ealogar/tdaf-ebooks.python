# development settings
from common import *
from os.path import join, normpath

DEBUG = True

# ######### DATABASE CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': normpath(join(DJANGO_ROOT, 'ebooks.db')),
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}

# Override loggers to use console
# Note that default print messages will be redirected to console
# like requests made to django
LOGGING['loggers'] = {
        '': {
            'handlers': ['file'],
            'propagate': True,
            'level': 'DEBUG',
        },
        'django': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': True,
            }
    }

INSTALLED_APPS = INSTALLED_APPS + ('django_nose',)

TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

NOSE_ARGS = ['-s',
             '-v',
             '--cover-erase',
             '--cover-branches',
             '--with-cov',
             '--cover-package=books,commons,users',
             '--cover-html'
             ]
