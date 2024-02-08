import requests

from ozon_api import InfoOzon
from odoo_info import InfoOdoo
from process_csv import ProcessFileCSV


class OdooMethod(InfoOdoo):
    def __init__(self):
        super().__init__()
        self.endpoint = "api/v1/get_data_for_ozon_products"

    def get_data(self) -> dict:
        url = self.odoo_base_url + self.endpoint
        headers = {"Cookie": f"session_id={self.odoo_session_id}"}
        response = requests.post(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        raise Exception(
            f"Ошибка при запросе в Odoo." + "" 
            f"Статус: {response.status_code}" + " "
            f"Текст: {response.text}"
        )


class GetProductsFromOzon(InfoOzon, ProcessFileCSV):
    def __init__(self):
        super().__init__()
        
        self.file_path = "./cache/"
        self.field_names = [
            "id_on_platform",
            "offer_id",
            "sku",
            "fbo_sku",
            "fbs_sku",
            "categories",
            "description_category_id",
            "full_categories",
            "full_categories_id",
            "name",
            "description",
            "keywords",
            "length",
            "width",
            "height",
            "weight",
            "seller_name",
            "trading_scheme",
            "price",
            "old_price",
            "ext_comp_min_price",
            "ozon_comp_min_price",
            "self_marketplaces_min_price",
            "price_index",
            *list(self.all_commission.keys()),
            "img_urls",
        ]

    def import_products_from_ozon_api_to_file(self, limit: int = 1000, file_limit: int = 1000):
        last_id, products = "", []

        all_file_paths = []

        first = True
        while len(products) == limit or first == True:
            first = False

            products, last_id = self.get_product(limit=limit, last_id=last_id)
            prod_ids = self.get_product_id(products)
            products_attrs = self.get_product_attributes(prod_ids, limit=limit)
            products_trading_schemes = self.get_product_trading_schemes(prod_ids, limit=limit)
            products_price_info = self.get_product_prices(prod_ids, limit=limit)
            products_commissions = self.get_product_commissions(prod_ids, limit=limit)
            prod_info_list = self.get_product_info_list_by_product_id(prod_ids)
            products_imgs_urls = self.get_image_urls_from_product_info_list(prod_info_list)
            products_skus = self.get_product_sku_from_product_info_list(prod_info_list)

            products_rows = []

            for prod in products_attrs:
                id_on_platform = prod["id"]
                attrs = prod["attributes"]
                for a in attrs:
                    if a["attribute_id"] == 9461:
                        category_name = a["values"][0]["value"]
                    if a["attribute_id"] == 22387:
                        parent_category = a["values"][0]["value"]
                        full_categories_id = a["values"][0]["dictionary_value_id"]
                    if a["attribute_id"] == 4191:
                        description = a["values"][0]["value"]
                    if a["attribute_id"] == 22336:
                        keywords = a["values"][0]["value"]

                description_category_id = prod["description_category_id"]
                offer_id = prod["offer_id"]
                name = prod["name"]
                dimensions = self.calculate_product_dimensions(prod)
                weight = self.calculate_product_weight_in_kg(prod)
                _price_info = products_price_info[id_on_platform]
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
                trading_scheme = products_trading_schemes[id_on_platform]
                commissions = products_commissions[id_on_platform]
                sku = products_skus[id_on_platform]["sku"]
                fbo_sku = products_skus[id_on_platform]["fbo_sku"]
                fbs_sku = products_skus[id_on_platform]["fbs_sku"]
                imgs_urls = products_imgs_urls[id_on_platform]

                row = {
                    "id_on_platform": id_on_platform,
                    "offer_id": offer_id,
                    "sku": sku,
                    "fbo_sku": fbo_sku,
                    "fbs_sku": fbs_sku,
                    "categories": category_name,
                    "description_category_id": description_category_id,
                    "full_categories": parent_category,
                    "full_categories_id": full_categories_id,
                    "name": name,
                    "description": description,
                    "keywords": keywords,
                    "length": dimensions["length"],
                    "width": dimensions["width"],
                    "height": dimensions["height"],
                    "weight": weight,
                    "seller_name": "Продавец",
                    "trading_scheme": trading_scheme,
                    "price": price,
                    "old_price": old_price,
                    "ext_comp_min_price": ext_comp_min_price,
                    "ozon_comp_min_price": ozon_comp_min_price,
                    "self_marketplaces_min_price": self_marketplaces_min_price,
                    "price_index": price_index,
                    **commissions,
                    "img_urls": imgs_urls,
                }
                products_rows.append(row)
                print(f"Product {id_on_platform} was saved")

            file_paths = self.generate_files_by_limit(
                file_dir=self.file_path,
                field_names=self.field_names,
                products_rows=products_rows,
                file_limit=file_limit
            )
            all_file_paths.extend(file_paths)

        return all_file_paths
    