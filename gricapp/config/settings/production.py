# pylint: disable=wildcard-import,unused-wildcard-import
from .base import *  # NOQA

DEBUG = False
REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    )
}
STATICFILES_STORAGE = 'whitenoise.django.GzipManifestStaticFilesStorage'
