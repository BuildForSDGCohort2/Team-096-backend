"""
Create test cases for GricApp
"""

from django.test import TestCase
from gricapi.models import Produce

# Create your tests here.


class ProduceTestCase(TestCase):
    """
    Create test case for the Produce model
    """

    def setUp(self):
        """ Define test client and other test variables"""
        self.produce_name = "Garri ijebu"
        self.produce = Produce(produce_name=self.produce_name)

    def test_model_can_create_new_produce(self):
        """ Test the Produce model can create new produce"""
        old_count = Produce.objects.count()
        self.produce.save()
        new_count = Produce.objects.count()
        self.assertNotEqual(old_count, new_count)

    def test_model_produce(self):
        """ model '__str__' returns human readable strings 'produce_name' """
        self.produce.save()
        self.assertEqual(str(self.produce), self.produce_name)
