"""
Test the API Views
"""
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework.views import status

from gricapi.models import (
    User, Profile, Produce, Category
)
from config.utilities import conf_reader
from config.settings.base import ROOT_DIR

# Get the test account credentials from the .credentials file
credentials_file = str(ROOT_DIR.path('login.credentials'))
EMAIL = conf_reader.get_value(credentials_file, 'LOGIN_USER')
EMAIL2 = conf_reader.get_value(credentials_file, 'LOGIN_USER2')
PASSWORD = conf_reader.get_value(credentials_file, 'LOGIN_PASSWORD')


class UserListCreateAPIView(APITestCase):

    def setUp(self):
        self.url = reverse('api:user-list')

    def test_create_user(self):
        self.assertEqual(
            User.objects.count(),
            0
        )
        data = {
            "email": "hallo@test.com",
            "password": "foo123",
            "profile": {
                "is_farmer": "False",
                "is_investor": "False",
            }
        }
        response = self.client.post(self.url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        user = User.objects.first()
        self.assertEqual(user.email, data["email"])
        profile = Profile.objects.first()
        self.assertEqual(profile.user, user)

    def test_get_user_list(self):
        user = User(email=EMAIL, password=PASSWORD)
        user.save()
        response = self.client.get(self.url)
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response_json), 1)
        data = response_json[0]
        self.assertEqual(data["id"], 1)
        self.assertEqual(data["email"], "hallo@test.com")
        self.assertIsNone(data['profile'])


