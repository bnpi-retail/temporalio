import ast
import requests
import json

from datetime import datetime, timedelta
from auth_odoo import AuthOdoo
from tools import update_activity_log_data


class PriceHistoryCompetitors(AuthOdoo):
    def __init__(self):
        super().__init__()
        self.chunk_size = 1000

    def _get_token_mpstats(self):
        headers = self.connect_to_odoo_api_with_auth()
        url = "http://0.0.0.0:8070/get_settings_credentials"
        response = requests.post(url, headers=headers)
        if response.status_code == 200:
            r = response.json()
            self.token_mpstats = r.get("MP_STATS_TOKEN")
            if not self.token_mpstats:
                return {"response": "MPStats токен не задан в ozon.settings"}
        else:
            return {"status_code": response.status_code, "response": response.text}

    def get_days(self) -> tuple:
        today_date = datetime.now()
        yesterday_date = today_date - timedelta(days=1)

        today_date_str = today_date.strftime("%Y-%m-%d")
        yesterday_date_str = yesterday_date.strftime("%Y-%m-%d")
        return today_date_str, yesterday_date_str

    def get_request_count_competitors(self, path: str) -> requests.Response:
        endpoint = f"{self.url}{path}"
        headers = self.connect_to_odoo_api_with_auth()

        response = requests.get(endpoint, headers=headers)

        if response.status_code != 200:
            return response
        return response.status_code

    def get_request_sku_competitors(self, path: str, range: int) -> requests.Response:
        endpoint = f"{self.url}{path}"
        headers = self.connect_to_odoo_api_with_auth()

        data = {"range": range}
        response = requests.post(endpoint, headers=headers, data=data)

        if response.status_code != 200:
            return response

        answer = response.json()
        product_competitors_list = answer["product_competitors"]
        return product_competitors_list

    def get_ad(self, ads: list) -> dict:
        return ads[-1]
        today, yesterday = self.get_days()

        for ad in ads:
            date = ad.get("data")
            if date != yesterday:
                continue
            return ad

    def get_request_create_history_price(
        self, path: str, history_prices: list, sku: int
    ):
        endpoint = f"{self.url}{path}"
        headers = self.connect_to_odoo_api_with_auth()
        print(history_prices)
        data = {"ads": str(history_prices), "sku": sku}
        print(data)
        response = requests.post(endpoint, headers=headers, data=data)

        return response

    def get_request_mpstats(self, sku: int) -> requests.Response:
        url = f"https://mpstats.io/api/oz/get/item/{sku}/sales"
        res = self._get_token_mpstats()
        if res:
            raise ValueError(f"{res['response']}")
        headers = {
            "X-Mpstats-TOKEN": self.token_mpstats,
            "Content-Type": "application/json",
        }

        today, yesterday = self.get_days()
        params = {
            "d1": today,
            "d2": yesterday,
        }

        # response = requests.get(url, headers=headers, params=params)
        response = requests.get(url, headers=headers)

        ### EXAMPLE
        # return [
        #     {
        #         "no_data": 0,
        #         "data": "2023-12-11",
        #         "balance": 253,
        #         "sales": 0,
        #         "rating": 4.88,
        #         "price": 8490,
        #         "final_price": 6990,
        #         "is_bestseller": 1,
        #         "comments": 96
        #     },
        #     {
        #         "no_data": 0,
        #         "data": "2020-08-13",
        #         "balance": 193,
        #         "sales": 20,
        #         "rating": 4.88,
        #         "price": 8490,
        #         "final_price": 6990,
        #         "is_bestseller": 1,
        #         "comments": 96
        #     },
        # ]

        if response.status_code == 200:
            # print(f"MP status: {response.status_code}")
            # raise ValueError(f"MP status: {response.status_code}")
            return response.json()

    def main(self):
        count_sku = self.get_request_count_competitors(
            path="/api/v1/price_history_competitors/count_records/"
        )
        # data = json.loads(res)
        # count_sku = data['total_records']
        # count_sku = 2
        print(count_sku)

        num_chunks = count_sku // self.chunk_size
        num_chunks = num_chunks + 1

        create_history_prices = {}

        for i in range(num_chunks):
            list_sku = self.get_request_sku_competitors(
                path="/api/v1/price_history_competitors/get_sku/",
                range=i * self.chunk_size,
            )
            # list_sku = ["207392166", "273856979"]
            print(list_sku)

            for sku in list_sku:
                ads = self.get_request_mpstats(sku)
                print(ads)
                if ads is None:
                    continue

                ad = self.get_ad(ads)

                if sku not in create_history_prices:
                    create_history_prices[sku] = []

                create_history_prices[sku].append(ad)

        with open("data.txt", "w") as file:
            file.write(str(create_history_prices))

        return "Success!"

    def activity_two(self, dict_ads: dict):
        log_data = {}
        sku_qty = 0
        for sku, ads in dict_ads.items():
            response = self.get_request_create_history_price(
                path="/api/v1/price_history_competitors/create_ads/",
                history_prices=ads,
                sku=sku,
            )
            update_activity_log_data(log_data, response.json())
            sku_qty += 1
        log_data['Количество товаров конкурентов по которым получены данные'] = sku_qty

        return log_data


def main():
    model = PriceHistoryCompetitors()
    model.main()


def activity_two():
    with open("data.txt", "r") as file:
        data_content = file.read()

    data_dict = ast.literal_eval(data_content)
    print(data_dict)

    model = PriceHistoryCompetitors()
    log_data = model.activity_two(data_dict)

    return log_data
