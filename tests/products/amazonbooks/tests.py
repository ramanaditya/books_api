import json
import time

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
    size = 5
    with open(file_name, "r") as f:
        data = json.load(f)
    if data.get("interactions", None):
        if len(data["interactions"]) >= 1:
            html = (
                data["interactions"][0]["response"]["body"]["string"]
                .replace("\\n", "")
                .replace('"', "'")
            )
            soup = BeautifulSoup(html, features="lxml")
            result.extend(product_details.get_data_list(soup))
            if len(result) > size:
                result = result[:size]
        for ind in range(1, len(data["interactions"])):
            html = (
                data["interactions"][ind]["response"]["body"]["string"]
                .replace("\\n", "")
                .replace('"', "'")
            )
            soup = BeautifulSoup(html, features="lxml")
            identifiers = product_details.get_isbn(soup)
            for identifier in identifiers:
                result[ind - 1][identifier["type"]] = identifier["identifier"]
    dir_list = file_name.split("/")
    out_file_name = f'data/{"/".join(dir_list[1:])}'
    with open(out_file_name, "w") as outfile:
        json.dump(result, outfile, ensure_ascii=False, indent=4)


class AmazonBooksAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="user@foo.com", email="user@foo.com", password="top_secret"
        )
        self.token = Token.objects.create(user=self.user)
        self.token.save()
        self.factory = APIRequestFactory()
        self.view = AmazonBooksViewSet.as_view({"get": "list"})
        self.query_string = "The Alchemist"
        self.file_name = (
            f"vcr_py/products/amazonbooks/{''.join(self.query_string.split(' '))}.json"
        )

    def test_amazonbooks_api(self):
        with vcr.use_cassette(
            f"{self.file_name}",
            serializer="json",
            record_mode="once",
            filter_query_parameters=["q"],
            match_on=("body",),
            decode_compressed_response=True,
        ):

            request = self.factory.get(
                f"/amazonbooks/?format=json&q={self.query_string}",
                HTTP_AUTHORIZATION=f"Token {self.token}",
                format="json",
            )
            response = self.view(request)
            self.assertEqual(
                response.status_code, 200, "Response error: {}".format(response)
            )
        max_check = 10
        for i in range(max_check):
            try:
                with open(self.file_name, "rb") as _:
                    break
            except IOError:
                time.sleep(3)
        save_json_data(self.file_name)

    def test_vcr_and_viewsets_amazonbooks(self):
        vcr_output = list()
        dirs_list = self.file_name.split("/")
        data_file_name = f"data/{'/'.join(dirs_list[1:])}"
        with open(data_file_name, "r") as infile:
            vcr_output = json.load(infile)
        infile.close()
        request = self.factory.get(
            f"/amazonbooks/?format=json&q={self.query_string}",
            HTTP_AUTHORIZATION=f"Token {self.token}",
            format="json",
        )
        response = self.view(request)
        response.render()
        assert response.data == vcr_output
