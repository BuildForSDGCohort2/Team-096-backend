""" Test for the serializers  """

from django.test import TestCase
from django.contrib.auth import get_user_model
from gricapi.models import Produce, Category, User
from gricapi.serializers import (
    UserSerializer, ProfileSerializer, ProduceSerializer
)
from config.utilities import conf_reader
from config.settings.base import ROOT_DIR

# Get the test account credentials from the .credentials file
credentials_file = str(ROOT_DIR.path('login.credentials'))
EMAIL2 = conf_reader.get_value(credentials_file, 'LOGIN_USER2')
PASSWORD = conf_reader.get_value(credentials_file, 'LOGIN_PASSWORD')


class UserSerializerTestCase(TestCase):

    def setUp(self):
        self.user_attributes = {
            "id": 1,
            "email": EMAIL2,
            "password": PASSWORD,
            "first_name": "Victory",
            "last_name": "Surety"
        }
        User = get_user_model()
        self.user = User.objects.create_user(**self.user_attributes)
        self.serializer = UserSerializer(instance=self.user)

    def test_user_serializer_contains_expected_fields(self):
        data = self.serializer.data

        self.assertEqual(data["id"], self.user_attributes["id"])
        self.assertCountEqual(data.keys(), [
                              "id", "email", "first_name", "last_name",
                              "profile", "date_joined"])

    def test_profile_serializer_contains_exact_content(self):
        profile_attributes = {
            "gender":  "F",
            "phone_number": +23456
        }
        serializer = ProfileSerializer(instance=profile_attributes)
        # nested user
        self.assertEqual(
            serializer.data["gender"], profile_attributes['gender'])
        self.user_attributes.update({"profile": profile_attributes})
        detail_serializer = UserSerializer(instance=self.user_attributes)
        self.assertEqual(
            detail_serializer.data["profile"]["gender"], "F")


class CategorySerializerTestCase(TestCase):
    """ Testing the Category Serializer """

    def setUp(self):
        self.category = Category(name="Fruits")
        self.category.save()
        self.user = User.objects.create_user(
            email=EMAIL2, password=PASSWORD
        )

    def test_produce_contains_exact_content(self):
        produce_attributes = {
            "produce_name": "orange R",
            "produce_category": self.category,
            "stock": 30,
            "owner": self.user
        }
        produce = Produce.objects.create(**produce_attributes)
        serializer = ProduceSerializer(instance=produce)
        self.assertEqual(serializer.data["owner"]
                         ["email"], EMAIL2)
