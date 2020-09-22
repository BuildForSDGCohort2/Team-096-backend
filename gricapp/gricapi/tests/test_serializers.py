""" Test for the serializers  """

from django.test import TestCase
from django.contrib.auth import get_user_model
from gricapi.models import Profile, Produce
from gricapi.serializers import UserSerializer, ProfileSerializer, ProduceSerializer


class UserSerializerTestCase(TestCase):

    def setUp(self):
        self.user_attributes = {
            "id": 1,
            "email": "hallo@example.com",
            "password": "asdf2",
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
                              "id", "email", "is_investor", "is_farmer"])

    def test_profile_serializer_contains_exact_content(self):
        profile_attributes = {
            "id": 1,
            "user": self.user,
            "gender":  "F",
            "phone_number": +23456
        }
        profile = Profile.objects.create(**profile_attributes)
        serializer = ProfileSerializer(instance=profile)
        # nested user
        self.assertEqual(serializer.data["user"]["email"], "hallo@example.com")
        self.assertNotEqual(serializer.data["user"]["is_farmer"], True)

    def test_produce_contains_exact_content(self):
        produce_attributes = {
            "produce_name": "orange R",
            "produce_type": "Fruits",
            "quantity": 30,
            "owner": self.user
        }
        produce = Produce.objects.create(**produce_attributes)
        serializer = ProduceSerializer(instance=produce)
        self.assertEqual(serializer.data["owner"]
                         ["email"], "hallo@example.com")
