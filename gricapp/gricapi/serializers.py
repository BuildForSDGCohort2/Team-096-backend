""" Serializers """

from rest_framework import serializers
from .models import User, Profile, Produce, Category
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
    """
    Serializes data for produce and it is preferable/recommened
    to use CategoryProduceSerializer for creating new produce.
    """

    MEASUREMENT_OPTIONS = ('bags', 'tonnes', 'units')
    owner = serializers.SlugRelatedField(
        queryset=User.objects.all(),
        slug_field='email'
    )
    produce_category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='category_name'
    )
    measurement_unit = serializers.ChoiceField(choices=MEASUREMENT_OPTIONS)

    class Meta:
        model = Produce
        fields = (
            "id", "owner", "produce_name",
            "produce_category", "stock",
            "measurement_unit", "price_tag",
            "product_description",
            "image_url", "date_created"
        )
        read_only_fields = ("date_created",)

    def update(self, instance, validated_data):
        category = validated_data.pop('produce_category')
        date_modified = serializers.DateTimeField(
            default=serializers.CreateOnlyDefault(timezone.now)
        )
        produce = self.instance

        produce.produce_name = validated_data.get(
            'produce_name', produce.produce_name)
        produce.stock = validated_data.get('stock', produce.stock)
        produce.measurement_unit = validated_data.get(
            'measurement_unit', produce.measurement_unit)
        produce.price_tag = validated_data.get(
            "price_tag", produce.price_tag)
        produce.image_url = validated_data.get(
            "image_url", produce.image_url)
        produce.product_description = validated_data.get(
            "product_desciption",
            produce.product_description
        )
        produce.owner = validated_data.get("owner", produce.owner)
        produce.date_modified = date_modified
        new_category = Category.objects.get(category_name=category)
        produce.produce_category = new_category

        produce.save()

        return super().update(instance, validated_data)


class ProduceDetailSerializer(serializers.ModelSerializer):
    """
    Serializer uses SlugRelatedField to represent owner field
    The Serializer display as:
       {
           owner: <email>,
           produce_name: <name>,
           stock: <Int>,
           measurement_unit: <unit>,
           price_tag: <price>,
           product_description: <description of product>,
           image_url: <link to image address>
       }
    """
    MEASUREMENT_OPTIONS = ('bags', 'tonnes', 'units')

    owner = serializers.SlugRelatedField(
        queryset=User.objects.all(),
        slug_field='email'
    )
    measurement_unit = serializers.ChoiceField(choices=MEASUREMENT_OPTIONS)

    class Meta:
        model = Produce
        fields = (
            "id", "owner", "produce_name", "stock",
            "measurement_unit", "price_tag",
            "product_description",
            "image_url", "date_modified"
        )


class CategoryProduceSerializer(serializers.ModelSerializer):
    """
    Serializer uses nested relationship and serializes as
       {
           category_name:<category_name>
           products: [
               {
                id: <pk>,
                owner: <email>,
                produce_name: <name>,
                stock: <Int>,
                measurement_unit: <unit>,
                price_tag: <price>,
                product_description: <description of product>,
                image_url: <link to image address>,
                date_modified: <date>
               }
            ]
       }
    Update method disallowed.
    """
    products = ProduceDetailSerializer(many=True)

    class Meta:
        model = Category
        fields = ("category_name", "products")

    def create(self, validated_data):
        products_data = validated_data.pop('products')
        self.instance = Category.objects.create(**validated_data)
        for product_data in products_data:
            Produce.objects.create(
                produce_category=self.instance,
                **product_data)
        return self.instance
