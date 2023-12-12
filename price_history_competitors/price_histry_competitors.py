import requests
import json
from datetime import datetime, timedelta


class PriceHistoryCompetitors:
    def __init__(self, username, password):
        self.username = username
        self.password = password

        self.url = 'http://0.0.0.0:8070/'
        self.db = 'db_odoo'

        self.chunk_size = 1000
        
        self.token_mpstats = '6577012915bcb8.30316494d539740253021878c9f1155b10958207'

    def get_days(self) -> tuple:
        today_date = datetime.now()
        yesterday_date = today_date - timedelta(days=1)

        today_date_str = today_date.strftime('%Y-%m-%d')
        yesterday_date_str = yesterday_date.strftime('%Y-%m-%d')
        return today_date_str, yesterday_date_str

    def connect_to_odoo_api_with_auth(self) -> dict:
        session_url = f'{self.url}/web/session/authenticate'
        data = {
            'jsonrpc': '2.0',
            'method': 'call',
            'params': {
                'db': self.db,
                'login': self.username,
                'password': self.password,
            }
        }
        session_response = requests.post(session_url, json=data)
        session_data = session_response.json()

        if session_data.get('result') and session_response.cookies.get('session_id'):
            session_id = session_response.cookies['session_id']
            headers = {'Cookie': f"session_id={session_id}"}
            return headers
        else:
            print(f'Error: Failed to authenticate - {session_data.get("error")}')
            return None
        
    def get_request_count_competitors(self, path:  str) -> requests.Response:
        endpoint = f"{self.url}{path}"
        headers = self.connect_to_odoo_api_with_auth()

        response = requests.get(endpoint, headers=headers)

        if response.status_code != 200:
            return response
        return response.text

    def get_request_sku_competitors(self, path: str, range: int) -> requests.Response:
        endpoint = f"{self.url}{path}"
        headers = self.connect_to_odoo_api_with_auth()

        data = {'range': range}
        response = requests.post(endpoint, headers=headers, data=data)

        if response.status_code != 200:
            return response
        

        answer = response.json()
        product_competitors_list = answer['product_competitors']
        return product_competitors_list

    def get_ad(self, ads: list) -> dict:
        today, yesterday = self.get_days()

        for ad in ads:
            date = ad.get('data')
            if date != yesterday:
                continue
            return ad

    def get_request_create_history_price(self, path: str, history_prices: list, sku: int):
        endpoint = f"{self.url}{path}"
        headers = self.connect_to_odoo_api_with_auth()
        print(sku)
        print(history_prices)
        data = {'ads': str(history_prices), 'sku': sku}
        print(data)
        response = requests.post(endpoint, headers=headers, data=data)

        return response.text
    
    def get_request_mpstats(self, sku: int) -> requests.Response:
        url = f'https://mpstats.io/api/oz/get/item/{sku}/sales'

        headers = {
            'X-Mpstats-TOKEN': self.token_mpstats,
            'Content-Type': 'application/json',
        }

        today, yesterday = self.get_days()
        params = {
            'd1':today,
            'd2': yesterday,
        }

        response = requests.get(url, headers=headers, params=params)

        return [
            {
                "no_data": 0,
                "data": "2023-12-11",
                "balance": 253,
                "sales": 0,
                "rating": 4.88,
                "price": 8490,
                "final_price": 6990,
                "is_bestseller": 1,
                "comments": 96
            },
            {
                "no_data": 0,
                "data": "2020-08-13",
                "balance": 193,
                "sales": 20,
                "rating": 4.88,
                "price": 8490,
                "final_price": 6990,
                "is_bestseller": 1,
                "comments": 96
            },
        ]
    
        if response.status_code != 200:
            print(f'MP status: {response.status_code}')
            return None
        return response.json()

    def main(self):
        res = self.get_request_count_competitors(
            path='/api/v1/price_history_competitors/count_records/'
        )
        data = json.loads(res)
        count_sku = data['total_records']

        num_chunks = count_sku // self.chunk_size
        num_chunks = num_chunks + 1

        create_history_prices = {}
        
        for i in range(num_chunks):
            list_sku = self.get_request_sku_competitors(
                path='/api/v1/price_history_competitors/get_sku/',
                range=i*self.chunk_size,
            )
            for sku in list_sku:
                ads = self.get_request_mpstats(sku)
                if ads is None:
                    continue
                
                ad = self.get_ad(ads)

                if sku not in create_history_prices:
                    create_history_prices[sku] = []

                create_history_prices[sku].append(ad)

        with open('data.txt', 'w') as file:
            print(create_history_prices)
            file.write(str(create_history_prices))

        return 'Success!'

    def activity_two(self, dict_ads: dict):
        for sku, ads in dict_ads.items():
            res = self.get_request_create_history_price(
                path='/api/v1/price_history_competitors/create_ads/', 
                history_prices=ads,
                sku=sku,
            )

def main():
    model = PriceHistoryCompetitors('admin', 'admin')
    res = model.main()
    print(res)

def activity_two(data_dict):
    model = PriceHistoryCompetitors('admin', 'admin')
    res = model.activity_two(data_dict)
    print(res)