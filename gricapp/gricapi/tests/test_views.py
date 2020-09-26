"""
Test the API Views
"""
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework.views import status

from gricapi.models import User, Profile
from config.utilities import conf_reader
from config.settings.base import ROOT_DIR

# Get the test account credentials from the .credentials file
credentials_file = str(ROOT_DIR.path('login.credentials'))
EMAIL = conf_reader.get_value(credentials_file, 'LOGIN_USER')
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
