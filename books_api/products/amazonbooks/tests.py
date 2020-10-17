import requests
import vcr
from django.conf import settings


@vcr.use_cassette("books_api/products/amazonbooks/test-amazonbooksapi.yml")
def test_amazonbooks_api():
    url = f"{settings.AMAZON_BOOKS_API}/s"
    response = requests.get(f"{url}", headers=settings.HEADERS_MAC,)
    assert response.status_code == 200
