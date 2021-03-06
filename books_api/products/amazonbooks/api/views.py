import requests
from bs4 import BeautifulSoup
from django.conf import settings
from rest_framework import viewsets
from rest_framework.response import Response


class ProductDetails:
    def __init__(self, query_string=None):
        self.headers = settings.HEADERS_MAC
        self.proxies = settings.PROXIES_MAC
        self.query_string = query_string
        self.products_list = list()

    def fetch_data(self, url, page_no=None):
        response = requests.get(
            f"{url}{'&page='+str(page_no) if page_no else ''}", headers=self.headers,
        )
        content = response.content
        soup = BeautifulSoup(content, features="lxml")
        return soup

    def get_data_list(self, soup):
        all_products = list()
        container = soup.findAll(
            "div",
            attrs={
                "class": "sg-col-4-of-12 sg-col-8-of-16 sg-col-16-of-24 sg-col-12-of-20 sg-col-24-of-32 sg-col sg-col-28-of-36 sg-col-20-of-28"
            },
        )
        for detail in container:
            title = detail.find(
                "span", attrs={"class": "a-size-medium a-color-base a-text-normal"}
            )
            url = detail.find(
                "a", attrs={"class": "a-link-normal a-text-normal", "href": True}
            )["href"]

            prod_detail = dict()
            prod_detail["title"] = title.text if title else "unknown-product"
            prod_detail["url"] = url.split("?")[0] if url else None

            all_products.append(prod_detail)
        return all_products

    def get_isbn(self, soup):
        data = list()
        try:
            temp = dict()
            temp["type"] = "ISBN_10"
            temp["identifier"] = (
                (
                    soup.select_one(
                        'span.a-text-bold:contains("ISBN-10"), b:contains("ISBN-10")'
                    )
                    .find_parent()
                    .text
                )
                .split(":")[-1]
                .strip()
            )
            data.append(temp)
        except:
            pass

        try:
            temp = dict()
            temp["type"] = "ISBN_13"
            temp["identifier"] = (
                (
                    soup.select_one(
                        'span.a-text-bold:contains("ISBN-13"), b:contains("ISBN-13")'
                    )
                    .find_parent()
                    .text
                )
                .split(":")[-1]
                .strip()
            )
            data.append(temp)
        except:
            pass
        return data


class AmazonBooksViewSet(viewsets.ViewSet):
    def list(self, request, *args, **kwargs):
        """
        :param request:
        :param args:
        :param kwargs:Ø
        :return:
        """
        query_string = request.query_params.get("q", default="")
        no_pages = int(request.query_params.get("pages", default=1))
        size = int(request.query_params.get("count", default=5))
        url = f"{settings.AMAZON_BOOKS_API}/s?k={query_string}"  # f"{settings.AMAZON_BOOKS_API}?k={query_string}&i=stripbooks-intl-ship&ref=nb_sb_noss_2"
        result = list()
        product_details = ProductDetails(query_string=query_string)
        for page in range(no_pages):
            soup = product_details.fetch_data(url, page)
            result.extend(product_details.get_data_list(soup))
            if len(result) > size:
                result = result[:size]
                break
        identifiers = []
        for ind in range(min(len(result), size)):
            if result[ind]["url"]:
                soup = product_details.fetch_data(
                    f"{settings.AMAZON_BOOKS_API}{result[ind]['url']}"
                )
                identifiers = product_details.get_isbn(soup)
            for identifier in identifiers:
                result[ind][identifier["type"]] = identifier["identifier"]
        return Response(result)
