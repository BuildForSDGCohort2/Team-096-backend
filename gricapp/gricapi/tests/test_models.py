"""
Create test cases for GricApp
"""

from django.test import TestCase
from django.db import IntegrityError
from gricapi.models import (
    Produce, User, Profile, Category, Order, OrderItem
)
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from config.utilities import conf_reader
from config.settings.base import ROOT_DIR

# Get the test account credentials from the .credentials file
credentials_file = str(ROOT_DIR.path('login.credentials'))
EMAIL = conf_reader.get_value(credentials_file, 'LOGIN_USER')
EMAIL2 = conf_reader.get_value(credentials_file, 'LOGIN_USER2')
PASSWORD = conf_reader.get_value(credentials_file, 'LOGIN_PASSWORD')

# Create your tests here.


class ProduceTestCase(TestCase):
    """
    Create test case for the Produce model
    """

    def setUp(self):
        """ Define test client and other test variables"""
        try:
            self.group = Group.objects.get(name='anonymous')
        except Group.DoesNotExist:
            self.group = Group.objects.create(name='anonymous')
        self.user = User.objects.create(
            groups=self.group, email="herd@example.com")
        self.category = Category.objects.create(category_name="Fruits")
        self.produce = Produce.objects.create(
            produce_name="Orange",
            produce_category=self.category,
            owner=self.user
        )

    def test_model_can_create_new_produce(self):
        """ Test the Produce model can create new produce"""
        old_count = Produce.objects.count()
        Produce.objects.create(produce_name="Lake rice",
                               produce_category=self.category,
                               owner=self.user)
        new_count = Produce.objects.count()
        self.assertNotEqual(old_count, new_count)

    def test_model_return_produce_name_str(self):
        """ model '__str__' returns human readable strings 'produce_name' """
        produce = Produce.objects.create(
            produce_name="Lake rice 3",
            produce_category=self.category,
            owner=self.user)
        self.assertEqual(str(produce), "Lake rice 3")

    def test_produce_name_label(self):
        """ model has correct label """
        produce = Produce.objects.get(id=1)
        field_label = produce._meta.get_field('produce_name').verbose_name
        self.assertEqual(field_label, 'produce name')

    def test_produce_name_max_length(self):
        produce = Produce.objects.get(id=1)
        max_length = produce._meta.get_field('produce_name').max_length
        self.assertEqual(max_length, 150)

    def test_produce_category_not_null(self):
        produce = Produce.objects.get(id=1)
        produce_type = produce._meta.get_field('produce_category').null
        self.assertNotEqual(produce_type, True)

    def test_slug_is_unique(self):
        produce1 = Produce.objects.get(id=1)
        produce2 = Produce(
            produce_name="Orange",
            produce_category=self.category,
            owner=self.user
        )
        produce2.save()
        self.assertNotEqual(produce1.slug, produce2.slug)

    def test_get_absolute_url(self):
        produce = Produce.objects.get(id=1)
        # This will also fail if the urlconf is not defined.
        self.assertEqual(produce.get_absolute_url(),
                         '/api/v1/catalog/produce/1/')


class ProduceSaveTest(TestCase):

    def setUp(self):
        try:
            self.group = Group.objects.get(name='anonymous')
        except Group.DoesNotExist:
            self.group = Group.objects.create(name='anonymous')
        self.produce_name = "Berry"
        self.category = Category.objects.create(category_name="Fruits")
        self.owner = User.objects.create(
            groups=self.group, email=EMAIL, password=PASSWORD)
        self.id = 3

    def test_id_autoset(self):
        prod = Produce.objects.create(
            produce_name=self.produce_name,
            produce_category=self.category,
            owner=self.owner
        )
        self.assertEqual(prod.id, 1)
        self.assertNotEqual(prod.slug, "")

    def test_id_honoured_when_supplied(self):
        prod = Produce.objects.create(
            id=self.id,
            produce_name=self.produce_name,
            produce_category=self.category,
            owner=self.owner
        )
        self.assertEqual(prod.id, self.id)

    def test_id_resets(self):
        prod = Produce.objects.create(
            produce_name=self.produce_name,
            produce_category=self.category,
            owner=self.owner
        )
        prod.id = None
        self.assertRaises(IntegrityError, prod.save())

    def test_slug_is_set_auto(self):
        prod = Produce.objects.create(
            produce_name=self.produce_name,
            slug="berry-000",
            produce_category=self.category,
            owner=self.owner
        )
        self.assertNotEqual(prod.slug, "berry-000")

    def test_slug_is_not_empty_when_id_is_supplied(self):
        prod = Produce.objects.create(
            id=self.id,
            produce_name=self.produce_name,
            produce_category=self.category,
            owner=self.owner
        )
        self.assertEqual(prod.id, self.id)
        self.assertNotEqual(prod.slug, "")


