""" Test for the serializers  """

from django.test import TestCase
from django.contrib.auth import get_user_model
from gricapi.models import Produce, Category, User, Order, OrderItem
from gricapi.serializers import (
    UserSerializer, ProfileSerializer, ProduceSerializer,
    OrderCreateSerializer, ItemSerializer, ItemListSerializer
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


class ProduceSerializerTestCase(TestCase):
    """ Testing the Category Serializer """

    def setUp(self):
        self.category = Category(category_name="Fruits")
        self.category.save()
        self.user = User.objects.create_user(
            email=EMAIL2, password=PASSWORD
        )
        self.produce_attributes = {
            "produce_name": "orange R",
            "produce_category": self.category,
            "stock": 30,
            "measurement_unit": "bags",
            "owner": self.user,
            "price_tag": 12
        }
        self.produce = Produce.objects.create(**self.produce_attributes)

    def test_produce_contains_exact_content(self):
        serializer = ProduceSerializer(instance=self.produce)
        self.assertEqual(serializer.data["owner"], self.produce.owner.email)
        self.assertEqual(serializer.data['stock'], self.produce.stock)

    def test_measurement_units_must_be_in_choices(self):
        self.produce_attributes['measurement_unit'] = 'single'
        serializer = ProduceSerializer(
            instance=self.produce,
            data=self.produce_attributes
        )

        self.assertFalse(serializer.is_valid())
        self.assertEqual(set(serializer.errors.keys()),
                         set(['measurement_unit']))


class OrderSerializerTestCase(TestCase):

    def setUp(self):
        self.category = Category(category_name="Fruits")
        self.category.save()
        self.user = User.objects.create_user(
            email=EMAIL2, password=PASSWORD
        )
        self.produce = Produce.objects.create(
            produce_name="orange R",
            produce_category=self.category,
            stock=45,
            price_tag=1500,
            owner=self.user
        )
        self.order = Order.objects.create(consumer=self.user)
        self.order_item_attributes = {
            "produce": self.produce,
            "quantity_ordered": 30,
            "order": self.order,
        }
        self.serializer = OrderCreateSerializer(instance=self.order)

    def test_order_serializer_contains_exact_contents(self):
        data = self.serializer.data
        self.assertEqual(data["id"], str(self.order.id))
        self.assertCountEqual(data.keys(),
                              ['id', 'consumer', 'items'])

    def test_orderitem_serializer_contains_expected_contents(self):
        item = OrderItem.objects.create(**self.order_item_attributes)
        serializer = ItemSerializer(instance=item)
        data = serializer.data

        self.assertCountEqual(data.keys(),
                              ['item_id', "produce",
                               'quantity_ordered'])

        # price should be 2 decimal places
        data["price"] = 34.298
        serializer = ItemListSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(set(serializer.errors), set(['price']))

        # quantity ordered should be integer
        data["quantity_ordered"] = 2.5
        serializer = ItemSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(set(serializer.errors), set(
            ['quantity_ordered']))
