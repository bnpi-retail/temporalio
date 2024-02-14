import datetime
import json
import traceback

import requests

from os import getenv
from dotenv import load_dotenv
from datetime import timedelta
from time import sleep

from auth_odoo import AuthOdoo

load_dotenv()


class OzonAnalysisData(AuthOdoo):
    def __init__(self) -> None:
        super().__init__()
        self.headers_ozon = {
            "Client-Id": getenv("OZON_CLIENT_ID"),
            "Api-Key": getenv("OZON_API_KEY"),
        }
        self.chunk_size = 500
        self.offset = 0
        self.skus = set()

    @staticmethod
    def get_days() -> datetime.date:
        yesterday = datetime.date.today() - timedelta(days=1)
        return yesterday

    def requests_ozon(self, date) -> dict:
        result = requests.post(
            "https://api-seller.ozon.ru/v1/analytics/data",
            headers=self.headers_ozon,
            data=json.dumps({
                "date_from": date.isoformat(),
                "date_to": date.isoformat(),
                "metrics": [
                    "hits_view",
                    "hits_tocart",
                ],
                "dimension": [
                    "sku",
                ],
                "limit": 1000,
                "offset": self.offset
            }),
        ).json()["result"]["data"]
        self.offset += 1000
        return result

    def treatment(self, data: list) -> dict:
        products = {}

        for product in data:
            sku = product['dimensions'][0]['id']
            hits_view = product['metrics'][0]
            hits_tocart = product['metrics'][1]

            if sku not in self.skus:
                self.skus.add(sku)
            else:
                continue

            products[sku] = {
                'hits_view': hits_view,
                'hits_tocart': hits_tocart
            }

        return products

    def send_to_odoo(self, data: dict, date) -> None:
        path = "api/v1/save-analysys-data-lots"
        endpoint = f"{self.url}{path}"
        headers = self.connect_to_odoo_api_with_auth()
        data = {'data': str(data), 'date': date}
        response = requests.post(endpoint, headers=headers, data=data)

        if response.status_code != 200:
            raise requests.exceptions.RequestException()

    def main(self) -> None:
        yesterday = self.get_days()
        period = []
        for i in range(1, 15):
            day = datetime.date.today() - timedelta(days=i)
            period.append(day)

        for day in period:
            while True:
                try:
                    data = self.requests_ozon(day)
                except KeyError as e:
                    print(f'Error: status {self.offset}')
                    continue
                print(self.offset)

                data = self.treatment(data)
                self.send_to_odoo(data, day)

                if self.offset == 4000 or len(data) != 1000:
                    self.offset = 0
                    break

                sleep(30)

