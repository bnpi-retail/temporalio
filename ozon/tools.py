import traceback
import requests
import logging

from functools import wraps
from typing import Callable
from auth_odoo import AuthOdoo

logger = logging.getLogger(__name__)


def odoo_log(decorator_data: dict):
    """
    Decorator for activity that create "ozon.mass_data_import" log data in odoo.
    :param decorator_data: {'name': 'Импорт продуктов'} will use to
           set "ozon.mass_data_import" name
    :return:
    """
    def decorator(activity: Callable):
        """
        fn must return data dict that will write to "ozon.mass_data_import"
        displaying_data field in key: value format
        """
        @wraps(activity)
        async def wrapper(*args, **kwargs):
            print(decorator_data)
            oal = OdooActivitiesLogging()
            log_id = await oal.create_mass_data_import(decorator_data)
            res = await activity(*args, **kwargs)
            if log_id:
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

    async def create_mass_data_import(self, data: dict) -> int | None:
        path = "/api/v1/mass-data-import"
        endpoint = f"{self.url}{path}"
        headers = self.connect_to_odoo_api_with_auth()
        data = {'data': data}
        response = requests.post(endpoint, headers=headers, json=data)

        if response.status_code != 200:
            raise requests.exceptions.RequestException()

        response_res = response.json().get('result')
        if response_res:
            log_id = response_res.get('log_id')

            return log_id

    async def update_mass_data_import(self, data: dict) -> None:
        path = "/api/v1/mass-data-import"
        endpoint = f"{self.url}{path}"
        data = {'data': data}
        headers = self.connect_to_odoo_api_with_auth()
        response = requests.put(endpoint, headers=headers, json=data)

        if response.status_code != 200:
            raise requests.exceptions.RequestException()


class OzonApiActivityException(Exception):
    pass