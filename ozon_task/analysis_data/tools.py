import requests

from functools import wraps
from typing import Callable
from auth_odoo import AuthOdoo


def odoo_log(decorator_data: dict):
    def decorator(fn: Callable):
        @wraps(fn)
        async def wrapper(*args, **kwargs):
            print(decorator_data)
            await OdooActivitiesLogging().create_mass_data_import(decorator_data)
            res = await fn(*args, **kwargs)
            print(res)
            print(decorator_data)
            return res

        return wrapper

    return decorator


class OdooActivitiesLogging(AuthOdoo):
    async def create_mass_data_import(self, data: dict) -> None:
        path = "api/v1/create-mass-data-import"
        endpoint = f"{self.url}{path}"
        headers = self.connect_to_odoo_api_with_auth()
        data = {'data': str(data)}
        response = requests.post(endpoint, headers=headers, data=data)

        if response.status_code != 200:
            raise requests.exceptions.RequestException()
