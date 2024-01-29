import asyncio
import traceback
import ast

from datetime import timedelta
from typing import NoReturn

from temporalio import activity, workflow
from temporalio.client import Client
from temporalio.common import RetryPolicy
from temporalio.worker import Worker

with workflow.unsafe.imports_passed_through():
    from price_histry_competitors import main as price_histry_competitors_main
    from price_histry_competitors import (
        activity_two as price_histry_competitors_activity_two,
    )


@activity.defn
async def mp_parsing_api_activity() -> NoReturn:
    price_histry_competitors_main()


@activity.defn
async def save_in_odoo_activity() -> NoReturn:
    price_histry_competitors_activity_two()


@workflow.defn
class MPStatsWorkflow:
    @workflow.run
    async def run(self) -> None:
        await workflow.execute_activity(
            mp_parsing_api_activity,
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
        task_queue="MP-stats-task-queue",
        workflows=[MPStatsWorkflow],
        activities=[mp_parsing_api_activity, save_in_odoo_activity],
    ):
        pass

        await client.execute_workflow(
            MPStatsWorkflow.run,
            id="MPstats-workflow-id",
            task_queue="MP-stats-task-queue",
        )


if __name__ == "__main__":
    asyncio.run(main())
