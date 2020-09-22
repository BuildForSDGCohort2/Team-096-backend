""" Serializers """

from rest_framework import serializers
from . import models


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.User
        fields = ("id", "email", "is_farmer", "is_investor")


class ProfileSerializer(serializers.ModelSerializer):
    GENDER = (
        (None, 'Select gender'),
        ('M', 'Male'),
        ('F', 'Female')
    )

    user = UserSerializer()

    class Meta:
        model = models.Profile
        fields = ("id", "user", "gender", "address", "phone_number")


class ProduceSerializer(serializers.ModelSerializer):
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
        ('Tonnes', 'tonnes')
    )
    owner = UserSerializer(read_only=True)

    class Meta:
        model = models.Produce
        fields = (
            "id", "owner", "produce_name",
            "produce_type", "quantity", "measurement_unit", "date_created"
        )
        read_only_fields = ("date_created", "owner")
