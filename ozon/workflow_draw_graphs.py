import os
import asyncio
from datetime import timedelta

from temporalio import workflow, activity
from temporalio.client import Client
from temporalio.common import RetryPolicy
from temporalio.worker import Worker

with workflow.unsafe.imports_passed_through():
    from activities import (
        activity_draw_graphs,
    )
    from sentry_interceptor import SentryInterceptor
    from dotenv import load_dotenv
    import sentry_sdk


# @activity.defn
# async def activity_create_mass_data_import() -> None:
#     await ImportLogging().create_mass_data_import({'name': 'Импорт отправлений за период', 'logged_activities_qty': 1})

EXECUTION_TIMEOUT = timedelta(hours=8)


@workflow.defn
class OzonDrawGraphsWorkflow:
    @workflow.run
    async def run(self) -> None:
        await workflow.execute_activity(
            activity_draw_graphs,
            start_to_close_timeout=timedelta(hours=6),
            retry_policy=RetryPolicy(maximum_interval=timedelta(minutes=1)),
        )


async def main():
    # Initialize the Sentry SDK
    load_dotenv()
    sentry_sdk.init(
        dsn=os.getenv("SENTRY_DSN"),
    )

    client = await Client.connect("localhost:7233")

    async with Worker(
            client,
            task_queue="ozon-task-queue-graphs",
            workflows=[OzonDrawGraphsWorkflow],
            activities=[
                activity_draw_graphs,
            ],
            interceptors=[SentryInterceptor()],  # Use SentryInterceptor for error reporting
    ):
        # handle = await client.start_workflow(
        #     OzonDrawGraphsWorkflow.run,
        #     id="ozon-workflow-draw_graph",
        #     task_queue="ozon-task-queue-graphs",
        # )
        await client.execute_workflow(
            OzonDrawGraphsWorkflow.run,
            id="ozon-workflow-draw_graph",
            task_queue="ozon-task-queue-graphs",
            execution_timeout=EXECUTION_TIMEOUT,
            retry_policy=RetryPolicy(maximum_interval=timedelta(minutes=2)),
        )

        # await handle.result()


if __name__ == "__main__":
    asyncio.run(main())
