import json

import vcr
from rest_framework.authtoken.models import Token
from rest_framework.test import APIRequestFactory
from rest_framework.test import APITestCase

from books_api.products.googlebooks.api.views import GoogleBooksViewSet
from books_api.users.models import User


class GoogleBooksAPITest(APITestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create_user(
            username="user@foo.com", email="user@foo.com", password="top_secret"
        )
        self.token = Token.objects.create(user=self.user)
        self.token.save()

    @vcr.use_cassette(
        "books_api/products/googlebooks/test-googlebooksapi.yml",
        filter_query_parameters=["q"],
    )
    def test_googlebooks_api(self):
        factory = APIRequestFactory()
        view = GoogleBooksViewSet.as_view({"get": "list"})
        request = factory.get(
            "/googlebooks/?format=json&q=None",
            HTTP_AUTHORIZATION=f"Token {self.token}",
            format="json",
        )
        response = view(request)
        self.assertEqual(
            response.status_code, 200, "Response error: {}".format(response.data)
        )
