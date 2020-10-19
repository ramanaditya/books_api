import json
import os
import time

import vcr
from rest_framework.authtoken.models import Token
from rest_framework.test import APIRequestFactory
from rest_framework.test import APITestCase

from books_api.products.googlebooks.api.views import (
    GoogleBooksViewSet,
    getCustomizedList,
)
from books_api.users.models import User


def save_googlebooks_output(file_name):
    data = dict()
    result = list()
    with open(file_name, "r") as f:
        result = json.load(f)
    f.close()
    items = json.loads(result["interactions"][0]["response"]["body"]["string"])
    if items:
        data = getCustomizedList(items)

        dir_list = file_name.split("/")
        out_file_name = f'data/{"/".join(dir_list[1:])}'
        with open(out_file_name, "w") as outfile:
            json.dump(data, outfile, ensure_ascii=False, indent=4)
        outfile.close()


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
        self.query_string = "The Alchemist"
        self.file_name = (
            f"vcr_py/products/googlebooks/{''.join(self.query_string.split(' '))}.json"
        )

    def test_googlebooks_api(self):
        with vcr.use_cassette(
            f"{self.file_name}",
            serializer="json",
            record_mode="once",
            filter_query_parameters=["q"],
            match_on=("body",),
            decode_compressed_response=True,
            # before_record_response=save_googlebooks_output(file_name),
        ):
            request = self.factory.get(
                f"/googlebooks/?format=json&q={self.query_string}",
                HTTP_AUTHORIZATION=f"Token {self.token}",
                format="json",
            )
            response = self.view(request)
            self.assertEqual(
                response.status_code, 200, "Response error: {}".format(response.data),
            )

        max_check = 10
        for i in range(max_check):
            try:
                with open(self.file_name, "rb") as _:
                    break
            except IOError:
                time.sleep(3)
        save_googlebooks_output(self.file_name)

    def test_vcr_and_viewsets_googlebooks(self):
        vcr_output = list()
        dirs_list = self.file_name.split("/")
        data_file_name = f"data/{'/'.join(dirs_list[1:])}"
        with open(data_file_name, "r") as infile:
            vcr_output = json.load(infile)
        infile.close()
        request = self.factory.get(
            f"/googlebooks/?format=json&q={self.query_string}",
            HTTP_AUTHORIZATION=f"Token {self.token}",
            format="json",
        )
        response = self.view(request)
        response.render()
        assert response.data[:2] == vcr_output[:2]