class UserModelTestCase(TestCase):
    """ This class defines the test suite for User model """

    def setUp(self):
        try:
            self.group = Group.objects.get(name='anonymous')
        except Group.DoesNotExist:
            self.group = Group.objects.create(name='anonymous')
        self.User = get_user_model()

    def test_create_user(self):
        user = self.User.objects.create_user(
            groups=self.group, email=EMAIL, password=PASSWORD)
        self.assertEqual(user.email, 'hallo@test.com')
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertIsNone(user.username)
        with self.assertRaises(TypeError):
            self.User.objects.create_user()
        with self.assertRaises(TypeError):
            self.User.objects.create_user(email='')
        with self.assertRaises(ValueError):
            self.User.objects.create_user(email='', password=PASSWORD)

    def test_create_superuser(self):
        try:
            group = Group.objects.get(name='admin')
        except Group.DoesNotExist:
            group = Group.objects.create(name='admin')
        admin_user = self.User.objects.create_superuser(
            EMAIL, PASSWORD, groups=group)
        self.assertEqual(admin_user.email, 'hallo@test.com')
        self.assertTrue(admin_user.is_active)
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)
        self.assertIsNone(admin_user.username)
        with self.assertRaises(ValueError):
            User.objects.create_superuser(
                email=EMAIL, password=PASSWORD, is_superuser=False)

    def test_user_string_returns_first_name_when_not_empty(self):
        """ Test user __str__ returns the first name of user """
        user = self.User.objects.create_user(
            groups=self.group, email=EMAIL, password=PASSWORD)
        self.assertEqual(str(user), "hallo@test.com")
        user2 = self.User.objects.create_user(
            groups=self.group,
            email=EMAIL2,
            password=PASSWORD, first_name="Victory"
        )
        self.assertNotEqual(str(user2), "Victoryhallo2@test.com")
        self.assertEqual(str(user2), "Victory")

    def test_has_valid_profile_string(self):
        """ Test user has profile string """
        user = self.User.objects.create_user(
            groups=self.group, email=EMAIL, password=PASSWORD)
        profile = Profile.objects.create(user=user)
        self.assertEqual(str(profile), "hallo@test.com")
        profile.is_farmer = True
        profile.save()
        self.assertNotEqual(str(profile), "hallo@test.com")
        self.assertEqual(str(profile), "hallo@test.com is a farmer")

        user2 = self.User.objects.create_user(
            groups=self.group,
            email=EMAIL2, password=PASSWORD,
            first_name="victory"
        )
        profile2 = Profile.objects.create(user=user2)
        self.assertEqual(str(profile2), "Victory")
        self.assertNotEqual(str(profile2), "hallo2@test.com")
        profile2.is_farmer = True
        profile2.save()
        self.assertNotEqual(str(profile2), "hallo2@test.com")
        self.assertEqual(str(profile2), "Victory is a farmer")


class CategoryTest(TestCase):

    def test_category_return_strings(self):
        category = Category.objects.create(category_name="Vegetables")
        self.assertEqual(str(category), "Vegetables")

    def test_category_slug_autoset(self):
        category = Category.objects.create(category_name="Fruits")
        self.assertIsNotNone(category.slug)
        category.slug = "fruityso--009"
        category.save()
        self.assertNotEqual(category.slug, "fruityso--009")

    def test_category_slug_resets(self):
        category = Category.objects.create(
            category_name="Minerals", slug="miney-00")
        self.assertNotEqual(category.slug, "miney-00")


class OrderTest(TestCase):

    def setUp(self):
        try:
            self.group = Group.objects.get(name='anonymous')
        except Group.DoesNotExist:
            self.group = Group.objects.create(name='anonymous')
        self.user = User.objects.create_user(
            groups=self.group, email=EMAIL2, password=PASSWORD)
        self.order = Order.objects.create(consumer=self.user)
        self.category = Category.objects.create(category_name="Fruits")
        self.produce = Produce.objects.create(
            produce_name="Orange-K",
            produce_category=self.category,
            owner=self.user
        )

    def test_order_return_string(self):
        order = Order.objects.create(consumer=self.user)
        self.assertEqual(str(order), str(order.id))

    def test_order_total_price(self):
        order_item = OrderItem.objects.create(
            order=self.order,
            produce=self.produce,
            quantity_ordered=15,
        )
        self.assertEqual(order_item.price, 15*self.produce.price_tag)
        self.assertIsNotNone(self.order.total_cost)


class OrderItemTest(TestCase):

    def setUp(self):
        try:
            self.group = Group.objects.get(name='anonymous')
        except Group.DoesNotExist:
            self.group = Group.objects.create(name='anonymous')
        self.user = User.objects.create_user(groups=self.group,
                                             email=EMAIL2, password=PASSWORD)
        self.order = Order.objects.create(consumer=self.user)
        self.category = Category.objects.create(category_name="Fruits")
        self.produce = Produce.objects.create(
            produce_name="Blueberry",
            produce_category=self.category,
            owner=self.user
        )

    def test_create_new_order(self):
        old_order_count = Order.objects.count()
        item_count = OrderItem.objects.count()
        order = Order.objects.create(consumer=self.user)
        OrderItem.objects.create(order=order,
                                 produce=self.produce, quantity_ordered=3)
        self.assertNotEqual(Order.objects.count(), old_order_count)
        self.assertNotEqual(OrderItem.objects.count(), item_count)

    def test_item_id_return_string(self):
        item = OrderItem.objects.create(
            order=self.order,
            produce=self.produce,
            quantity_ordered=10
        )
        self.assertEqual(str(item), "Item" + str(item.item_id))

    def test_item_id_is_unique(self):
        item = OrderItem.objects.create(
            order=self.order,
            produce=self.produce,
            quantity_ordered=10
        )
        item2 = OrderItem.objects.create(
            order=self.order,
            produce=self.produce,
            quantity_ordered=10
        )
        item2.item_id = item.item_id
        self.assertRaises(IntegrityError, item2.save())
