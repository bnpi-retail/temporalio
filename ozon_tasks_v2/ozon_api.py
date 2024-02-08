import requests
import json

from dotenv import load_dotenv
from os import getenv


load_dotenv()


class InfoOzon:
    def __init__(self):
        self.ozon_headers = {
            "Client-Id": getenv("OZON_CLIENT_ID"),
            "Api-Key": getenv("OZON_API_KEY"),
        }

        self.all_commission = {
            "acquiring": "Максимальная комиссия за эквайринг",
            "fbo_fulfillment_amount": "Комиссия за сборку заказа (FBO)",
            "fbo_direct_flow_trans_min_amount": "Магистраль от (FBO)",
            "fbo_direct_flow_trans_max_amount": "Магистраль до (FBO)",
            "fbo_deliv_to_customer_amount": "Последняя миля (FBO)",
            "fbo_return_flow_amount": "Комиссия за возврат и отмену (FBO)",
            "fbo_return_flow_trans_min_amount": "Комиссия за обратную логистику от (FBO)",
            "fbo_return_flow_trans_max_amount": "Комиссия за обратную логистику до (FBO)",
            "fbs_first_mile_min_amount": "Минимальная комиссия за обработку отправления (FBS) — 0 рублей",
            "fbs_first_mile_max_amount": "Максимальная комиссия за обработку отправления (FBS) — 25 рублей",
            "fbs_direct_flow_trans_min_amount": "Магистраль от (FBS)",
            "fbs_direct_flow_trans_max_amount": "Магистраль до (FBS)",
            "fbs_deliv_to_customer_amount": "Последняя миля (FBS)",
            "fbs_return_flow_amount": "Комиссия за возврат и отмену, обработка отправления (FBS)",
            "fbs_return_flow_trans_min_amount": "Комиссия за возврат и отмену, магистраль от (FBS)",
            "fbs_return_flow_trans_max_amount": "Комиссия за возврат и отмену, магистраль до (FBS)",
            "sales_percent_fbo": "Процент комиссии за продажу (FBO)",
            "sales_percent_fbs": "Процент комиссии за продажу (FBS)",
            "sales_percent": "Наибольший процент комиссии за продажу среди FBO и FBS",
        }

    def get_product(self, limit=1000, last_id="") -> dict:
        result = requests.post(
            "https://api-seller.ozon.ru/v2/product/list",
            headers=self.ozon_headers,
            data=json.dumps(
                {
                    "filter": {},
                    "last_id": last_id,
                    "limit": limit,
                }
            ),
        ).json()["result"]

        return result["items"], result["last_id"]

    def get_product_attributes(self, product_ids: list, limit=1000) -> list:
        response = requests.post(
            "https://api-seller.ozon.ru/v3/products/info/attributes",
            headers=self.ozon_headers,
            data=json.dumps(
                {
                    "filter": {"product_id": [str(prod_id) for prod_id in product_ids]},
                    "limit": limit,
                }
            ),
        )
        return response.json()["result"]
    
    def get_product_trading_schemes(self, product_ids: list, limit=1000) -> dict:
        result = requests.post(
            "https://api-seller.ozon.ru/v3/product/info/stocks",
            headers=self.ozon_headers,
            data=json.dumps(
                {
                    "filter": {
                        "product_id": [str(prod_id) for prod_id in product_ids],
                    },
                    "limit": limit,
                }
            ),
        ).json()["result"]["items"]
        products_trading_schemes = {}
        for item in result:
            stocks = item["stocks"]
            trading_schemes = [
                stock["type"].upper()
                for stock in stocks
                if stock["present"] != 0 and stock["type"] in ["fbs", "fbo"]
            ]
            products_trading_schemes[item["product_id"]] = (
                ", ".join(trading_schemes) if trading_schemes else "undefined"
            )

        return products_trading_schemes
    
    def get_product_prices(self, product_ids: list, limit=1000):
        """Returns a dict {product_id: prices_info}"""
        result = self.get_price_objects(product_ids, limit)
        product_price_info = {}
        for item in result:
            product_price_info[item["product_id"]] = item
        return product_price_info
    
    def get_price_objects(self, product_ids: list, limit=1000):
        result = requests.post(
            "https://api-seller.ozon.ru/v4/product/info/prices",
            headers=self.ozon_headers,
            data=json.dumps(
                {
                    "filter": {
                        "product_id": [str(prod_id) for prod_id in product_ids],
                    },
                    "limit": limit,
                }
            ),
        ).json()

        return result["result"]["items"]
    
    def get_product_commissions(self, product_ids: list, limit=1):
        result = self.get_price_objects(product_ids, limit)

        product_comissions = {}
        for item in result:
            product_comissions[item["product_id"]] = {
                "acquiring": item["acquiring"],
                **item["commissions"],
            }
        return product_comissions
    
    def get_product_info_list_by_product_id(self, product_id_list: list):
        result = requests.post(
            "https://api-seller.ozon.ru/v2/product/info/list",
            headers=self.ozon_headers,
            data=json.dumps({"product_id": product_id_list}),
        ).json()
        return result["result"]["items"]

    @staticmethod
    def get_product_id(products: list) -> list:
        return [item["product_id"] for item in products]
        
    @staticmethod
    def get_image_urls_from_product_info_list(product_info_list: list) -> dict:
        """Returns dict:
        {
            prod_id_1: [img1_url, ...],
            ...
            }
        }
        """
        images = {}
        for item in product_info_list:
            prod_id = item["id"]
            if item["primary_image"]:
                images[prod_id] = [item["primary_image"]]
            if item["images"]:
                images[prod_id].extend(
                    url for url in item["images"] if url != item["primary_image"]
                )
        return images
    
    @staticmethod
    def get_product_sku_from_product_info_list(product_info_list: list) -> dict:
        """Returns dict:
        {
            prod_id_1: sku_1,
            ...
            prod_id_n: {
                'fbs': sku_n_1,
                'fbo': sku_n_2
            }
        }
        """
        skus = {}
        for item in product_info_list:
            skus[item["id"]] = {
                "sku": item["sku"],
                "fbo_sku": item["fbo_sku"],
                "fbs_sku": item["fbs_sku"],
            }
        return skus
    
    @staticmethod
    def calculate_product_dimensions(product: dict) -> dict:
        dimension_unit = product["dimension_unit"]
        prod_length = product["depth"]
        prod_width = product["width"]
        prod_height = product["height"]

        if dimension_unit == "mm":
            prod_length /= 100
            prod_width /= 100
            prod_height /= 100
        elif dimension_unit == "cm":
            prod_length /= 10
            prod_width /= 10
            prod_height /= 10
        elif dimension_unit == "in":
            prod_length = round(prod_length / 3.937, 1)
            prod_width = round(prod_width / 3.937, 1)
            prod_height = round(prod_height / 3.937, 1)

        return {"length": prod_length, "width": prod_width, "height": prod_height}
    
    @staticmethod
    def calculate_product_weight_in_kg(product: dict) -> float:
        weight_unit = product["weight_unit"]
        prod_weight = product["weight"]

        if weight_unit == "g":
            prod_weight = round(prod_weight / 1000, 2)
        else:
            raise Exception("Неизвестная мера веса")

        return prod_weight