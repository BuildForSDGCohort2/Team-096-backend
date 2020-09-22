"""
Test the API Views
"""
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework.views import status

from gricapi.models import User


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
            "password": "foo123"
        }
        response = self.client.post(self.url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        user = User.objects.first()
        self.assertEqual(user.email, data["email"])
        self.assertNotEqual(user.is_investor, True)

    def test_get_user_list(self):
        user = User(email="hallow@test.com", password="foo")
        user.save()
        response = self.client.get(self.url)
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response_json), 1)
        data = response_json[0]
        self.assertEqual(data["id"], 1)
        self.assertEqual(data["email"], "hallow@test.com")


class UserDetailsAPIView(APITestCase):
    def setUp(self):
        self.user = User(email="hallow@test.com",
                         password="foo", is_farmer=True)
        self.user.save()
        self.url = reverse("api:user-detail", kwargs={'pk': self.user.id})

    def test_get_user_details(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()
        self.assertEqual(data['id'], self.user.id)
        self.assertEqual(data["email"], self.user.email)
        self.assertEqual(data["is_farmer"], self.user.is_farmer)

    def test_update_user(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()
        data["is_farmer"] = "False"
        data["is_investor"] = "True"
        response = self.client.put(self.url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.is_farmer, False)
        self.assertEqual(self.user.is_investor, True)
