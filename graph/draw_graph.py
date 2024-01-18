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
        path = "api/v1/get-data-for-draw-graphs"
        endpoint = f"{self.url}{path}"
        headers = self.connect_to_odoo_api_with_auth()
        response = requests.post(endpoint, headers=headers)
        
        if response.status_code != 200:
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
            plt.gca().xaxis.set_major_locator(mdates.WeekdayLocator(interval=2))
            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))

            plt.yticks(np.arange(min(qty), max(qty) + 1, step=1))

            plt.tight_layout()
            plt.savefig(f'../static/images/odoo/{product_id}.png')


    # def send_to_odoo(self, images: list) -> None:
    #     path = "api/v1/save-images-for-lots"
    #     endpoint = f"{self.url}{path}"
    #     headers = self.connect_to_odoo_api_with_auth()
    #     data = {'data': str(data), 'today': today, 'one_week_ago': one_week_ago}
    #     response = requests.post(endpoint, headers=headers, data=data)
        
    #     if response.status_code != 200:
    #         raise requests.exceptions.RequestException()
    
    def main(self) -> None:
        data = self.get_data_for_graphs()
        self.treatment(data)
        # self.send_to_odoo(data, images)
        
DrawOdoo().main()