import json

import vcr
from rest_framework.authtoken.models import Token
from rest_framework.test import APIRequestFactory
from rest_framework.test import APITestCase

from books_api.products.googlebooks.api.views import (
    GoogleBooksViewSet,
    getCustomizedList,
)
from books_api.users.models import User


def reformat_response_body():
    def before_record_response(response):
        items = json.loads(response["body"]["string"])
        data = list()
        if items:
            data = getCustomizedList(items)
        response["body"]["output"] = data
        return response

    return before_record_response


class GoogleBooksAPITest(APITestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create_user(
            username="user@foo.com", email="user@foo.com", password="top_secret"
        )
        self.token = Token.objects.create(user=self.user)
        self.token.save()
        self.factory = APIRequestFactory()
        self.view = GoogleBooksViewSet.as_view({"get": "list"})

    def test_googlebooks_api(self):
        with vcr.use_cassette(
            "data/products/googlebooks/test-googlebooks.json",
            serializer="json",
            record_mode="once",
            filter_query_parameters=["q"],
            match_on=("body",),
            decode_compressed_response=True,
            before_record_response=reformat_response_body(),
        ):
            request = self.factory.get(
                "/googlebooks/?format=json&q=None",
                HTTP_AUTHORIZATION=f"Token {self.token}",
                format="json",
            )
            response = self.view(request)
            response.render()
            self.assertEqual(
                response.status_code, 200, "Response error: {}".format(response.data),
            )
