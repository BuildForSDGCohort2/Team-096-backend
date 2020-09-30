""" Serializers """

from rest_framework import serializers
from .models import User, Profile, Produce
from django.utils import timezone


class ProfileSerializer(serializers.ModelSerializer):
    GENDER = (
        (None, 'Select gender'),
        ('M', 'Male'),
        ('F', 'Female')
    )

    class Meta:
        model = Profile
        fields = ("gender", "address", "phone_number",
                  "is_farmer", "is_investor")


class UserSerializer(serializers.ModelSerializer):

    date_joined = serializers.DateTimeField(
        default=serializers.CreateOnlyDefault(timezone.now)
    )
    profile = ProfileSerializer()

    class Meta:
        model = User
        fields = ("id", "email", "password", "first_name",
                  "last_name", "profile", "date_joined")
        extra_kwargs = {
            'password': {
                'write_only': True,
                'required': False
            }
        }

    def create(self, validated_data):
        profile_data = validated_data.pop('profile')
        self.instance = User.objects.create_user(**validated_data)
        Profile.objects.create(user=self.instance, **profile_data)
        return self.instance

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile')
        profile = instance.profile

        profile.gender = profile_data.get('gender', profile.gender)
        profile.address = profile_data.get('address', profile.address)
        profile.phone_number = profile_data.get(
            'phone_number', profile.phone_number)
        profile.is_farmer = profile_data.get("is_farmer", profile.is_farmer)
        profile.is_investor = profile_data.get(
            "is_investor", profile.is_investor)

        profile.save()

        email = instance.email

        if 'email' in validated_data:
            # check for changes in the email
            if validated_data.get('email') != email:
                raise serializers.ValidationError({
                    'email': 'You cannot change this field.',
                })

        return super().update(instance, validated_data)


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
        ('Tonnes', 'tonnes'),
        ('Single units (Retail)', 'units')
    )
    owner = UserSerializer(read_only=True)

    class Meta:
        model = Produce
        fields = (
            "id", "owner", "produce_name",
            "produce_category", "stock", "measurement_unit", "date_created"
        )
        read_only_fields = ("date_created", "owner")
