import requests
from datetime import datetime, timedelta


def get_days() -> tuple:
    today_date = datetime.now()
    yesterday_date = today_date - timedelta(days=1)

    today_date_str = today_date.strftime('%Y-%m-%d')
    yesterday_date_str = yesterday_date.strftime('%Y-%m-%d')
    return today_date_str, yesterday_date_str

def get_request_mpstats(sku: int) -> requests.Response:
    url = f'https://mpstats.io/api/oz/get/item/{sku}/sales'

    headers = {
        'X-Mpstats-TOKEN': '658191888c92d3.6926326394b21a4a75d6efac2ba3ba09bde8db4a',
        'Content-Type': 'application/json',
    }
    today, yesterday = get_days()
    params = {
        'd1':today,
        'd2': yesterday,
    }
    response = requests.get(url, headers=headers, params=params)
    return response.json()

sku = '178146273'
res = get_request_mpstats(sku)
print(res)