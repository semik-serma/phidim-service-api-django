from datetime import timedelta

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken


class CurrentUserTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(
            email='srv.2019.study@gmail.com',
            first_name='SRV', last_name='2019', role='c',
        )
        cls.other_user = get_user_model().objects.create_user(
            email='other@example.com', first_name='Other', last_name='User',
        )

    def setUp(self):
        self.url = reverse('current-user')

    def authenticate(self, token):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    def test_returns_token_user_and_role(self):
        self.assertEqual(self.url, '/api/auth/user/')
        for role in ('c', 't', 'a'):
            with self.subTest(role=role):
                self.user.role = role
                self.user.save(update_fields=['role'])
                token = AccessToken.for_user(self.user)
                self.authenticate(token)
                response = self.client.get(self.url, {'user_id': self.other_user.pk})
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                self.assertEqual(str(response.data['pk']), str(token['user_id']))
                self.assertEqual(response.data['email'], self.user.email)
                self.assertEqual(response.data['first_name'], self.user.first_name)
                self.assertEqual(response.data['last_name'], self.user.last_name)
                self.assertEqual(response.data['role'], role)

    def test_missing_token_returns_401(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_invalid_token_returns_401(self):
        self.authenticate('invalid-token')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_expired_token_returns_401(self):
        token = AccessToken.for_user(self.user)
        token.set_exp(lifetime=timedelta(seconds=-1))
        self.authenticate(token)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_refresh_token_returns_401(self):
        self.authenticate(RefreshToken.for_user(self.user))
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_deleted_user_returns_401(self):
        token = AccessToken.for_user(self.other_user)
        self.other_user.delete()
        self.authenticate(token)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_inactive_user_returns_401(self):
        token = AccessToken.for_user(self.user)
        self.user.is_active = False
        self.user.save(update_fields=['is_active'])
        self.authenticate(token)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_endpoint_does_not_create_or_update_users(self):
        self.authenticate(AccessToken.for_user(self.user))
        count = get_user_model().objects.count()
        for method in ('post', 'put', 'patch', 'delete'):
            with self.subTest(method=method):
                response = getattr(self.client, method)(self.url, {'role': 'a'})
                self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(get_user_model().objects.count(), count)
        self.user.refresh_from_db()
        self.assertEqual(self.user.role, 'c')
