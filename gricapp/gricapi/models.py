"""
Models for GricApp
"""
from django.db import models


class Produce(models.Model):
    """ Model for Produce """
    produce_name = models.CharField(max_length=255, blank=False)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        """Return a human readable representation of the model instance."""
        return "{}".format(self.produce_name)
