# pylint: disable=wildcard-import,unused-wildcard-import
from .base import *  # NOQA

DEBUG = False
REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
}
STATICFILES_STORAGE = 'whitenoise.django.GzipManifestStaticFilesStorage'
