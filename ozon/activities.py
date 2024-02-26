import os
import requests
import subprocess
from os import getenv
from datetime import datetime, time, timedelta

from tools import odoo_log, ImportLogging
from dotenv import load_dotenv
from temporalio import activity

from get_analysys_data import OzonAnalysisData
from get_ozon_numbers_of_products import OzonNumberOfProducts

from ozon_api import (
    convert_datetime_str_to_ozon_date,
    import_actions_from_ozon_api_to_file,
    import_fbo_supply_orders_from_ozon_api_to_file,
    import_postings_from_ozon_api_to_file,
    import_prices_from_ozon_api_to_file,
    import_products_from_ozon_api_to_file,
    import_stocks_from_ozon_api_to_file,
    import_transactions_from_ozon_api_to_file,
)
from fill_db import (
    authenticate_to_odoo,
    divide_csv_into_chunks,
    remove_all_csv_files,
    send_csv_file_to_ozon_import_file,
)


load_dotenv()


USERNAME = getenv("USERNAME")
PASSWORD = getenv("PASSWORD")
TRANSACTIONS_PATH = getenv("TRANSACTIONS_PATH")
PRODUCTS_PATH = getenv("PRODUCTS_PATH")
STOCKS_PATH = getenv("STOCKS_PATH")
PRICES_PATH = getenv("PRICES_PATH")
POSTINGS_PATH = getenv("POSTINGS_PATH")
FBO_SUPPLY_ORDERS_PATH = getenv("FBO_SUPPLY_ORDERS_PATH")
ACTIONS_PATH = getenv("ACTIONS_PATH")


@activity.defn
async def activity_import_products() -> None:
    import_products_from_ozon_api_to_file(PRODUCTS_PATH)

@activity.defn
@odoo_log({'name': 'Импорт Продуктов из файла в odoo'})
async def activity_write_products_to_odoo() -> None:
    session_id = authenticate_to_odoo(username=USERNAME, password=PASSWORD)
    divide_csv_into_chunks(PRODUCTS_PATH)
    url = "http://0.0.0.0:8070/import/products_from_ozon_api_to_file"

    for fpath in os.listdir():
        if fpath.startswith("chunk"):
            response = send_csv_file_to_ozon_import_file(
                url=url, session_id=session_id, file_path=fpath
            )
            if response.status_code != 200:
                print("activity_write_products_to_odoo error. Traceback in odoo log")
                raise requests.exceptions.RequestException()
            break

@activity.defn
@odoo_log({'name': 'Импорт Транзакций из Озон API в файл'})
async def activity_import_transactions() -> None:
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
@odoo_log({'name': 'Импорт Транзакций за предыдущий месяц из Озон API в файл'})
async def activity_import_transactions_from_prev_month() -> None:
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
@odoo_log({'name': 'Импорт транзакций за 2 года из Озон API в файл'})
async def activity_import_transactions_from_prev_2_years() -> None:
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
@odoo_log({'name': 'Импорт Транзакций из файла в odoo'})
async def activity_write_transactions_to_odoo() -> None:
    session_id = authenticate_to_odoo(username=USERNAME, password=PASSWORD)
    divide_csv_into_chunks(TRANSACTIONS_PATH)
    url = "http://0.0.0.0:8070/import/transactions_from_ozon_api_to_file"

    for fpath in os.listdir():
        if fpath.startswith("chunk"):
            response = send_csv_file_to_ozon_import_file(
                url=url, session_id=session_id, file_path=fpath
            )
            if response.status_code != 200:
                print("activity_write_transactions_to_odoo error. Traceback in odoo log")
                raise requests.exceptions.RequestException()

@activity.defn
@odoo_log({'name': 'Импорт Остатков из Озон API в файл'})
async def activity_import_stocks() -> None:
    import_stocks_from_ozon_api_to_file(STOCKS_PATH)

@activity.defn
@odoo_log({'name': 'Импорт Остатков из файла в odoo'})
async def activity_write_stocks_to_odoo() -> None:
    session_id = authenticate_to_odoo(username=USERNAME, password=PASSWORD)
    divide_csv_into_chunks(STOCKS_PATH)
    url = "http://0.0.0.0:8070/import/stocks_from_ozon_api_to_file"

    for fpath in os.listdir():
        if fpath.startswith("chunk"):
            response = send_csv_file_to_ozon_import_file(
                url=url, session_id=session_id, file_path=fpath
            )
            if response.status_code != 200:
                print("activity_write_stocks_to_odoo error. Traceback in odoo log")
                raise requests.exceptions.RequestException()

@activity.defn
@odoo_log({'name': 'Удаление файлов'})
async def activity_remove_csv_files() -> None:
    remove_all_csv_files()

@activity.defn
@odoo_log({'name': 'Запуск скрипта в odoo для расчета коэффициентов и групп продуктов'})
async def activity_compute_products_coefs_and_groups() -> None:
    session_id = authenticate_to_odoo(username=USERNAME, password=PASSWORD)
    url = "http://0.0.0.0:8070/compute/products_coefs_and_groups"
    headers = {"Cookie": f"session_id={session_id}"}
    response = requests.post(url, headers=headers)
    if response.status_code != 200:
        print("activity_compute_products_coefs_and_groups error. Traceback in odoo log")
        raise requests.exceptions.RequestException()
    print(response.text)

