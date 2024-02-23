import datetime
import json
import requests

from os import getenv
from dotenv import load_dotenv
from datetime import timedelta
from time import sleep
from collections import defaultdict

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
        self.counter = defaultdict(int)

    @staticmethod
    def get_days() -> tuple:
        date_from = date_to = datetime.date.today() - timedelta(days=1)
        return date_from, date_to

    def requests_ozon(self, date_from, date_to) -> dict:
        result = requests.post(
            "https://api-seller.ozon.ru/v1/analytics/data",
            headers=self.headers_ozon,
            data=json.dumps({
                "date_from": date_from.isoformat(),
                "date_to": date_to.isoformat(),
                "metrics": [
                    "hits_view",
                    "hits_tocart",
                ],
                "dimension": [
                    "sku",
                    "day",
                ],
                "limit": 1000,
                "offset": self.offset
            }),
        ).json()["result"]["data"]
        self.offset += 1000
        return result

    def treatment(self, data: dict) -> dict:
        products = {}

        for product in data:
            sku = product['dimensions'][0]['id']
            date = product['dimensions'][1]['id']
            hits_view = product['metrics'][0]
            hits_tocart = product['metrics'][1]

            self.counter[date] += 1

            products[(sku, date)] = {
                'hits_view': hits_view,
                'hits_tocart': hits_tocart,
            }

        return products

    def send_to_odoo(self, data: dict) -> None:
        path = "api/v1/save-analysys-data-lots"
        endpoint = f"{self.url}{path}"
        headers = self.connect_to_odoo_api_with_auth()
        data = {'data': str(data)}
        response = requests.post(endpoint, headers=headers, data=data)

        if response.status_code != 200:
            raise requests.exceptions.RequestException()

    def main(self):
        date_from, date_to = self.get_days()
        while True:
            try:
                data = self.requests_ozon(date_from, date_to)
            except KeyError as e:
                print(f'Error: status {self.offset}')
                continue
            print(self.offset)

            data = self.treatment(data)
            self.send_to_odoo(data)

            if len(data) != 1000:
                break

        records_qty = sum(self.counter.values())
        res_list = [f"{len(self.counter)} из {(date_to - date_from).days + 1} дней импортировано. "
                    f"Всего {records_qty} записей\n", ]
        for date, qty in self.counter.items():
            res_list.append(f"{date}: {qty} записей\n")
        res = ''.join(res_list)
        log_data = {
            "Начало периода": date_from.strftime("%d.%m.%Y"),
            "Конец периода": date_to.strftime("%d.%m.%Y"),
            "Результат": res
        }
        return log_data
