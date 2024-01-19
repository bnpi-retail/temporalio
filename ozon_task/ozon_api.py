import copy
import csv
import json

import os
import requests

from dotenv import load_dotenv

load_dotenv()

OZON_CLIENT_ID = os.getenv("OZON_CLIENT_ID")
OZON_API_KEY = os.getenv("OZON_API_KEY")

if not OZON_CLIENT_ID or not OZON_API_KEY:
    raise ValueError("Env variables $OZON_CLIENT_ID and $OZON_API_KEY weren't found")

headers = {
    "Client-Id": OZON_CLIENT_ID,
    "Api-Key": OZON_API_KEY,
}

attributes_ids = {
    "категория": 9461,
    "артикул продавца": 9024,
    "родительская категория": 22387,
    "name": 4180,
    "description": 4191,
}


ALL_COMMISSIONS = {
    "acquiring": "Максимальная комиссия за эквайринг",
    "fbo_fulfillment_amount": "Комиссия за сборку заказа (FBO)",
    "fbo_direct_flow_trans_min_amount": "Магистраль от (FBO)",
    "fbo_direct_flow_trans_max_amount": "Магистраль до (FBO)",
    "fbo_deliv_to_customer_amount": "Последняя миля (FBO)",
    "fbo_return_flow_amount": "Комиссия за возврат и отмену (FBO)",
    "fbo_return_flow_trans_min_amount": "Комиссия за обратную логистику от (FBO)",
    "fbo_return_flow_trans_max_amount": "Комиссия за обратную логистику до (FBO)",
    "fbs_first_mile_min_amount": "Минимальная комиссия за обработку отправления (FBS) — 0 рублей",
    "fbs_first_mile_max_amount": "Максимальная комиссия за обработку отправления (FBS) — 25 рублей",
    "fbs_direct_flow_trans_min_amount": "Магистраль от (FBS)",
    "fbs_direct_flow_trans_max_amount": "Магистраль до (FBS)",
    "fbs_deliv_to_customer_amount": "Последняя миля (FBS)",
    "fbs_return_flow_amount": "Комиссия за возврат и отмену, обработка отправления (FBS)",
    "fbs_return_flow_trans_min_amount": "Комиссия за возврат и отмену, магистраль от (FBS)",
    "fbs_return_flow_trans_max_amount": "Комиссия за возврат и отмену, магистраль до (FBS)",
    "sales_percent_fbo": "Процент комиссии за продажу (FBO)",
    "sales_percent_fbs": "Процент комиссии за продажу (FBS)",
    "sales_percent": "Наибольший процент комиссии за продажу среди FBO и FBS",
}
FBO_FIX_COMMISSIONS = {
    "acquiring": "Максимальная комиссия за эквайринг",
    "fbo_fulfillment_amount": "Комиссия за сборку заказа (FBO)",
    "fbo_direct_flow_trans_min_amount": "Магистраль от (FBO)",
    "fbo_direct_flow_trans_max_amount": "Магистраль до (FBO)",
    "fbo_deliv_to_customer_amount": "Последняя миля (FBO)",
    "fbo_return_flow_amount": "Комиссия за возврат и отмену (FBO)",
    "fbo_return_flow_trans_min_amount": "Комиссия за обратную логистику от (FBO)",
    "fbo_return_flow_trans_max_amount": "Комиссия за обратную логистику до (FBO)",
}
FBO_PERCENT_COMMISSIONS = {
    "sales_percent_fbo": "Процент комиссии за продажу (FBO)",
}
FBS_FIX_COMMISSIONS = {
    "acquiring": "Максимальная комиссия за эквайринг",
    "fbs_first_mile_min_amount": "Минимальная комиссия за обработку отправления (FBS) — 0 рублей",
    "fbs_first_mile_max_amount": "Максимальная комиссия за обработку отправления (FBS) — 25 рублей",
    "fbs_direct_flow_trans_min_amount": "Магистраль от (FBS)",
    "fbs_direct_flow_trans_max_amount": "Магистраль до (FBS)",
    "fbs_deliv_to_customer_amount": "Последняя миля (FBS)",
    "fbs_return_flow_amount": "Комиссия за возврат и отмену, обработка отправления (FBS)",
    "fbs_return_flow_trans_min_amount": "Комиссия за возврат и отмену, магистраль от (FBS)",
    "fbs_return_flow_trans_max_amount": "Комиссия за возврат и отмену, магистраль до (FBS)",
}
FBS_PERCENT_COMMISSIONS = {
    "sales_percent_fbs": "Процент комиссии за продажу (FBS)",
}
OPERATION_TYPES = {
    "MarketplaceNotDeliveredCostItem": "возврат невостребованного товара от покупателя на склад",
    "MarketplaceReturnAfterDeliveryCostItem": "возврат от покупателя на склад после доставки",
    "MarketplaceDeliveryCostItem": "доставка товара до покупателя",
    "MarketplaceSaleReviewsItem": "приобретение отзывов на платформе",
    "ItemAdvertisementForSupplierLogistic": "доставка товаров на склад Ozon : кросс-докинг",
    "MarketplaceServiceStorageItem": "размещения товаров",
    "MarketplaceMarketingActionCostItem": "продвижение товаров",
    "MarketplaceServiceItemInstallment": "продвижениe и продажа в рассрочку",
    "MarketplaceServiceItemMarkingItems": "обязательная маркировка товаров",
    "MarketplaceServiceItemFlexiblePaymentSchedule": "гибкий график выплат",
    "MarketplaceServiceItemReturnFromStock": "комплектация товаров для вывоза продавцом",
    "ItemAdvertisementForSupplierLogisticSeller": "транспортно-экспедиционные услуги",
    "MarketplaceServiceItemDelivToCustomer": "последняя миля",
    "MarketplaceServiceItemDirectFlowTrans": "магистраль",
    "MarketplaceServiceItemDropoffFF": "обработка отправления",
    "MarketplaceServiceItemDropoffPVZ": "обработка отправления",
    "MarketplaceServiceItemDropoffSC": "обработка отправления",
    "MarketplaceServiceItemFulfillment": "сборка заказа",
    "MarketplaceServiceItemPickup": "выезд транспортного средства по адресу продавца для забора отправлений : Pick-up",
    "MarketplaceServiceItemReturnAfterDelivToCustomer": "обработка возврата",
    "MarketplaceServiceItemReturnFlowTrans": "обратная магистраль",
    "MarketplaceServiceItemReturnNotDelivToCustomer": "обработка отмен",
    "MarketplaceServiceItemReturnPartGoodsCustomer": "обработка невыкупа",
    "MarketplaceRedistributionOfAcquiringOperation": "оплата эквайринга",
    "MarketplaceReturnStorageServiceAtThePickupPointFbsItem": "краткосрочное размещение возврата FBS",
    "MarketplaceReturnStorageServiceInTheWarehouseFbsItem": "долгосрочное размещение возврата FBS",
    "MarketplaceServiceItemDeliveryKGT": "доставка крупногабаритного товара (КГТ)",
    "MarketplaceServiceItemDirectFlowLogistic": "логистика",
    "MarketplaceServiceItemReturnFlowLogistic": "обратная логистика",
    "MarketplaceServicePremiumCashbackIndividualPoints": "услуга продвижения «Бонусы продавца»",
    "MarketplaceServicePremiumPromotion": "услуга продвижение Premium, фиксированная комиссия",
    "OperationMarketplaceWithHoldingForUndeliverableGoods": "удержание за недовложение товара",
    "MarketplaceServiceItemDropoffPPZ": "услуга drop-off в пункте приёма заказов",
}


