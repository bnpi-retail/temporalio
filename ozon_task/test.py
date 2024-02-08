import aiohttp

from temporalio import activity


headers = {
    "Client-Id": "16713",
    "Api-Key": "de602215-8e7c-4b9f-aea4-0b4a3c333db9",
}


async def get_product(last_id, limit=1000) -> dict:
    url = "https://api-seller.ozon.ru/v2/product/list"
    payload = {"filter": {}, "last_id": last_id, "limit": limit}

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=payload) as response:
            data = await response.json()
            result = data.get("result")
            if result is None:
                raise ValueError(data)
            return result["items"], result["last_id"]


@activity.defn
async def get_items() -> dict:
    data = {
        "last_id": None,
        "items": [],
    }

    last_id = ""
    for _ in range(3):
        items, last_id = await get_product(last_id=last_id)

        data["last_id"] = last_id
        data["items"].append(items)

    return data


@activity.defn
async def send_to_odoo(item):
    print("send")