import asyncio

from datetime import timedelta
from unittest import result

from temporalio import activity, workflow
from temporalio.client import Client
from temporalio.common import RetryPolicy
from temporalio.worker import Worker

with workflow.unsafe.imports_passed_through():
    from test import (
        get_items, send_to_odoo
    )


@workflow.defn
class GeneralWorkflow:
    @workflow.run
    async def run(self) -> None:
        for _ in range(3):

            data = await workflow.execute_activity(
                get_items, start_to_close_timeout=timedelta(seconds=5)
            )

            tasks = []
            for item in data["items"]:
                tasks.append(
                    workflow.execute_activity(
                        send_to_odoo, item, start_to_close_timeout=timedelta(seconds=5)
                    )
                )

            await asyncio.gather(*tasks)


async def main():
    client = await Client.connect("localhost:7233")

    async with Worker(
        client,
        task_queue="ozon-task-queue",
        workflows=[GeneralWorkflow],
        activities=[
            get_items,
            send_to_odoo
        ],
    ):
        handle = await client.start_workflow(
            GeneralWorkflow.run,
            id="ozon-workflow-products-id",
            task_queue="ozon-task-queue",
        )

        await handle.result()


if __name__ == "__main__":
    asyncio.run(main())
