from datetime import datetime, time, timedelta
import os
import subprocess
from typing import NoReturn

from dotenv import load_dotenv
from temporalio import activity
import requests

from ozon_api import (
    import_products_from_ozon_api_to_file,
    import_transactions_from_ozon_api_to_file,
    import_stocks_from_ozon_api_to_file,
    import_prices_from_ozon_api_to_file,
    import_postings_from_ozon_api_to_file,
    import_fbo_supply_orders_from_ozon_api_to_file,
    import_actions_from_ozon_api_to_file,
    convert_datetime_str_to_ozon_date,
)
from fill_db import (
    authenticate_to_odoo,
    divide_csv_into_chunks,
    send_csv_file_to_ozon_import_file,
    remove_all_csv_files,
)

load_dotenv()

USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
TRANSACTIONS_PATH = "./transactions.csv"
PRODUCTS_PATH = "./products.csv"
STOCKS_PATH = "./stocks.csv"
PRICES_PATH = "./prices.csv"
POSTINGS_PATH = "./postings.csv"
FBO_SUPPLY_ORDERS_PATH = "./fbo_supply_orders.csv"
ACTIONS_PATH = "./actions.csv"


@activity.defn
async def activity_import_products() -> NoReturn:
    import_products_from_ozon_api_to_file(PRODUCTS_PATH)


@activity.defn
async def activity_write_products_to_odoo():
    session_id = authenticate_to_odoo(username=USERNAME, password=PASSWORD)
    divide_csv_into_chunks(PRODUCTS_PATH)
    url = "http://0.0.0.0:8070/import/products_from_ozon_api_to_file"

    for fpath in os.listdir():
        if fpath.startswith("chunk"):
            send_csv_file_to_ozon_import_file(
                url=url, session_id=session_id, file_path=fpath
            )


@activity.defn
async def activity_import_transactions():
    date_from = convert_datetime_str_to_ozon_date(
        str(datetime.combine(datetime.now(), time.min) - timedelta(days=1))
    )
    date_to = convert_datetime_str_to_ozon_date(
        str(datetime.combine(datetime.now(), time.max) - timedelta(days=1))
    )
    next_page = 1
    while next_page != "Successfully imported all transactions!":
        next_page = import_transactions_from_ozon_api_to_file(
            file_path=TRANSACTIONS_PATH, date_from=date_from, date_to=date_to
        )


@activity.defn
async def activity_import_transactions_from_prev_month():
    date_from = convert_datetime_str_to_ozon_date(
        str(datetime.combine(datetime.now(), time.min) - timedelta(days=30))
    )
    date_to = convert_datetime_str_to_ozon_date(
        str(datetime.combine(datetime.now(), time.max) - timedelta(days=1))
    )
    next_page = 1
    while next_page != "Successfully imported all transactions!":
        next_page = import_transactions_from_ozon_api_to_file(
            file_path=TRANSACTIONS_PATH, date_from=date_from, date_to=date_to
        )


@activity.defn
async def activity_import_transactions_from_prev_2_years():
    date_from = datetime.combine(datetime.now(), time.min) - timedelta(days=730)
    string_date_from = convert_datetime_str_to_ozon_date(str(date_from))

    date_to = datetime.combine(datetime.now(), time.min) - timedelta(days=702)
    string_date_to = convert_datetime_str_to_ozon_date(str(date_to))
    today = datetime.now()

    while date_to < today:
        print(f"Transactions from {string_date_from} ---------- to {string_date_to}")
        next_page = 1
        while next_page != "Successfully imported all transactions!":
            next_page = import_transactions_from_ozon_api_to_file(
                file_path=TRANSACTIONS_PATH,
                date_from=string_date_from,
                date_to=string_date_to,
                next_page=next_page,
            )

        date_from = date_to
        date_to = date_to + timedelta(days=28)
        string_date_from = convert_datetime_str_to_ozon_date(str(date_from))
        string_date_to = convert_datetime_str_to_ozon_date(str(date_to))


@activity.defn
async def activity_write_transactions_to_odoo():
    session_id = authenticate_to_odoo(username=USERNAME, password=PASSWORD)
    divide_csv_into_chunks(TRANSACTIONS_PATH)
    url = "http://0.0.0.0:8070/import/transactions_from_ozon_api_to_file"

    for fpath in os.listdir():
        if fpath.startswith("chunk"):
            send_csv_file_to_ozon_import_file(
                url=url, session_id=session_id, file_path=fpath
            )


@activity.defn
async def activity_import_stocks() -> NoReturn:
    import_stocks_from_ozon_api_to_file(STOCKS_PATH)


