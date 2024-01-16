import json
import requests

from os import getenv
from dotenv import load_dotenv
from auth_odoo import AuthOdoo
from time import sleep


load_dotenv()


class OzonNumberOfProducts(AuthOdoo):
    def __init__(self) -> None:
        super().__init__()
        self.headers_ozon = {
            "Client-Id": getenv("OZON_CLIENT_ID"),
            "Api-Key": getenv("OZON_API_KEY"),
        }
        self.chunk_size = 500

    def get_skus(self) -> requests.Response:
        path = "api/v1/get-all-skus-of-lots"
        endpoint = f"{self.url}{path}"
        headers = self.connect_to_odoo_api_with_auth()
        response = requests.get(endpoint, headers=headers)

        if response.status_code != 200:
            return response.status_code
        return [
            "679301130",
            "669996337",
        ]
        return response.json()

    def requests_ozon(self, skus: list):
        result = requests.post(
            "https://api-seller.ozon.ru/v1/product/info/stocks-by-warehouse/fbs",
            headers=self.headers_ozon,
            data=json.dumps({
                "sku": skus
            }),
        )
        return result.json()['result']

    def treatment(self, data: list) -> None:
        products = {}

        for product in data:
            present = product['present']
            reserved = product['reserved']
            sku = product['sku']
            
            if sku not in products:
                products[sku] = {'present': 0, 'reserved': 0}
                
            products[sku]['present'] += present
            products[sku]['reserved'] += reserved
        
        return products

    def create_chunks(self, elements: list):
        return [elements[i:i + self.chunk_size] for i in range(0, len(elements), self.chunk_size)]
    
    def send_to_odoo(self, data: dict) -> None:
        path = "api/v1/save-numbers-of-products-history"
        endpoint = f"{self.url}{path}"
        headers = self.connect_to_odoo_api_with_auth()
        data = {'data': str(data)}
        response = requests.post(endpoint, headers=headers, data=data)
        
        if response.status_code != 200:
            raise requests.exceptions.RequestException()
    
    def main(self):
        all_skus = self.get_skus()
        chunks = self.create_chunks(all_skus)

        for skus in chunks:
            data = self.requests_ozon(skus)
            data = self.treatment(data)
            self.send_to_odoo(data)