'''
(c) Copyright 2013 Telefonica, I+D. Printed in Spain (Europe). All Rights
Reserved.

The copyright to the software program(s) is property of Telefonica I+D.
The program(s) may be used and or copied only with the express written
consent of Telefonica I+D or in accordance with the terms and conditions
stipulated in the agreement/contract under which the program(s) have
been supplied.
'''
from common import *
from os.path import normpath, join, exists
from os import makedirs

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
            'level': 'DEBUG',
            'propagate': True,
            }
    }

# Integrate nose with django. django-nose plugin
INSTALLED_APPS = INSTALLED_APPS + ('django_nose', )

TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
# cobertura dir must be in the root of our project not django
COBERTURA_DIR = join(dirname(DJANGO_ROOT), 'target', 'site', 'cobertura')
UNIT_TESTS_DIR = join(dirname(DJANGO_ROOT), 'target', 'surefire-reports')
if not exists(COBERTURA_DIR):
    makedirs(COBERTURA_DIR)

if not exists(UNIT_TESTS_DIR):
    makedirs(UNIT_TESTS_DIR)

NOSE_ARGS = ['-s',
             '-v',
             '--cover-erase',
             '--cover-branches',
             '--with-cov',
             '--cover-package=books,commons,users',
             '--cover-xml',
             '--cover-xml-file={0}/coverage.xml'.format(COBERTURA_DIR),
             '--with-xunit',
             '--xunit-file={0}/TEST-nosetests.xml'.format(UNIT_TESTS_DIR)
             ]
