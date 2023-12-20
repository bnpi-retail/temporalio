import asyncio

from datetime import timedelta

from temporalio import activity, workflow
from temporalio.client import Client
from temporalio.common import RetryPolicy
from temporalio.worker import Worker


with workflow.unsafe.imports_passed_through():
    from activities import activity_compute_products_coefs_and_groups


@workflow.defn
class OzonComputeWorkflow:
    @workflow.run
    async def run(self) -> None:
        await workflow.execute_activity(
            activity_compute_products_coefs_and_groups,
            start_to_close_timeout=timedelta(seconds=20000),
            retry_policy=RetryPolicy(maximum_interval=timedelta(hours=24)),
        )


async def main():
    client = await Client.connect("localhost:7233")

    async with Worker(
        client,
        task_queue="ozon-task-queue",
        workflows=[OzonComputeWorkflow],
        activities=[
            activity_compute_products_coefs_and_groups,
        ],
    ):
        handle = await client.start_workflow(
            OzonComputeWorkflow.run,
            id="ozon-compute-workflow-id",
            task_queue="ozon-task-queue",
        )

        await handle.result()


if __name__ == "__main__":
    asyncio.run(main())
