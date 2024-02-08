import csv
import uuid


class ProcessFileCSV:
    def generate_files_by_limit(self, file_dir, field_names, products_rows, file_limit) -> list:
        chunks = [products_rows[i:i + file_limit] for i in range(0, len(products_rows), file_limit)]

        file_paths = []

        for chunk in chunks:
            file_path_save = self.__generate_file_path(file_dir)
            self.__write_headers_to_csv(file_path_save, field_names)
            self.__write_products_to_csv(field_names, chunk, file_path_save)
            file_paths.append(file_path_save)
        
        return file_paths

    @staticmethod
    def __write_headers_to_csv(file_path: str, field_names: list):
        with open(file_path, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=field_names)
            writer.writeheader()

    @staticmethod
    def __generate_file_path(file_dir: str) -> str:
        unique_id = uuid.uuid4()
        return f"{file_dir}{unique_id}.csv"

    @staticmethod
    def __write_products_to_csv(field_names, chunk: list, file_path_save: str):
        with open(file_path_save, "a", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=field_names)
            for product in chunk:
                writer.writerow(product)
