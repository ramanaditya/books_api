import json

import vcr
from bs4 import BeautifulSoup
from django.urls import reverse
from rest_framework.authtoken.models import Token
from rest_framework.test import APIRequestFactory
from rest_framework.test import APITestCase

from books_api.products.amazonbooks.api.views import (
    AmazonBooksViewSet,
    ProductDetails,
)
from books_api.users.models import User


def save_json_data(file_name):
    data = dict()
    product_details = ProductDetails()
    result = list()
    with open(file_name, "r") as f:
        data = json.load(f)
    if data.get("interactions", None):
        if len(data["interactions"]) >= 1:
            html = data["interactions"][0]["response"]["body"]["string"]
            soup = BeautifulSoup(html, features="lxml")
            result.extend(product_details.get_data_list(soup))
        for ind in range(1, len(data["interactions"])):
            html = data["interactions"][ind]["response"]["body"]["string"]
            soup = BeautifulSoup(html, features="lxml")
            identifiers = product_details.get_isbn(soup)
            for identifier in identifiers:
                result[ind][identifier["type"]] = identifier["identifier"]
    data["output"] = result
    # dir_list = file_name.split("/")
    # out_file_name = f'{"/".join(dir_list[:-1])}/data-{dir_list[-1]}'
    with open(file_name, "w") as outfile:
        json.dump(data, outfile, ensure_ascii=False, indent=4)


class AmazonBooksAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="user@foo.com", email="user@foo.com", password="top_secret"
        )
        self.token = Token.objects.create(user=self.user)
        self.token.save()
        self.factory = APIRequestFactory()
        self.view = AmazonBooksViewSet.as_view({"get": "list"})

    def test_amazonbooks_api(self):
        q = "The Alchemist"
        with vcr.use_cassette(
            "data/products/amazonbooks/test-amazonbooks.json",
            serializer="json",
            record_mode="once",
            filter_query_parameters=["q", "headers"],
            match_on=("body",),
            decode_compressed_response=True,
            # before_record_response=reformat_response_body(q),
        ):

            request = self.factory.get(
                f"/amazonbooks/?format=json&q={q}",
                HTTP_AUTHORIZATION=f"Token {self.token}",
                format="json",
            )
            response = self.view(request).render()
            self.assertEqual(
                response.status_code, 200, "Response error: {}".format(response)
            )
        save_json_data("data/products/amazonbooks/test-amazonbooks.json")
