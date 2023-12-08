import asyncio
import traceback

from datetime import timedelta
from typing import NoReturn

from temporalio import activity, workflow
from temporalio.client import Client
from temporalio.common import RetryPolicy
from temporalio.worker import Worker


@activity.defn
async def api_1c_activity() -> NoReturn:
    from fill_db import connect_to_odoo_api_with_auth

@workflow.defn
class Workflow1C:
    @workflow.run
    async def run(self) -> None:
        await workflow.execute_activity(
            api_1c_activity,
            start_to_close_timeout=timedelta(seconds=20000),
            retry_policy=RetryPolicy(maximum_interval=timedelta(hours=24)),
        )

async def main():
    client = await Client.connect("localhost:7233")

    async with Worker(
        client,
        task_queue="1c-task-queue",
        workflows=[Workflow1C],
        activities=[api_1c_activity],
    ):

        handle = await client.start_workflow(
            Workflow1C.run,
            id="1c-workflow-id",
            task_queue="1c-task-queue",
        )

        await handle.result()


if __name__ == "__main__":
    asyncio.run(main())