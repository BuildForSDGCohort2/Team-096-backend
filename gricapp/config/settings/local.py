# pylint: disable=wildcard-import,unused-wildcard-import
from .base import *  # NOQA

DEBUG = True
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),

}
