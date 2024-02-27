import asyncio

from datetime import timedelta
from typing import NoReturn

from temporalio import activity, workflow
from temporalio.client import Client
from temporalio.common import RetryPolicy
from temporalio.worker import Worker

with workflow.unsafe.imports_passed_through():
    from price_histry_competitors_mpstats import main as price_histry_competitors_main
    from price_histry_competitors_mpstats import (
        activity_two as price_histry_competitors_activity_two,
    )
    from tools import ImportLogging, odoo_log

@activity.defn
async def activity_create_mass_data_import() -> None:
    await ImportLogging().create_mass_data_import({'name': 'MPstats импорт', 'logged_activities_qty': 1})

@activity.defn
async def mp_parsing_api_activity() -> NoReturn:
    price_histry_competitors_main()


@activity.defn
@odoo_log({'name': 'Импорт истории цен конкурентов'})
async def save_in_odoo_activity() -> dict:
    return price_histry_competitors_activity_two()


@workflow.defn
class MPStatsWorkflow:
    @workflow.run
    async def run(self) -> None:
        await workflow.execute_activity(
            activity_create_mass_data_import,
            start_to_close_timeout=timedelta(minutes=5),
            retry_policy=RetryPolicy(maximum_interval=timedelta(minutes=2)),
        )

        await workflow.execute_activity(
            mp_parsing_api_activity,
            start_to_close_timeout=timedelta(minutes=60),
            retry_policy=RetryPolicy(maximum_interval=timedelta(minutes=2)),
        )

        await workflow.execute_activity(
            save_in_odoo_activity,
            start_to_close_timeout=timedelta(minutes=60),
            retry_policy=RetryPolicy(maximum_interval=timedelta(minutes=2)),
        )


async def main():
    client = await Client.connect("localhost:7233")

    async with Worker(
        client,
        task_queue="MP-stats-task-queue",
        workflows=[MPStatsWorkflow],
        activities=[mp_parsing_api_activity, save_in_odoo_activity, activity_create_mass_data_import],
    ):
        await client.execute_workflow(
            MPStatsWorkflow.run,
            id="MPstats-workflow-id",
            task_queue="MP-stats-task-queue",
            execution_timeout=timedelta(hours=2)
        )


if __name__ == "__main__":
    asyncio.run(main())
