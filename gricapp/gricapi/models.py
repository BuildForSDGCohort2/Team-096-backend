"""
Models for GricApp
"""
from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.utils.translation import ugettext_lazy as _
from django.urls import reverse
from .managers import CustomUserManager


class User(AbstractUser):
    username = None
    email = models.EmailField(_('email address'), unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    date_joined = models.DateTimeField(auto_now_add=True)

    objects = CustomUserManager()

    def __str__(self):
        if self.first_name != "":
            return "{}".format(self.first_name.capitalize())
        return "{}".format(self.email)


class Profile(models.Model):
    GENDER = (
        (None, 'Select gender'),
        ('M', 'Male'),
        ('F', 'Female')
    )
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    gender = models.CharField(max_length=6, choices=GENDER, null=True)
    address = models.CharField(max_length=60, blank=True, null=True)
    phone_number = models.BigIntegerField(blank=True, null=True)
    is_farmer = models.BooleanField(default=False)
    is_investor = models.BooleanField(default=False)

    def __str__(self):
        if self.is_farmer:
            return "{} is a farmer".format(self.user)
        return "{}".format(self.user)


class Produce(models.Model):
    """ Model for Produce """

    PRODUCT_TYPE_CHOICES = (
        (' ', "Select your produce type"),
        ('Fruits', 'Fruits'),
        ("Cereals (Grains)", "Cereals"),
        ('Oils', "Oils"),
        ("Eggs", "Eggs"),
        ("Meat", "Meat"),
        ("Fish", "Fish"),
        ("Raw materials (e.g rubber, cotton)", "Raw")
    )

    MEASUREMENT_UNITS = (
        ('Bags', 'bags'),
        ('Tonnes', 'tonnes'),
        ('Single units(Retail)', 'units')
    )

    produce_name = models.CharField(max_length=150, blank=False)
    produce_type = models.CharField(max_length=25, choices=PRODUCT_TYPE_CHOICES,
                                    default=' ', null=False)
    quantity = models.BigIntegerField(blank=True, default=0)
    measurement_unit = models.CharField(max_length=25, default="bags",
                                        choices=MEASUREMENT_UNITS)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    price_tag = models.FloatField(blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    def get_absolute_url(self):
        return reverse('api:produce-detail', args=[str(self.id)])

    def __str__(self):
        """Return a human readable representation of the model instance."""
        return "{}".format(self.produce_name)