def get_attrs_by_category_id(category_id: int) -> list:
    result = requests.post(
        "https://api-seller.ozon.ru/v3/category/attribute",
        headers=headers,
        data=json.dumps(
            {
                "category_id": [category_id],
            }
        ),
    ).json()["result"]
    return result


def write_headers_to_csv(file_path: str, fieldnames: list):
    with open(file_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()


def calculate_product_dimensions(product: dict) -> dict:
    dimension_unit = product["dimension_unit"]
    prod_length = product["depth"]
    prod_width = product["width"]
    prod_height = product["height"]

    if dimension_unit == "mm":
        prod_length /= 100
        prod_width /= 100
        prod_height /= 100
    elif dimension_unit == "cm":
        prod_length /= 10
        prod_width /= 10
        prod_height /= 10
    elif dimension_unit == "in":
        prod_length = round(prod_length / 3.937, 1)
        prod_width = round(prod_width / 3.937, 1)
        prod_height = round(prod_height / 3.937, 1)

    return {"length": prod_length, "width": prod_width, "height": prod_height}


def calculate_product_weight_in_kg(product: dict) -> float:
    weight_unit = product["weight_unit"]
    prod_weight = product["weight"]

    if weight_unit == "g":
        prod_weight = round(prod_weight / 1000, 2)
    else:
        raise Exception("Неизвестная мера веса")

    return prod_weight


def get_product(limit=1000, last_id="") -> dict:
    result = requests.post(
        "https://api-seller.ozon.ru/v2/product/list",
        headers=headers,
        data=json.dumps(
            {
                "filter": {},
                "last_id": last_id,
                "limit": limit,
            }
        ),
    ).json()["result"]

    return result["items"], result["last_id"]


def get_product_id(products: list) -> list:
    return [item["product_id"] for item in products]


def get_product_info(product_id: int):
    result = requests.post(
        "https://api-seller.ozon.ru/v2/product/info",
        headers=headers,
        data=json.dumps({"product_id": product_id}),
    ).json()["result"]

    return result


def get_product_info_list_by_sku(sku_list: list):
    result = requests.post(
        "https://api-seller.ozon.ru/v2/product/info/list",
        headers=headers,
        data=json.dumps({"sku": sku_list}),
    ).json()
    return result["result"]["items"]


def get_product_info_list_by_product_id(product_id_list: list):
    result = requests.post(
        "https://api-seller.ozon.ru/v2/product/info/list",
        headers=headers,
        data=json.dumps({"product_id": product_id_list}),
    ).json()
    return result["result"]["items"]


def get_product_sku_from_product_info_list(product_info_list: list) -> dict:
    """Returns dict:
    {
        prod_id_1: sku_1,
        ...
        prod_id_n: {
            'fbs': sku_n_1,
            'fbo': sku_n_2
        }
    }
    """
    sku = {}
    for item in product_info_list:
        if item["sku"] != 0:
            sku[item["id"]] = item["sku"]
        else:
            multiple_skus = {}
            for i in item["sources"]:
                multiple_skus[i["source"]] = i["sku"]
            sku[item["id"]] = multiple_skus
    return sku


def get_product_attributes(product_ids: list, limit=1000) -> list:
    response = requests.post(
        "https://api-seller.ozon.ru/v3/products/info/attributes",
        headers=headers,
        data=json.dumps(
            {
                "filter": {"product_id": [str(prod_id) for prod_id in product_ids]},
                "limit": limit,
            }
        ),
    )
    return response.json()["result"]


def get_price_objects(product_ids: list, limit=1000):
    result = requests.post(
        "https://api-seller.ozon.ru/v4/product/info/prices",
        headers=headers,
        data=json.dumps(
            {
                "filter": {
                    "product_id": [str(prod_id) for prod_id in product_ids],
                },
                "limit": limit,
            }
        ),
    ).json()

    return result["result"]["items"]


def get_product_prices(product_ids: list, limit=1000):
    """Returns a dict {product_id: prices_info}"""
    result = get_price_objects(product_ids, limit)
    product_price_info = {}
    for item in result:
        product_price_info[item["product_id"]] = item
    return product_price_info


def get_product_trading_schemes(product_ids: list, limit=1000) -> dict:
    result = requests.post(
        "https://api-seller.ozon.ru/v3/product/info/stocks",
        headers=headers,
        data=json.dumps(
            {
                "filter": {
                    "product_id": [str(prod_id) for prod_id in product_ids],
                },
                "limit": limit,
            }
        ),
    ).json()["result"]["items"]
    products_trading_schemes = {}
    for item in result:
        stocks = item["stocks"]
        trading_schemes = [
            stock["type"].upper()
            for stock in stocks
            if stock["present"] != 0 and stock["type"] in ["fbs", "fbo"]
        ]
        products_trading_schemes[item["product_id"]] = (
            trading_schemes if trading_schemes else [""]
        )

    return products_trading_schemes


def get_product_commissions(product_ids: list, limit=1):
    result = get_price_objects(product_ids, limit)

    product_comissions = {}
    for item in result:
        product_comissions[item["product_id"]] = {
            "acquiring": item["acquiring"],
            **item["commissions"],
        }
    return product_comissions


def import_comissions_by_categories_from_ozon_api_to_file(file_path: str):
    fieldnames = [
        "commission_name",
        "category_name",
        "trading_scheme",
        "value",
        "commission_type",
    ]
    write_headers_to_csv(file_path, fieldnames)
    limit = 1000
    last_id = ""
    products = ["" for _ in range(limit)]
    structure = {}

    while len(products) == limit:
        products, last_id = get_product(limit=limit, last_id=last_id)
        prod_ids = get_product_id(products)
        products_attrs = get_product_attributes(prod_ids, limit=limit)
        commissions_rows = []
        for prod in products_attrs:
            product_id = prod["id"]
            attrs = prod["attributes"]
            for a in attrs:
                if a["attribute_id"] == 9461:
                    category_name = a["values"][0]["value"]

            if structure.get(category_name):
                continue
            else:
                structure[category_name] = True

            prod_info = get_product_info(product_id)

            for com in prod_info["commissions"]:
                if com["sale_schema"] == "fbo":
                    com_name = "Процент комиссии за продажу (FBO)"
                    trad_scheme = "FBO"
                elif com["sale_schema"] == "fbs":
                    com_name = "Процент комиссии за продажу (FBS)"
                    trad_scheme = "FBS"
                elif com["sale_schema"] == "rfbs":
                    com_name = "Процент комиссии за продажу (rFBS)"
                    trad_scheme = "rFBS"
                percent = com["percent"]

                row = {
                    "category_name": category_name,
                    "commission_name": com_name,
                    "trading_scheme": trad_scheme,
                    "value": percent,
                    "commission_type": "percent",
                }
                commissions_rows.append(row)

        with open(file_path, "a", newline="") as csvfile:
            for row in commissions_rows:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writerow(row)

    return


def get_transactions(
    date_from: str = "2023-11-01T00:00:00.000Z",
    date_to: str = "2023-12-01T00:00:00.000Z",
    page=1,
    page_size=1000,
):
    result = requests.post(
        "https://api-seller.ozon.ru/v3/finance/transaction/list",
        headers=headers,
        data=json.dumps(
            {
                "filter": {
                    "date": {
                        "from": date_from,
                        "to": date_to,
                    },
                    "transaction_type": "all",
                },
                "page": page,
                "page_size": page_size,
            }
        ),
    ).json()

    message = result.get("message")
    if message:
        raise Exception(message)

    result = result["result"]
    page_count = result["page_count"]
    operations = result["operations"]
    next_page = page + 1
    if next_page <= page_count:
        return operations, next_page
    else:
        return operations, None


def import_transactions_from_ozon_api_to_file(
    file_path: str, date_from: str, date_to: str, next_page=1
):
    fieldnames = [
        "transaction_id",
        "transaction_date",
        "order_date",
        "name",
        "amount",
        "product_ids_on_platform",
        "services",
        "posting_number",
    ]
    if not os.path.isfile(file_path):
        write_headers_to_csv(file_path, fieldnames)

    page_size = 1000
    operations = ["" for _ in range(page_size)]
    while len(operations) == page_size:
        print(next_page)
        try:
            operations, next_page = get_transactions(
                page=next_page,
                page_size=page_size,
                date_from=date_from,
                date_to=date_to,
            )
        except Exception as e:
            print(e)
            return next_page

        operations_rows = []
        for oper in operations:
            transaction_id = oper["operation_id"]
            transaction_date = oper["operation_date"]
            order_date = oper["posting"]["order_date"]
            name = oper["operation_type_name"]
            amount = oper["amount"]
            product_skus = [i["sku"] for i in oper["items"]]

            services = []
            for service in oper["services"]:
                sn = OPERATION_TYPES.get(service["name"])
                service_name = sn if sn else service["name"]
                service_price = service["price"]
                services.append((service_name, service_price))

            posting_number = oper["posting"]["posting_number"]
            row = {
                "transaction_id": transaction_id,
                "transaction_date": transaction_date,
                "order_date": order_date if order_date else transaction_date,
                "name": name,
                "amount": amount,
                "product_ids_on_platform": product_skus,
                "services": services,
                "posting_number": posting_number,
            }
            operations_rows.append(row)
            print(f'Transaction {oper["operation_id"]} was imported')

        with open(file_path, "a", newline="") as csvfile:
            for row in operations_rows:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writerow(row)

    return "Successfully imported all transactions!"


def convert_datetime_str_to_ozon_date(datetime_str: str):
    return datetime_str.replace(" ", "T") + "Z"


def get_image_urls_from_product_info_list(product_info_list: list) -> dict:
    """Returns dict:
    {
        prod_id_1: [img1_url, ...],
        ...
        }
    }
    """
    images = {}
    for item in product_info_list:
        prod_id = item["id"]
        if item["primary_image"]:
            images[prod_id] = [item["primary_image"]]
        if item["images"]:
            images[prod_id].extend(
                url for url in item["images"] if url != item["primary_image"]
            )
    return images


def import_products_from_ozon_api_to_file(file_path: str):
    fieldnames = [
        "categories",
        "id_on_platform",
        "full_categories",
        "name",
        "description",
        "keywords",
        "product_id",
        "length",
        "width",
        "height",
        "weight",
        "seller_name",
        "trading_scheme",
        "price",
        "old_price",
        *list(ALL_COMMISSIONS.keys()),
        "img_urls",
    ]
    write_headers_to_csv(file_path, fieldnames)
    limit = 1000
    last_id = ""
    products = ["" for _ in range(limit)]
    sku_added = {}
    while len(products) == limit:
        products, last_id = get_product(limit=limit, last_id=last_id)
        prod_ids = get_product_id(products)
        products_attrs = get_product_attributes(prod_ids, limit=limit)
        products_trading_schemes = get_product_trading_schemes(prod_ids, limit=limit)
        products_price_info = get_product_prices(prod_ids, limit=limit)
        products_commissions = get_product_commissions(prod_ids, limit=limit)

        prod_info_list = get_product_info_list_by_product_id(prod_ids)
        products_imgs_urls = get_image_urls_from_product_info_list(prod_info_list)
        products_skus = get_product_sku_from_product_info_list(prod_info_list)

        products_rows = []
        for i, prod in enumerate(products_attrs):
            prod_id = prod["id"]
            attrs = prod["attributes"]
            for a in attrs:
                if a["attribute_id"] == 9461:
                    category_name = a["values"][0]["value"]
                if a["attribute_id"] == 22387:
                    parent_category = a["values"][0]["value"]
                if a["attribute_id"] == 4191:
                    description = a["values"][0]["value"]
                if a["attribute_id"] == 22336:
                    keywords = a["values"][0]["value"]

            id_on_platform = prod_id
            product_id = prod["offer_id"]
            name = prod["name"]
            dimensions = calculate_product_dimensions(prod)
            weight = calculate_product_weight_in_kg(prod)
            _price_info = products_price_info[id_on_platform]
            price = _price_info["price"]["price"]
            old_price = _price_info["price"]["old_price"]
            trading_schemes = products_trading_schemes[id_on_platform]
            commissions = products_commissions[id_on_platform]
            sku = products_skus[prod_id]
            imgs_urls = products_imgs_urls[prod_id]

            for trad_scheme in trading_schemes:
                row = {
                    "categories": category_name,
                    "full_categories": parent_category,
                    "name": name,
                    "description": description,
                    "keywords": keywords,
                    "product_id": product_id,
                    "length": dimensions["length"],
                    "width": dimensions["width"],
                    "height": dimensions["height"],
                    "weight": weight,
                    "seller_name": "Продавец",
                    "price": price,
                    "old_price": old_price,
                    **commissions,
                    "img_urls": imgs_urls,
                }

                if isinstance(sku, dict):
                    new_row = {}
                    for tr_scheme, sku_number in sku.items():
                        if sku_added.get(sku_number):
                            continue
                        new_row = {
                            "id_on_platform": sku_number,
                            "trading_scheme": tr_scheme.upper(),
                            **row,
                        }
                        products_rows.append(new_row)
                        print(f"Product {sku_number} was imported")
                        sku_added[sku_number] = True

                    continue

                if sku_added.get(sku):
                    continue
                row["id_on_platform"] = sku
                row["trading_scheme"] = (
                    trad_scheme if trad_scheme == "" else ", ".join(trading_schemes)
                )
                products_rows.append(row)
                print(f"Product {sku} was imported")
                sku_added[sku] = True

        with open(file_path, "a", newline="") as csvfile:
            for prod in products_rows:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writerow(prod)

    return


def get_product_stocks(product_ids: list, limit=1000) -> dict:
    """Returns dict:
    {
        <prod_id>: {
            'fbs': int,
            'fbo': int,
        },
        ...
    }
    """
    result = requests.post(
        "https://api-seller.ozon.ru/v3/product/info/stocks",
        headers=headers,
        data=json.dumps(
            {
                "filter": {
                    "product_id": [str(prod_id) for prod_id in product_ids],
                },
                "limit": limit,
            }
        ),
    ).json()["result"]["items"]
    stocks = {}
    for prod in result:
        prod_id = prod["product_id"]

        prod_stocks = {}
        for stock in prod["stocks"]:
            scheme = stock["type"]
            present_stocks = stock["present"]
            prod_stocks[scheme] = present_stocks

        stocks[prod_id] = prod_stocks

    return stocks


def import_stocks_from_ozon_api_to_file(file_path: str):
    fieldnames = [
        "product_id",
        "id_on_platform",
        "stocks_fbs",
        "stocks_fbo",
    ]
    write_headers_to_csv(file_path, fieldnames)
    limit = 1000
    last_id = ""
    products = ["" for _ in range(limit)]
    while len(products) == limit:
        products, last_id = get_product(limit=limit, last_id=last_id)
        prod_ids = get_product_id(products)
        prod_info_list = get_product_info_list_by_product_id(prod_ids)
        products_skus = get_product_sku_from_product_info_list(prod_info_list)
        stocks = get_product_stocks(product_ids=prod_ids, limit=limit)
        stocks_rows = []

        for prod_id in prod_ids:
            row = {"product_id": prod_id, "stocks_fbs": 0, "stocks_fbo": 0}
            sku = products_skus[prod_id]
            if isinstance(sku, dict):
                for tr_scheme, sku_number in sku.items():
                    new_row = {"product_id": prod_id, "stocks_fbs": 0, "stocks_fbo": 0}
                    new_row["id_on_platform"] = sku_number
                    stock = stocks[prod_id][tr_scheme]
                    if tr_scheme == "fbs":
                        new_row["stocks_fbs"] = stock
                    elif tr_scheme == "fbo":
                        new_row["stocks_fbo"] = stock

                    stocks_rows.append(new_row)
                    print(f"Product {sku_number} stocks were imported")
            else:
                row["id_on_platform"] = sku
                stock = stocks[prod_id]
                row["stocks_fbs"] = stock["fbs"]
                row["stocks_fbo"] = stock["fbo"]
                stocks_rows.append(row)
                print(f"Product {sku} stocks were imported")

        with open(file_path, "a", newline="") as csvfile:
            for prod in stocks_rows:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writerow(prod)

    return


def import_prices_from_ozon_api_to_file(file_path: str):
    fieldnames = [
        "id_on_platform",
        "price",
        "old_price",
        "ext_comp_min_price",
        "ozon_comp_min_price",
        "self_marketplaces_min_price",
        "price_index",
    ]
    write_headers_to_csv(file_path, fieldnames)
    limit = 1000
    last_id = ""
    products = ["" for _ in range(limit)]
    while len(products) == limit:
        products, last_id = get_product(limit=limit, last_id=last_id)
        prod_ids = get_product_id(products)
        prod_info_list = get_product_info_list_by_product_id(prod_ids)
        products_skus = get_product_sku_from_product_info_list(prod_info_list)
        products_price_info = get_product_prices(prod_ids, limit=limit)
        prices_rows = []
        for prod_id in prod_ids:
            _price_info = products_price_info[prod_id]
            price = _price_info["price"]["price"]
            old_price = _price_info["price"]["old_price"]
            ext_comp_min_price = _price_info["price_indexes"]["external_index_data"][
                "minimal_price"
            ]
            ozon_comp_min_price = _price_info["price_indexes"]["ozon_index_data"][
                "minimal_price"
            ]
            self_marketplaces_min_price = _price_info["price_indexes"][
                "self_marketplaces_index_data"
            ]["minimal_price"]
            price_index = _price_info["price_indexes"]["price_index"]

            row = {
                "price": price,
                "old_price": old_price,
                "ext_comp_min_price": ext_comp_min_price,
                "ozon_comp_min_price": ozon_comp_min_price,
                "self_marketplaces_min_price": self_marketplaces_min_price,
                "price_index": price_index,
            }
            sku = products_skus[prod_id]
            if isinstance(sku, dict):
                for tr_scheme, sku_number in sku.items():
                    new_row = copy.deepcopy(row)
                    new_row["id_on_platform"] = sku_number
                    prices_rows.append(new_row)
                    print(f"Product {sku_number} prices were imported")
            else:
                row["id_on_platform"] = sku
                prices_rows.append(row)
                print(f"Product {sku} prices were imported")

        with open(file_path, "a", newline="") as csvfile:
            for prod in prices_rows:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writerow(prod)

    return


# Отправления
def get_postings_fbo(date_from: str, date_to: str, limit=1000, offset=0):
    """
    Возвращает список отправлений FBO за указанный период времени.
    Если период больше года, вернётся ошибка PERIOD_IS_TOO_LONG.
    """
    response = requests.post(
        "https://api-seller.ozon.ru/v2/posting/fbo/list",
        headers=headers,
        data=json.dumps(
            {
                "dir": "ASC",
                "filter": {
                    "since": date_from,
                    "status": "",
                    "to": date_to,
                },
                "limit": limit,
                "offset": offset,
                "with": {"analytics_data": True, "financial_data": True},
            }
        ),
    ).json()
    result = response["result"]
    return result


def get_postings_fbs(date_from: str, date_to: str, limit=1000, offset=0):
    """
    Возвращает список отправлений FBS за указанный период времени (не больше 1 года)
    """
    response = requests.post(
        "https://api-seller.ozon.ru/v3/posting/fbs/list",
        headers=headers,
        data=json.dumps(
            {
                "dir": "ASC",
                "filter": {
                    "since": date_from,
                    "status": "",
                    "to": date_to,
                },
                "limit": limit,
                "offset": offset,
                "with": {
                    "analytics_data": True,
                    "barcodes": True,
                    "financial_data": True,
                    "translit": True,
                },
            }
        ),
    ).json()
    result = response["result"]["postings"]
    return result


def import_postings_from_ozon_api_to_file(
    file_path: str,
    date_from: str,
    date_to: str,
):
    """Import postings for both trading schemes FBS and FBO into csv file to upload in ozon.posting model"""
    fieldnames = [
        "in_process_at",
        "trading_scheme",
        "posting_number",
        "order_id",
        "status",
        "skus",
        "region",
        "city",
        "warehouse_id",
        "warehouse_name",
        "cluster_from",
        "cluster_to",
    ]
    write_headers_to_csv(file_path, fieldnames)
    limit = 1000
    offset = 0
    while True:
        postings_fbo = get_postings_fbo(
            date_from=date_from, date_to=date_to, limit=limit, offset=offset
        )
        postings_fbs = get_postings_fbs(
            date_from=date_from, date_to=date_to, limit=limit, offset=offset
        )

        if len(postings_fbo) == 0 and len(postings_fbs) == 0:
            break
        offset += 1000

        postings_rows = []
        for posting in postings_fbo + postings_fbs:
            in_process_at = posting["in_process_at"]
            trading_scheme = "FBS" if posting.get("delivery_method") else "FBO"
            posting_number = posting["posting_number"]
            order_id = posting["order_id"]
            status = posting["status"]
            # TODO: какие статусы брать?
            if status not in ["delivered", "cancelled"]:
                continue
            skus = [i["sku"] for i in posting["products"]]
            region = posting["analytics_data"]["region"]
            city = posting["analytics_data"]["city"]
            warehouse_id = posting["analytics_data"]["warehouse_id"]
            if trading_scheme == "FBS":
                warehouse_name = posting["analytics_data"]["warehouse"]
            else:
                warehouse_name = posting["analytics_data"]["warehouse_name"]
            cluster_from = posting["financial_data"]["cluster_from"]
            cluster_to = posting["financial_data"]["cluster_to"]
            row = {
                "in_process_at": in_process_at,
                "trading_scheme": trading_scheme,
                "posting_number": posting_number,
                "order_id": order_id,
                "status": status,
                "skus": skus,
                "region": region,
                "city": city,
                "warehouse_id": warehouse_id,
                "warehouse_name": warehouse_name,
                "cluster_from": cluster_from,
                "cluster_to": cluster_to,
            }
            postings_rows.append(row)

        with open(file_path, "a", newline="") as csvfile:
            for row in postings_rows:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writerow(row)

    return "Successfully imported all postings!"


# Поставки FBO
def get_fbo_supply_orders(page=1):
    """Возвращает список завершенных заявок на поставку на склад Ozon (FBO)"""
    response = requests.post(
        "https://api-seller.ozon.ru/v1/supply-order/list",
        headers=headers,
        data=json.dumps({"page": page, "page_size": 100, "states": ["COMPLETED"]}),
    ).json()
    return response["supply_orders"], response["has_next"]


def get_fbo_supply_order_products(supply_order_id: int, page=1):
    """Возвращает список товаров и их кол-ва в заявке на поставку на склад Ozon (FBO)"""
    response = requests.post(
        "https://api-seller.ozon.ru/v1/supply-order/items",
        headers=headers,
        data=json.dumps(
            {"page": page, "page_size": 100, "supply_order_id": supply_order_id}
        ),
    ).json()
    products = [{"sku": i["sku"], "qty": i["quantity"]} for i in response["items"]]

    return products, response["has_next"]


def import_fbo_supply_orders_from_ozon_api_to_file(file_path: str):
    """Import postings for both trading schemes FBS and FBO into csv file to upload in ozon.posting model"""
    fieldnames = [
        "supply_order_id",
        "created_at",
        "supply_date",
        "total_items_count",
        "total_quantity",
        "warehouse_id",
        "warehouse_name",
        "items",
    ]
    write_headers_to_csv(file_path, fieldnames)
    supply_orders = []
    has_next = True
    page = 1
    while has_next:
        s_orders, has_next = get_fbo_supply_orders(page=page)
        supply_orders.extend(s_orders)
        page += 1

    supply_orders_rows = []
    for order in supply_orders:
        order_id = order["supply_order_id"]
        has_next = True
        page = 1
        order_products = []
        while has_next:
            products, has_next = get_fbo_supply_order_products(
                supply_order_id=order_id, page=page
            )
            order_products.extend(products)
            page += 1

        supply_date = None
        if timeslot := order.get("local_timeslot"):
            supply_date = timeslot["from"]
        row = {
            "supply_order_id": order_id,
            "created_at": order["created_at"],
            "supply_date": supply_date,
            "total_items_count": order["total_items_count"],
            "total_quantity": order["total_quantity"],
            "warehouse_id": order["supply_warehouse"]["warehouse_id"],
            "warehouse_name": order["supply_warehouse"]["name"],
            "items": order_products,
        }
        supply_orders_rows.append(row)

    with open(file_path, "a", newline="") as csvfile:
        for row in supply_orders_rows:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writerow(row)

    return "Successfully imported all FBO supply orders!"
