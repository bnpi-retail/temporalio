import asyncio
import traceback
import ast

from datetime import timedelta
from typing import NoReturn

from temporalio import activity, workflow
from temporalio.client import Client
from temporalio.common import RetryPolicy
from temporalio.worker import Worker


@activity.defn
async def ozon_api_activity() -> NoReturn:
    from price_histry_competitors import main
    main()

@activity.defn
async def save_in_odoo_activity() -> NoReturn:
    with open('data.txt', 'r') as file:
        data_content = file.read()

    data_dict = ast.literal_eval(data_content)
    print(data_dict)

    from price_histry_competitors import activity_two
    activity_two(data_dict)


@workflow.defn
class OzonWorkflow:
    @workflow.run
    async def run(self) -> None:
        await workflow.execute_activity(
            ozon_api_activity,
            start_to_close_timeout=timedelta(seconds=20000),
            retry_policy=RetryPolicy(maximum_interval=timedelta(hours=24)),
        )

        await workflow.execute_activity(
            save_in_odoo_activity,
            start_to_close_timeout=timedelta(seconds=20000),
            retry_policy=RetryPolicy(maximum_interval=timedelta(hours=24)),
        )


async def main():
    client = await Client.connect("localhost:7233")

    async with Worker(
        client,
        task_queue="ozon-task-queue",
        workflows=[OzonWorkflow],
        activities=[ozon_api_activity, save_in_odoo_activity],
    ):

        handle = await client.start_workflow(
            OzonWorkflow.run,
            id="ozon-workflow-id",
            task_queue="ozon-task-queue",
        )

        await handle.result()


if __name__ == "__main__":
    asyncio.run(main())
