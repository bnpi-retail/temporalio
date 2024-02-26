import asyncio

from temporalio import workflow
from temporalio.client import Client
from temporalio.worker import Worker
from temporalio.common import RetryPolicy
from datetime import timedelta

EXECUTION_TIMEOUT = timedelta(hours=6)

with workflow.unsafe.imports_passed_through():
    from ozon_workflow import GeneralOzonWorkflow
    from workflows import (
        OzonProductsWorkflow,
        OzonFboSupplyOrdersWorkflow,
        OzonTransactionsWorkflow,
        OzonStocksWorkflow,
        OzonPostingsWorkflow,
        OzonActionsWorkflow,
        OzonComputeAllExpensesWorkflow,
        OzonComputeCoefsAndGroupsWorkflow,
        OzonComputePercentExpensesWorkflow,
        OzonTasksWorkflow,
        OzonPricesWorkflow,
        OzonAnalysisWorkflow,
        OzonNumberOfProductsWorkflow,
        CreateMassDataImportWorkflow,
    )
    from activities import (
        activity_compute_products_all_expenses,
        activity_compute_products_coefs_and_groups,
        activity_compute_products_percent_expenses,
        activity_create_daily_tasks,
        activity_import_fbo_supply_orders,
        activity_import_ozon_actions,
        activity_import_postings,
        activity_import_prices,
        activity_import_products,
        activity_import_stocks,
        activity_import_transactions,
        activity_import_transactions_from_prev_2_years,
        activity_import_transactions_from_prev_month,
        activity_remove_csv_files,
        activity_write_fbo_supply_orders_to_odoo,
        activity_write_ozon_actions_to_odoo,
        activity_write_postings_to_odoo,
        activity_write_prices_to_odoo,
        activity_write_products_to_odoo,
        activity_write_stocks_to_odoo,
        activity_write_transactions_to_odoo,
        activity_ozon_analysis_data_activity,
        activity_get_ozon_number_of_products,
        activity_create_mass_data_import
    )


async def main():
    client = await Client.connect("localhost:7233")

    task_queue = "general-ozon-task-queue"
    workflow_id = "general-ozon-workflow-id"

    async with Worker(
        client,
        task_queue=task_queue,
        workflows=[
            GeneralOzonWorkflow,
            OzonProductsWorkflow,
            OzonFboSupplyOrdersWorkflow,
            OzonTransactionsWorkflow,
            OzonStocksWorkflow,
            OzonPostingsWorkflow,
            OzonActionsWorkflow,
            OzonComputeAllExpensesWorkflow,
            OzonComputeCoefsAndGroupsWorkflow,
            OzonComputePercentExpensesWorkflow,
            OzonTasksWorkflow,
            OzonPricesWorkflow,
            OzonAnalysisWorkflow,
            OzonNumberOfProductsWorkflow,
            CreateMassDataImportWorkflow,
        ],
        activities = [
            activity_compute_products_all_expenses,
            activity_compute_products_coefs_and_groups,
            activity_compute_products_percent_expenses,
            activity_create_daily_tasks,
            activity_import_fbo_supply_orders,
            activity_import_ozon_actions,
            activity_import_postings,
            activity_import_prices,
            activity_import_products,
            activity_import_stocks,
            activity_import_transactions,
            activity_import_transactions_from_prev_2_years,
            activity_import_transactions_from_prev_month,
            activity_remove_csv_files,
            activity_write_fbo_supply_orders_to_odoo,
            activity_write_ozon_actions_to_odoo,
            activity_write_postings_to_odoo,
            activity_write_prices_to_odoo,
            activity_write_products_to_odoo,
            activity_write_stocks_to_odoo,
            activity_write_transactions_to_odoo,
            activity_ozon_analysis_data_activity,
            activity_get_ozon_number_of_products,
            activity_create_mass_data_import
        ],
    ):

        await client.execute_workflow(
            GeneralOzonWorkflow.run,
            id=workflow_id,
            task_queue=task_queue,
            execution_timeout=EXECUTION_TIMEOUT,
            retry_policy=RetryPolicy(maximum_interval=timedelta(minutes=2)),
        )


if __name__ == "__main__":
    asyncio.run(main())
