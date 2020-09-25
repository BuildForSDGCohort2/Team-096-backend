"""
Create test cases for GricApp
"""

from django.test import TestCase
from gricapi.models import Produce, User, Profile
from django.contrib.auth import get_user_model

# Create your tests here.


class ProduceTestCase(TestCase):
    """
    Create test case for the Produce model
    """

    def setUp(self):
        """ Define test client and other test variables"""
        self.user = User.objects.create(email="herd@example.com")
        self.produce = Produce.objects.create(produce_name="Orange", produce_type="Fruits",
                                              owner=self.user)

    def test_model_can_create_new_produce(self):
        """ Test the Produce model can create new produce"""
        old_count = Produce.objects.count()
        Produce.objects.create(produce_name="Lake rice", owner=self.user)
        new_count = Produce.objects.count()
        self.assertNotEqual(old_count, new_count)

    def test_model_return_produce_name_str(self):
        """ model '__str__' returns human readable strings 'produce_name' """
        produce = Produce.objects.create(
            produce_name="Lake rice 3", owner=self.user)
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

    def test_produce_type_not_null(self):
        produce = Produce.objects.get(id=1)
        produce_type = produce._meta.get_field('produce_type').null
        self.assertNotEqual(produce_type, True)

    def test_get_absolute_url(self):
        produce = Produce.objects.get(id=1)
        # This will also fail if the urlconf is not defined.
        self.assertEqual(produce.get_absolute_url(), '/api/catalog/produce/1/')


class UserModelTestCase(TestCase):
    """ This class defines the test suite for User model """

    def setUp(self):
        self.User = get_user_model()

    def test_create_user(self):
        User = get_user_model()
        user = User.objects.create_user(
            email='normal@test.com', password='foo')
        self.assertEqual(user.email, 'normal@test.com')
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertIsNone(user.username)
        with self.assertRaises(TypeError):
            User.objects.create_user()
        with self.assertRaises(TypeError):
            User.objects.create_user(email='')
        with self.assertRaises(ValueError):
            User.objects.create_user(email='', password="foo")

    def test_create_superuser(self):
        User = get_user_model()
        admin_user = User.objects.create_superuser('super@test.com', 'foo')
        self.assertEqual(admin_user.email, 'super@test.com')
        self.assertTrue(admin_user.is_active)
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)
        self.assertIsNone(admin_user.username)
        with self.assertRaises(ValueError):
            User.objects.create_superuser(
                email='super@user.com', password='foo', is_superuser=False)

    def test_user_string_returns_first_name_when_not_empty(self):
        """ Test user __str__ returns the first name of user """
        user = self.User.objects.create_user(
            email="hallo@test.com", password='foo')
        self.assertEqual(str(user), "hallo@test.com")
        user2 = self.User.objects.create_user(
            email="hallo2@test.com",
            password="foo", first_name="Victory"
        )
        self.assertNotEqual(str(user2), "Victoryhallo2@test.com")
        self.assertEqual(str(user2), "Victory")

    def test_has_valid_profile_string(self):
        """ Test user has profile string """
        user = self.User.objects.create_user(
            email="hallo@test.com", password='foo')
        profile = Profile.objects.create(user=user)
        self.assertEqual(str(profile), "hallo@test.com")
        profile.is_farmer = True
        profile.save()
        self.assertNotEqual(str(profile), "hallo@test.com")
        self.assertEqual(str(profile), "hallo@test.com is a farmer")

        user2 = self.User.objects.create_user(
            email="hallo2@test.com", password='foo', first_name="victory")
        profile2 = Profile.objects.create(user=user2)
        self.assertEqual(str(profile2), "Victory")
        self.assertNotEqual(str(profile2), "hallo2@test.com")
        profile2.is_farmer = True
        profile2.save()
        self.assertNotEqual(str(profile2), "hallo2@test.com")
        self.assertEqual(str(profile2), "Victory is a farmer")
