import requests
import json

from functools import wraps
from typing import Callable
from auth_odoo import AuthOdoo


def odoo_log(decorator_data: dict):
    def decorator(fn: Callable):
        @wraps(fn)
        async def wrapper(*args, **kwargs):
            print(decorator_data)
            oal = OdooActivitiesLogging()
            log_id = await oal.create_mass_data_import(decorator_data)
            res = await fn(*args, **kwargs)
            data = {
                'activity_data': res,
                'log_id': log_id,
                'state': 'done',
                'log_value': True,
            }
            await oal.update_mass_data_import(data)

            return res

        return wrapper

    return decorator


class OdooActivitiesLogging(AuthOdoo):
    def __init__(self):
        super().__init__()
        self.headers = {}

    async def create_mass_data_import(self, data: dict) -> None:
        path = "/api/v1/mass-data-import"
        endpoint = f"{self.url}{path}"
        headers = self.headers
        if not self.headers:
            headers = self.connect_to_odoo_api_with_auth()
            self.headers = headers
        data = {'data': data}
        response = requests.post(endpoint, headers=headers, json=data)

        if response.status_code != 200:
            raise requests.exceptions.RequestException()

        return response.json().get('result').get('log_id')

    async def update_mass_data_import(self, data: dict) -> None:
        path = "/api/v1/mass-data-import"
        endpoint = f"{self.url}{path}"
        data = {'data': data}
        headers = self.headers
        if not self.headers:
            headers = self.connect_to_odoo_api_with_auth()
            self.headers = headers
        response = requests.put(endpoint, headers=headers, json=data)

        if response.status_code != 200:
            raise requests.exceptions.RequestException()