class UserDetailsAPIView(APITestCase):
    def setUp(self):
        self.user = User(email=EMAIL,
                         password=PASSWORD)
        self.user.save()
        self.profile = Profile.objects.create(user=self.user)
        self.url = reverse("api:user-detail", kwargs={'pk': self.user.id})

    def test_get_user_details(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()
        self.assertEqual(data['id'], self.user.id)
        self.assertEqual(data["email"], self.user.email)
        self.assertIsNotNone(data['date_joined'])
        self.assertNotEqual(data['profile'], None)

    def test_update_user(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()
        data["email"] = "hallo121@test.com"
        data["first_name"] = "loveth"
        response = self.client.put(self.url, data=data, format='json')
        # should return bad request for changing 'email', a write_once field
        self.assertEqual(response.status_code,
                         status.HTTP_400_BAD_REQUEST)
        # make a new request with correct data
        response2 = self.client.get(self.url)
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        data2 = response2.json()
        data2["last_name"] = "Grace"
        response = self.client.put(self.url, data2, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.user.refresh_from_db()
        self.assertEqual(self.user.last_name, data2["last_name"])

    def test_update_a_profile(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()
        data['profile']["is_farmer"] = "True"
        data['profile']['gender'] = "M"
        data['profile']['phone_number'] = +23480321
        response = self.client.put(self.url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.phone_number,
                         data['profile']['phone_number'])


class ProduceListCreateAPIView(APITestCase):
    def setUp(self):
        self.user = User(email=EMAIL,
                         password=PASSWORD)
        self.user.save()
        self.url = reverse("api:products-list")
        self.category = Category.objects.create(category_name="Vegetables")
        self.produce = Produce.objects.create(
            produce_category=self.category,
            produce_name="Lenscus",
            stock=50,
            price_tag=3500,
            measurement_unit="tonnes",
            owner=self.user

        )
        self.data = {
            "produce_name": "Letus",
            "produce_category": "Vegetables",
            "stock": 40,
            "measurement_unit": 'bags',
            "owner": EMAIL,
            "price_tag": 1500,
            "product_description": "This product is suitable for "
        }

    def test_get_produce_list(self):
        response = self.client.get(self.url)

        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response_json), 1)
        data = response_json[0]
        self.assertEqual(data["id"], 1)
        self.assertEqual(data["produce_name"], self.produce.produce_name)
        self.assertEqual(data["produce_category"], self.category.category_name)

    def test_create_a_new_produce(self):
        self.assertEqual(
            Produce.objects.count(),
            1
        )

        response = self.client.post(self.url, data=self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Produce.objects.count(), 2)
        produce = Produce.objects.get(id=2)
        self.assertEqual(response.data["owner"], self.data["owner"])
        self.assertEqual(
            response.data["produce_name"], self.data["produce_name"])
        self.assertEqual(produce.price_tag, self.data["price_tag"])

    def test_update_product(self):
        Category.objects.create(category_name="Fruits")
        url = reverse('api:products-detail', kwargs={"pk": 1})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()
        data["id"] = self.produce.id
        data["produce_name"] = "Blue-Orange"
        data['produce_category'] = "Fruits"
        data['stock'] = 212
        response = self.client.put(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.produce.refresh_from_db()
        self.assertEqual(self.produce.stock,
                         data['stock'])

        response2 = self.client.get(url)
        self.assertEqual(response2.status_code, status.HTTP_200_OK)

        data2 = response2.json()
        data2["produce_name"] = "Orange"
        data2['produce_category'] = None  # produce_category should not be None
        response2 = self.client.put(url, data2, format='json')
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_a_product_as_the_owner(self):
        url = reverse('api:products-detail', kwargs={"pk": 1})
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_a_product_as_staff(self):
        url = reverse('api:products-detail', kwargs={"pk": 1})
        user = User(email=EMAIL2, password=PASSWORD)
        user.is_staff = True
        user.save()
        user.refresh_from_db()
        self.client.force_authenticate(user=user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_a_product_failed(self):
        url = reverse('api:products-detail', kwargs={"pk": 1})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class CategoryListCreate(APITestCase):

    def setUp(self):

        self.owner = User.objects.create_user(email=EMAIL, password=PASSWORD)
        self.data = {"category_name": "Fruits"}
        self.url = reverse("api:produce-category-list")

    def test_category_list(self):
        category = Category.objects.create(category_name="Fruits")
        response = self.client.get(self.url)
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response_json), Category.objects.count())
        data = response_json[0]
        self.assertEqual(category.category_name, data["category_name"])

    def test_create_a_new_produce_and_category(self):
        self.assertEqual(
            Produce.objects.count(),
            0
        )
        self.assertEqual(
            Category.objects.count(),
            0
        )
        data = {
            "category_name": "Grains",
            "products": [
                {
                    "produce_name": "Beans",
                    "stock": 100,
                    "measurement_unit": 'bags',
                    "owner": EMAIL,
                    "price_tag": 7500,
                    "product_description": "This is a cereal product "
                }
            ]
        }
        response = self.client.post(self.url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            Produce.objects.count(),
            1
        )
        self.assertEqual(
            Category.objects.count(),
            1
        )


class CategoryProduceDetailsAPITest(APITestCase):
    """
    The products detail index can be accessed with position products[pk-1]
    """

    def setUp(self):
        self.owner = User.objects.create_user(email=EMAIL, password=PASSWORD)
        self.category = Category.objects.create(category_name="Fruits")
        self.produce = Produce.objects.create(
            produce_category=self.category, produce_name="Berry", stock=2,
            price_tag=20, owner=self.owner)
        self.produce1 = Produce.objects.create(
            produce_category=self.category, produce_name="Berry2345", stock=90,
            price_tag=200, owner=self.owner)
        self.url = reverse("api:produce-category-detail", kwargs={"pk": 1})

    def test_get_produce_details_for_each_category(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()
        self.assertEqual(data['products'][0]['id'], self.produce.id)
        self.assertEqual(data["products"][0]["owner"], self.owner.email)
        self.assertEqual(data["category_name"], self.category.category_name)
        self.assertIsNotNone(data["products"][0]['date_modified'])
        self.assertEqual(len(data['products']), 2)

    def test_update_product_failed(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()
        data['products'][0]["produce_name"] = "Blue-Orange"
        data['products'][0]['stock'] = 3
        response = self.client.put(self.url, data=data, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete_category_failed(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_a_product_as_admin(self):
        user = User(email=EMAIL2, password=PASSWORD)
        user.is_superuser = True
        user.save()
        user.refresh_from_db()
        self.client.force_authenticate(user=user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