@activity.defn
@odoo_log({'name': 'Запуск скрипта в odoo для расчета процентных расходов'})
async def activity_compute_products_percent_expenses() -> None:
    session_id = authenticate_to_odoo(username=USERNAME, password=PASSWORD)
    url = "http://0.0.0.0:8070/compute/products_percent_expenses"
    subprocess.Popen(
        ["curl", "-X", "POST", "-H", f"Cookie: session_id={session_id}", url, "&"]
    )
    print("Products percent expenses computation launched.")

@activity.defn
@odoo_log({'name': 'Запуск скрипта в odoo для расчета всех расходов'})
async def activity_compute_products_all_expenses() -> None:
    session_id = authenticate_to_odoo(username=USERNAME, password=PASSWORD)
    url = "http://0.0.0.0:8070/compute/products_all_expenses"
    headers = {"Cookie": f"session_id={session_id}"}
    response = requests.post(url, headers=headers)
    if response.status_code != 200:
        print("activity_compute_products_all_expenses error. Traceback in odoo log")
        raise requests.exceptions.RequestException()
    print(response.text)

@activity.defn
@odoo_log({'name': 'Создание ежедневных задач'})
async def activity_create_daily_tasks() -> None:
    session_id = authenticate_to_odoo(username=USERNAME, password=PASSWORD)
    url = "http://0.0.0.0:8070/tasks/create_daily_tasks"
    headers = {"Cookie": f"session_id={session_id}"}
    response = requests.post(url, headers=headers)
    if response.status_code != 200:
        print("activity_create_daily_tasks error. Traceback in odoo log")
        raise requests.exceptions.RequestException()
    print(response.text)

@activity.defn
@odoo_log({'name': 'Импорт Цен из Озон API в файл'})
async def activity_import_prices() -> None:
    import_prices_from_ozon_api_to_file(PRICES_PATH)

@activity.defn
@odoo_log({'name': 'Импорт Цен из файла в odoo'})
async def activity_write_prices_to_odoo() -> None:
    session_id = authenticate_to_odoo(username=USERNAME, password=PASSWORD)
    divide_csv_into_chunks(PRICES_PATH)
    url = "http://0.0.0.0:8070/import/prices_from_ozon_api_to_file"

    for fpath in os.listdir():
        if fpath.startswith("chunk"):
            response = send_csv_file_to_ozon_import_file(
                url=url, session_id=session_id, file_path=fpath
            )
            if response.status_code != 200:
                print("activity_write_prices_to_odoo error. Traceback in odoo log")
                raise requests.exceptions.RequestException()

@activity.defn
@odoo_log({'name': 'Импорт Отправлений из Озон API в файл'})
async def activity_import_postings() -> None:
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
@odoo_log({'name': 'Импорт Отправлений из файла в odoo'})
async def activity_write_postings_to_odoo() -> None:
    session_id = authenticate_to_odoo(username=USERNAME, password=PASSWORD)
    divide_csv_into_chunks(POSTINGS_PATH)
    url = "http://0.0.0.0:8070/import/postings_from_ozon_api_to_file"

    for fpath in os.listdir():
        if fpath.startswith("chunk"):
            response = send_csv_file_to_ozon_import_file(
                url=url, session_id=session_id, file_path=fpath
            )
            if response.status_code != 200:
                print("activity_import_postings error. Traceback in odoo log")
                raise requests.exceptions.RequestException()

@activity.defn
@odoo_log({'name': 'Импорт Заказов на поставку из Озон API в файл'})
async def activity_import_fbo_supply_orders() -> None:
    import_fbo_supply_orders_from_ozon_api_to_file(FBO_SUPPLY_ORDERS_PATH)

@activity.defn
@odoo_log({'name': 'Импорт Заказов на поставку из файла в odoo'})
async def activity_write_fbo_supply_orders_to_odoo() -> None:
    session_id = authenticate_to_odoo(username=USERNAME, password=PASSWORD)
    divide_csv_into_chunks(FBO_SUPPLY_ORDERS_PATH)
    url = "http://0.0.0.0:8070/import/fbo_supply_orders_from_ozon_api_to_file"

    for fpath in os.listdir():
        if fpath.startswith("chunk"):
            response = send_csv_file_to_ozon_import_file(
                url=url, session_id=session_id, file_path=fpath
            )
            if response.status_code != 200:
                print("activity_write_fbo_supply_orders_to_odoo error. Traceback in odoo log")
                raise requests.exceptions.RequestException()

@activity.defn
@odoo_log({'name': 'Импорт Акций из Озон API в файл'})
async def activity_import_ozon_actions() -> None:
    import_actions_from_ozon_api_to_file(ACTIONS_PATH)

@activity.defn
@odoo_log({'name': 'Импорт Акций из файла в odoo'})
async def activity_write_ozon_actions_to_odoo() -> None:
    session_id = authenticate_to_odoo(username=USERNAME, password=PASSWORD)
    url = "http://0.0.0.0:8070/import/ozon_actions"
    response = send_csv_file_to_ozon_import_file(
        url=url, session_id=session_id, file_path=ACTIONS_PATH
    )
    if response.status_code != 200:
        print("activity_write_fbo_supply_orders_to_odoo error. Traceback in odoo log")
        raise requests.exceptions.RequestException()

@activity.defn
@odoo_log({'name': 'Импорт данных по интересу к товарам'})
async def activity_ozon_analysis_data_activity() -> dict:
    return OzonAnalysisData().main()

@activity.defn
@odoo_log({'name': 'Импорт количества продуктов'})
async def activity_get_ozon_number_of_products() -> dict:
    return OzonNumberOfProducts().main()

@activity.defn
async def activity_create_mass_data_import() -> None:
    await ImportLogging().create_mass_data_import({'name': 'Главный поток'})

