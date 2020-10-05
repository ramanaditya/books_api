import json

import requests
from django.conf import settings
from rest_framework import viewsets
from rest_framework.response import Response


class GoogleBooksViewSet(viewsets.ViewSet):
    def list(self, request, *args, **kwargs):
        """
        For query params, q=<Any title/isbn/author/ etc>
            for isbn, q=isbn:<isbn number>
        :param request:
        :param args:
        :param kwargs:Ø
        :return:
        """
        query_string = request.query_params.get("q", default="")
        url = f"{settings.GOOGLE_BOOKS_API}?q={query_string}"
        response = requests.get(url)
        ret = list()
        if response.status_code == 200:
            output = json.loads(response.text)
            items = output.get("items", None)
            if items:
                for item in items:
                    data = dict()
                    vol_info = item.get("volumeInfo", None)
                    if vol_info:
                        # title contains the title of the book
                        # identifiers contains the isbn details
                        data["title"] = vol_info.get("title", None)
                        data["identifiers"] = vol_info.get("industryIdentifiers", None)
                    ret.append(data)
        return Response(ret)