@activity.defn
async def activity_write_stocks_to_odoo():
    session_id = authenticate_to_odoo(username=USERNAME, password=PASSWORD)
    divide_csv_into_chunks(STOCKS_PATH)
    url = "http://0.0.0.0:8070/import/stocks_from_ozon_api_to_file"

    for fpath in os.listdir():
        if fpath.startswith("chunk"):
            send_csv_file_to_ozon_import_file(
                url=url, session_id=session_id, file_path=fpath
            )


@activity.defn
async def activity_remove_csv_files():
    remove_all_csv_files()


@activity.defn
async def activity_compute_products_coefs_and_groups():
    session_id = authenticate_to_odoo(username=USERNAME, password=PASSWORD)
    url = "http://0.0.0.0:8070/compute/products_coefs_and_groups"
    headers = {"Cookie": f"session_id={session_id}"}
    response = requests.post(url, headers=headers)
    print(response.text)


@activity.defn
async def activity_compute_products_percent_expenses():
    session_id = authenticate_to_odoo(username=USERNAME, password=PASSWORD)
    url = "http://0.0.0.0:8070/compute/products_percent_expenses"
    subprocess.Popen(
        ["curl", "-X", "POST", "-H", f"Cookie: session_id={session_id}", url, "&"]
    )
    print("Products percent expenses computation launched.")


@activity.defn
async def activity_compute_products_all_expenses():
    session_id = authenticate_to_odoo(username=USERNAME, password=PASSWORD)
    url = "http://0.0.0.0:8070/compute/products_all_expenses"
    headers = {"Cookie": f"session_id={session_id}"}
    response = requests.post(url, headers=headers)
    print(response.text)


@activity.defn
async def activity_create_daily_tasks():
    session_id = authenticate_to_odoo(username=USERNAME, password=PASSWORD)
    url = "http://0.0.0.0:8070/tasks/create_daily_tasks"
    headers = {"Cookie": f"session_id={session_id}"}
    response = requests.post(url, headers=headers)
    print(response.text)


@activity.defn
async def activity_import_prices():
    import_prices_from_ozon_api_to_file(PRICES_PATH)


@activity.defn
async def activity_write_prices_to_odoo():
    session_id = authenticate_to_odoo(username=USERNAME, password=PASSWORD)
    divide_csv_into_chunks(PRICES_PATH)
    url = "http://0.0.0.0:8070/import/prices_from_ozon_api_to_file"

    for fpath in os.listdir():
        if fpath.startswith("chunk"):
            send_csv_file_to_ozon_import_file(
                url=url, session_id=session_id, file_path=fpath
            )


@activity.defn
async def activity_import_postings():
    date_from = convert_datetime_str_to_ozon_date(
        str(datetime.combine(datetime.now(), time.min) - timedelta(days=1))
    )
    date_to = convert_datetime_str_to_ozon_date(
        str(datetime.combine(datetime.now(), time.max) - timedelta(days=1))
    )

    import_postings_from_ozon_api_to_file(
        file_path=POSTINGS_PATH, date_from=date_from, date_to=date_to
    )


@activity.defn
async def activity_write_postings_to_odoo():
    session_id = authenticate_to_odoo(username=USERNAME, password=PASSWORD)
    divide_csv_into_chunks(POSTINGS_PATH)
    url = "http://0.0.0.0:8070/import/postings_from_ozon_api_to_file"

    for fpath in os.listdir():
        if fpath.startswith("chunk"):
            send_csv_file_to_ozon_import_file(
                url=url, session_id=session_id, file_path=fpath
            )


@activity.defn
async def activity_import_fbo_supply_orders():
    import_fbo_supply_orders_from_ozon_api_to_file(FBO_SUPPLY_ORDERS_PATH)


@activity.defn
async def activity_write_fbo_supply_orders_to_odoo():
    session_id = authenticate_to_odoo(username=USERNAME, password=PASSWORD)
    divide_csv_into_chunks(FBO_SUPPLY_ORDERS_PATH)
    url = "http://0.0.0.0:8070/import/fbo_supply_orders_from_ozon_api_to_file"

    for fpath in os.listdir():
        if fpath.startswith("chunk"):
            send_csv_file_to_ozon_import_file(
                url=url, session_id=session_id, file_path=fpath
            )


@activity.defn
async def activity_import_ozon_actions():
    import_actions_from_ozon_api_to_file(ACTIONS_PATH)


@activity.defn
async def activity_write_ozon_actions_to_odoo():
    session_id = authenticate_to_odoo(username=USERNAME, password=PASSWORD)
    url = "http://0.0.0.0:8070/import/ozon_actions"
    send_csv_file_to_ozon_import_file(
        url=url, session_id=session_id, file_path=ACTIONS_PATH
    )
