import requests
import vcr


# Create your tests here.


@vcr.use_cassette("books_api/products/googlebooks/test-googlebooksapi.yml")
def test_googlebooks_api():
    response = requests.get("https://www.googleapis.com/books/v1/volumes?q=None")
    assert response.status_code == 200
