import io
import datetime
import json

import requests
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import matplotlib.dates as mdates
from os import getenv
from dotenv import load_dotenv
from datetime import timedelta
from datetime import datetime as dt
from time import sleep

from auth_odoo import AuthOdoo


load_dotenv()


class DrawOdoo(AuthOdoo):
    def __init__(self) -> None:
        super().__init__()

    def get_data_for_graphs(self) -> dict:
        return {"6737--2023": [{"week": 1, "qty": 0, "revenue": 0}, {"week": 2, "qty": 1, "revenue": 562.91}, {"week": 3, "qty": 0, "revenue": 0}, {"week": 4, "qty": 0, "revenue": 0}, {"week": 5, "qty": 0, "revenue": 0}, {"week": 6, "qty": 0, "revenue": 0}, {"week": 7, "qty": 0, "revenue": 0}, {"week": 8, "qty": 0, "revenue": 0}, {"week": 9, "qty": 0, "revenue": 0}, {"week": 10, "qty": 0, "revenue": 0}, {"week": 11, "qty": 0, "revenue": 0}, {"week": 12, "qty": 0, "revenue": 0}, {"week": 13, "qty": 0, "revenue": 0}, {"week": 14, "qty": 0, "revenue": 0}, {"week": 15, "qty": 0, "revenue": 0}, {"week": 16, "qty": 0, "revenue": 0}, {"week": 17, "qty": 0, "revenue": 0}, {"week": 18, "qty": 0, "revenue": 0}, {"week": 19, "qty": 0, "revenue": 0}, {"week": 20, "qty": 0, "revenue": 0}, {"week": 21, "qty": 0, "revenue": 0}, {"week": 22, "qty": 0, "revenue": 0}, {"week": 23, "qty": 0, "revenue": 0}, {"week": 24, "qty": 0, "revenue": 0}, {"week": 25, "qty": 0, "revenue": 0}, {"week": 26, "qty": 0, "revenue": 0}, {"week": 27, "qty": 0, "revenue": 0}, {"week": 28, "qty": 0, "revenue": 0}, {"week": 29, "qty": 0, "revenue": 0}, {"week": 30, "qty": 0, "revenue": 0}, {"week": 31, "qty": 0, "revenue": 0}, {"week": 32, "qty": 0, "revenue": 0}, {"week": 33, "qty": 0, "revenue": 0}, {"week": 34, "qty": 0, "revenue": 0}, {"week": 35, "qty": 0, "revenue": 0}, {"week": 36, "qty": 0, "revenue": 0}, {"week": 37, "qty": 0, "revenue": 0}, {"week": 38, "qty": 0, "revenue": 0}, {"week": 39, "qty": 0, "revenue": 0}, {"week": 40, "qty": 0, "revenue": 0}, {"week": 41, "qty": 0, "revenue": 0}, {"week": 42, "qty": 0, "revenue": 0}, {"week": 43, "qty": 0, "revenue": 0}, {"week": 44, "qty": 0, "revenue": 0}, {"week": 45, "qty": 0, "revenue": 0}, {"week": 46, "qty": 0, "revenue": 0}, {"week": 47, "qty": 0, "revenue": 0}, {"week": 48, "qty": 0, "revenue": 0}, {"week": 49, "qty": 0, "revenue": 0}, {"week": 50, "qty": 0, "revenue": 0}, {"week": 51, "qty": 0, "revenue": 0}, {"week": 52, "qty": 0, "revenue": 0}], "14987--2023": [{"week": 1, "qty": 2, "revenue": 2673.8599999999997}, {"week": 2, "qty": 2, "revenue": 2670.1800000000003}, {"week": 3, "qty": 0, "revenue": 0}, {"week": 4, "qty": 0, "revenue": 0}, {"week": 5, "qty": 0, "revenue": 0}, {"week": 6, "qty": 0, "revenue": 0}, {"week": 7, "qty": 0, "revenue": 0}, {"week": 8, "qty": 0, "revenue": 0}, {"week": 9, "qty": 0, "revenue": 0}, {"week": 10, "qty": 0, "revenue": 0}, {"week": 11, "qty": 0, "revenue": 0}, {"week": 12, "qty": 0, "revenue": 0}, {"week": 13, "qty": 0, "revenue": 0}, {"week": 14, "qty": 0, "revenue": 0}, {"week": 15, "qty": 0, "revenue": 0}, {"week": 16, "qty": 0, "revenue": 0}, {"week": 17, "qty": 0, "revenue": 0}, {"week": 18, "qty": 0, "revenue": 0}, {"week": 19, "qty": 0, "revenue": 0}, {"week": 20, "qty": 0, "revenue": 0}, {"week": 21, "qty": 0, "revenue": 0}, {"week": 22, "qty": 0, "revenue": 0}, {"week": 23, "qty": 0, "revenue": 0}, {"week": 24, "qty": 0, "revenue": 0}, {"week": 25, "qty": 0, "revenue": 0}, {"week": 26, "qty": 0, "revenue": 0}, {"week": 27, "qty": 0, "revenue": 0}, {"week": 28, "qty": 0, "revenue": 0}, {"week": 29, "qty": 0, "revenue": 0}, {"week": 30, "qty": 0, "revenue": 0}, {"week": 31, "qty": 0, "revenue": 0}, {"week": 32, "qty": 0, "revenue": 0}, {"week": 33, "qty": 0, "revenue": 0}, {"week": 34, "qty": 0, "revenue": 0}, {"week": 35, "qty": 0, "revenue": 0}, {"week": 36, "qty": 0, "revenue": 0}, {"week": 37, "qty": 0, "revenue": 0}, {"week": 38, "qty": 0, "revenue": 0}, {"week": 39, "qty": 0, "revenue": 0}, {"week": 40, "qty": 0, "revenue": 0}, {"week": 41, "qty": 0, "revenue": 0}, {"week": 42, "qty": 0, "revenue": 0}, {"week": 43, "qty": 0, "revenue": 0}, {"week": 44, "qty": 0, "revenue": 0}, {"week": 45, "qty": 0, "revenue": 0}, {"week": 46, "qty": 0, "revenue": 0}, {"week": 47, "qty": 0, "revenue": 0}, {"week": 48, "qty": 1, "revenue": 1341.62}, {"week": 49, "qty": 0, "revenue": 0}, {"week": 50, "qty": 4, "revenue": 5399.74}, {"week": 51, "qty": 2, "revenue": 2709.66}, {"week": 52, "qty": 5, "revenue": 6734.39}], "4--2023": [{"week": 1, "qty": 0, "revenue": 0}, {"week": 2, "qty": 0, "revenue": 0}, {"week": 3, "qty": 0, "revenue": 0}, {"week": 4, "qty": 0, "revenue": 0}, {"week": 5, "qty": 0, "revenue": 0}, {"week": 6, "qty": 0, "revenue": 0}, {"week": 7, "qty": 0, "revenue": 0}, {"week": 8, "qty": 0, "revenue": 0}, {"week": 9, "qty": 0, "revenue": 0}, {"week": 10, "qty": 0, "revenue": 0}, {"week": 11, "qty": 0, "revenue": 0}, {"week": 12, "qty": 0, "revenue": 0}, {"week": 13, "qty": 0, "revenue": 0}, {"week": 14, "qty": 0, "revenue": 0}, {"week": 15, "qty": 0, "revenue": 0}, {"week": 16, "qty": 0, "revenue": 0}, {"week": 17, "qty": 0, "revenue": 0}, {"week": 18, "qty": 0, "revenue": 0}, {"week": 19, "qty": 0, "revenue": 0}, {"week": 20, "qty": 0, "revenue": 0}, {"week": 21, "qty": 0, "revenue": 0}, {"week": 22, "qty": 0, "revenue": 0}, {"week": 23, "qty": 0, "revenue": 0}, {"week": 24, "qty": 0, "revenue": 0}, {"week": 25, "qty": 0, "revenue": 0}, {"week": 26, "qty": 0, "revenue": 0}, {"week": 27, "qty": 0, "revenue": 0}, {"week": 28, "qty": 0, "revenue": 0}, {"week": 29, "qty": 0, "revenue": 0}, {"week": 30, "qty": 0, "revenue": 0}, {"week": 31, "qty": 0, "revenue": 0}, {"week": 32, "qty": 0, "revenue": 0}, {"week": 33, "qty": 0, "revenue": 0}, {"week": 34, "qty": 0, "revenue": 0}, {"week": 35, "qty": 0, "revenue": 0}, {"week": 36, "qty": 0, "revenue": 0}, {"week": 37, "qty": 0, "revenue": 0}, {"week": 38, "qty": 0, "revenue": 0}, {"week": 39, "qty": 0, "revenue": 0}, {"week": 40, "qty": 0, "revenue": 0}, {"week": 41, "qty": 0, "revenue": 0}, {"week": 42, "qty": 0, "revenue": 0}, {"week": 43, "qty": 0, "revenue": 0}, {"week": 44, "qty": 0, "revenue": 0}, {"week": 45, "qty": 0, "revenue": 0}, {"week": 46, "qty": 0, "revenue": 0}, {"week": 47, "qty": 0, "revenue": 0}, {"week": 48, "qty": 1, "revenue": 78.63}, {"week": 49, "qty": 0, "revenue": 0}, {"week": 50, "qty": 0, "revenue": 0}, {"week": 51, "qty": 0, "revenue": 0}, {"week": 52, "qty": 0, "revenue": 0}], "6730--2023": [{"week": 1, "qty": 0, "revenue": 0}, {"week": 2, "qty": 0, "revenue": 0}, {"week": 3, "qty": 0, "revenue": 0}, {"week": 4, "qty": 0, "revenue": 0}, {"week": 5, "qty": 0, "revenue": 0}, {"week": 6, "qty": 0, "revenue": 0}, {"week": 7, "qty": 0, "revenue": 0}, {"week": 8, "qty": 0, "revenue": 0}, {"week": 9, "qty": 0, "revenue": 0}, {"week": 10, "qty": 0, "revenue": 0}, {"week": 11, "qty": 0, "revenue": 0}, {"week": 12, "qty": 0, "revenue": 0}, {"week": 13, "qty": 0, "revenue": 0}, {"week": 14, "qty": 0, "revenue": 0}, {"week": 15, "qty": 0, "revenue": 0}, {"week": 16, "qty": 0, "revenue": 0}, {"week": 17, "qty": 0, "revenue": 0}, {"week": 18, "qty": 1, "revenue": 523.99}, {"week": 19, "qty": 0, "revenue": 0}, {"week": 20, "qty": 0, "revenue": 0}, {"week": 21, "qty": 0, "revenue": 0}, {"week": 22, "qty": 0, "revenue": 0}, {"week": 23, "qty": 0, "revenue": 0}, {"week": 24, "qty": 0, "revenue": 0}, {"week": 25, "qty": 0, "revenue": 0}, {"week": 26, "qty": 0, "revenue": 0}, {"week": 27, "qty": 0, "revenue": 0}, {"week": 28, "qty": 0, "revenue": 0}, {"week": 29, "qty": 0, "revenue": 0}, {"week": 30, "qty": 0, "revenue": 0}, {"week": 31, "qty": 0, "revenue": 0}, {"week": 32, "qty": 0, "revenue": 0}, {"week": 33, "qty": 0, "revenue": 0}, {"week": 34, "qty": 0, "revenue": 0}, {"week": 35, "qty": 0, "revenue": 0}, {"week": 36, "qty": 0, "revenue": 0}, {"week": 37, "qty": 0, "revenue": 0}, {"week": 38, "qty": 0, "revenue": 0}, {"week": 39, "qty": 0, "revenue": 0}, {"week": 40, "qty": 0, "revenue": 0}, {"week": 41, "qty": 0, "revenue": 0}, {"week": 42, "qty": 0, "revenue": 0}, {"week": 43, "qty": 0, "revenue": 0}, {"week": 44, "qty": 0, "revenue": 0}, {"week": 45, "qty": 0, "revenue": 0}, {"week": 46, "qty": 0, "revenue": 0}, {"week": 47, "qty": 0, "revenue": 0}, {"week": 48, "qty": 0, "revenue": 0}, {"week": 49, "qty": 0, "revenue": 0}, {"week": 50, "qty": 0, "revenue": 0}, {"week": 51, "qty": 0, "revenue": 0}, {"week": 52, "qty": 0, "revenue": 0}], "6730--2022": [{"week": 1, "qty": 0, "revenue": 0}, {"week": 2, "qty": 0, "revenue": 0}, {"week": 3, "qty": 0, "revenue": 0}, {"week": 4, "qty": 0, "revenue": 0}, {"week": 5, "qty": 0, "revenue": 0}, {"week": 6, "qty": 0, "revenue": 0}, {"week": 7, "qty": 0, "revenue": 0}, {"week": 8, "qty": 0, "revenue": 0}, {"week": 9, "qty": 0, "revenue": 0}, {"week": 10, "qty": 0, "revenue": 0}, {"week": 11, "qty": 0, "revenue": 0}, {"week": 12, "qty": 0, "revenue": 0}, {"week": 13, "qty": 0, "revenue": 0}, {"week": 14, "qty": 0, "revenue": 0}, {"week": 15, "qty": 0, "revenue": 0}, {"week": 16, "qty": 0, "revenue": 0}, {"week": 17, "qty": 0, "revenue": 0}, {"week": 18, "qty": 0, "revenue": 0}, {"week": 19, "qty": 0, "revenue": 0}, {"week": 20, "qty": 0, "revenue": 0}, {"week": 21, "qty": 1, "revenue": 877.0}, {"week": 22, "qty": 0, "revenue": 0}, {"week": 23, "qty": 0, "revenue": 0}, {"week": 24, "qty": 0, "revenue": 0}, {"week": 25, "qty": 0, "revenue": 0}, {"week": 26, "qty": 0, "revenue": 0}, {"week": 27, "qty": 0, "revenue": 0}, {"week": 28, "qty": 0, "revenue": 0}, {"week": 29, "qty": 0, "revenue": 0}, {"week": 30, "qty": 0, "revenue": 0}, {"week": 31, "qty": 0, "revenue": 0}, {"week": 32, "qty": 0, "revenue": 0}, {"week": 33, "qty": 0, "revenue": 0}, {"week": 34, "qty": 0, "revenue": 0}, {"week": 35, "qty": 0, "revenue": 0}, {"week": 36, "qty": 0, "revenue": 0}, {"week": 37, "qty": 0, "revenue": 0}, {"week": 38, "qty": 0, "revenue": 0}, {"week": 39, "qty": 0, "revenue": 0}, {"week": 40, "qty": 0, "revenue": 0}, {"week": 41, "qty": 0, "revenue": 0}, {"week": 42, "qty": 0, "revenue": 0}, {"week": 43, "qty": 0, "revenue": 0}, {"week": 44, "qty": 0, "revenue": 0}, {"week": 45, "qty": 0, "revenue": 0}, {"week": 46, "qty": 0, "revenue": 0}, {"week": 47, "qty": 0, "revenue": 0}, {"week": 48, "qty": 0, "revenue": 0}, {"week": 49, "qty": 0, "revenue": 0}, {"week": 50, "qty": 0, "revenue": 0}, {"week": 51, "qty": 0, "revenue": 0}, {"week": 52, "qty": 0, "revenue": 0}]}
        path = "api/v1/get-data-for-draw-graphs"
        endpoint = f"{self.url}{path}"
        headers = self.connect_to_odoo_api_with_auth()
        response = requests.get(endpoint, headers=headers)
        
        if response.status_code != 200:
            print(response.status_code)
            raise requests.exceptions.RequestException()
        
        return response.json()

    def moving_average(self, data, window_size):
        weights = np.repeat(1.0, window_size) / window_size
        return np.convolve(data, weights, 'valid')

    def treatment(self, data: dict) -> list:
        for product_id, weeks_data in data.items():
            weeks = [week["week"] for week in weeks_data]
            qty = [week["qty"] for week in weeks_data]
            revenue = [week["revenue"] for week in weeks_data]

            start_date = dt.strptime('2023-01-01', '%Y-%m-%d')
            days_per_week = 7
            week_dates = [start_date + timedelta(days=(week - 1) * days_per_week) for week in weeks]

            plt.figure(figsize=(10, 5))
            plt.plot(week_dates, qty, marker='o', label=f'История продаж')

            window_size = 5
            avg_qty = self.moving_average(qty, window_size)
            avg_week_dates = [start_date + timedelta(days=(week - 1) * days_per_week) for week in weeks[window_size - 1:]]

            plt.plot(avg_week_dates, avg_qty, color='r', linestyle='--', label=f'Средняя скользящая линия')

            plt.title('История продаж')
            plt.xlabel('Дата')
            plt.ylabel('Проданных товаров, кол.')
            plt.legend()

            plt.xticks(rotation=45)
            plt.gca().xaxis.set_major_locator(mdates.MonthLocator())
            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m.%Y'))

            plt.yticks(np.arange(min(qty), max(qty) + 1, step=1))

            plt.tight_layout()
            plt.savefig(f'../static/images/odoo/{product_id}.png')
            # plt.savefig(f'/home/sammy/static/images/odoo/{product_id}.png')

    def main(self) -> None:
        data = self.get_data_for_graphs()
        self.treatment(data)
        
DrawOdoo().main()