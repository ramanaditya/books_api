import json
import time

import vcr
from django.conf import settings
from rest_framework.authtoken.models import Token
from rest_framework.test import APIRequestFactory
from rest_framework.test import APITestCase

from books_api.products.amazonbooks.api.views import AmazonBooksViewSet
from books_api.users.models import User
from tests.products.googlebooks.tests import write_data_to_json


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
            f"vcr_py/products/amazonbooks/{''.join(self.query_string.split(' '))}.yaml"
        )

    def test_amazonbooks_api(self):
        with vcr.use_cassette(
            f"{self.file_name}",
            serializer="yaml",
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
            response.render()
            vcr_output = response.data
            if settings.VCR_WRITE_MODE:
                max_check = 10
                for i in range(max_check):
                    try:
                        with open(self.file_name, "rb") as _:
                            break
                    except IOError:
                        time.sleep(3)
                write_data_to_json(self.file_name, response.data)
                self.assertEqual(
                    response.status_code, 200, "Response error: {}".format(response)
                )
            else:
                saved_data = list()
                dirs_list = self.file_name.split("/")
                data_file_name = f"data/{'/'.join(dirs_list[1:-1])}/{dirs_list[-1].replace('yaml','json')}"
                with open(data_file_name, "r") as infile:
                    saved_data = json.load(infile)
                infile.close()
                assert vcr_output == saved_data
