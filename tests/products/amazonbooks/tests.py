import vcr
from rest_framework.authtoken.models import Token
from rest_framework.test import APIRequestFactory
from rest_framework.test import APITestCase

from books_api.products.amazonbooks.api.views import AmazonBooksViewSet
from books_api.users.models import User


@vcr.use_cassette()
class AmazonBooksAPITest(APITestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create_user(
            username="user@foo.com", email="user@foo.com", password="top_secret"
        )
        self.token = Token.objects.create(user=self.user)
        self.token.save()

    def test_amazonbooks_api(self):
        with vcr.use_cassette(
            "data/products/amazonbooks/test-amazonbooks.json",
            serializer="json",
            record_mode="once",
            filter_query_parameters=["q"],
            match_on=("body",),
            decode_compressed_response=True,
        ):
            factory = APIRequestFactory()
            view = AmazonBooksViewSet.as_view({"get": "list"})
            request = factory.get(
                "/amazonbooks/?format=json&q=None",
                HTTP_AUTHORIZATION=f"Token {self.token}",
                format="json",
            )
            response = view(request)
            self.assertEqual(
                response.status_code, 200, "Response error: {}".format(response.data)
            )
