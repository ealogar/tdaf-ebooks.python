# development settings
from common import *

# ######### DATABASE CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'ebukxoppython',
        'USER': 'root',
        'PASSWORD': 'sysadmin',
        'HOST': 'localhost',
        'PORT': '3307',
    }
}
# Override loggers to define level
LOGGING['loggers'] = {
        '': {
            'handlers': ['file'],
            'propagate': True,
            'level': 'INFO',
        },
        'django': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': True,
            }
    }
