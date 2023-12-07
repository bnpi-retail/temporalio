import asyncio
import traceback

from datetime import timedelta
from typing import NoReturn

from temporalio import activity, workflow
from temporalio.client import Client
from temporalio.common import RetryPolicy
from temporalio.worker import Worker


@activity.defn
async def ozon_api_activity() -> NoReturn:
    pass
    path = './products_from_ozon_api.csv'
    from ozon_api import import_products_from_ozon_api_to_file
    import_products_from_ozon_api_to_file(path)


@activity.defn
async def fill_db_activity() -> NoReturn:
    from fill_db import connect_to_odoo_api_with_auth


@workflow.defn
class OzonWorkflow:
    @workflow.run
    async def run(self) -> None:
        await workflow.execute_activity(
            ozon_api_activity,
            start_to_close_timeout=timedelta(seconds=20000),
            retry_policy=RetryPolicy(maximum_interval=timedelta(seconds=2)),
        )

        await workflow.execute_activity(
            fill_db_activity,
            start_to_close_timeout=timedelta(seconds=20000),
            retry_policy=RetryPolicy(maximum_interval=timedelta(seconds=2)),
        )




async def main():
    client = await Client.connect("localhost:7233")

    async with Worker(
        client,
        task_queue="ozon-task-queue",
        workflows=[OzonWorkflow],
        activities=[fill_db_activity, ozon_api_activity],
    ):

        handle = await client.start_workflow(
            OzonWorkflow.run,
            id="ozon-workflow-id",
            task_queue="ozon-task-queue",
        )

        await handle.result()


if __name__ == "__main__":
    asyncio.run(main())