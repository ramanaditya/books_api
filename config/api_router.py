from django.conf import settings
from rest_framework.routers import DefaultRouter, SimpleRouter

from books_api.products.amazonbooks.api.views import AmazonBooksViewSet
from books_api.products.googlebooks.api.views import GoogleBooksViewSet
from books_api.users.api.views import UserViewSet

if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()

router.register("users", UserViewSet)
router.register("googlebooks", GoogleBooksViewSet, "googlebooks")
router.register("amazonbooks", AmazonBooksViewSet, "amazonbooks")

app_name = "api"
urlpatterns = router.urls
