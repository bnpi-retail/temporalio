from datetime import timedelta

from temporalio import workflow
from temporalio.common import RetryPolicy


with workflow.unsafe.imports_passed_through():
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
    )


@workflow.defn
class OzonProductsWorkflow:
    @workflow.run
    async def run(self) -> None:

        start_to_close_timeout = 2

        await workflow.execute_activity(
            activity_import_products,
            start_to_close_timeout=timedelta(days=start_to_close_timeout),
            retry_policy=RetryPolicy(maximum_interval=timedelta(days=24)),
        )

        await workflow.execute_activity(
            activity_write_products_to_odoo,
            start_to_close_timeout=timedelta(days=start_to_close_timeout),
            retry_policy=RetryPolicy(maximum_interval=timedelta(days=24)),
        )

        await workflow.execute_activity(
            activity_remove_csv_files,
            start_to_close_timeout=timedelta(days=start_to_close_timeout),
            retry_policy=RetryPolicy(maximum_interval=timedelta(hours=24)),
        )


@workflow.defn
class OzonFboSupplyOrdersWorkflow:
    @workflow.run
    async def run(self) -> None:

        start_to_close_timeout = 2

        await workflow.execute_activity(
            activity_import_fbo_supply_orders,
            start_to_close_timeout=timedelta(days=start_to_close_timeout),
            retry_policy=RetryPolicy(maximum_interval=timedelta(days=24)),
        )

        await workflow.execute_activity(
            activity_write_fbo_supply_orders_to_odoo,
            start_to_close_timeout=timedelta(days=start_to_close_timeout),
            retry_policy=RetryPolicy(maximum_interval=timedelta(days=24)),
        )

        await workflow.execute_activity(
            activity_remove_csv_files,
            start_to_close_timeout=timedelta(days=start_to_close_timeout),
            retry_policy=RetryPolicy(maximum_interval=timedelta(hours=24)),
        )


@workflow.defn
class OzonTransactionsWorkflow:
    @workflow.run
    async def run(self) -> None:

        start_to_close_timeout = 2

        await workflow.execute_activity(
            activity_import_transactions,
            start_to_close_timeout=timedelta(days=start_to_close_timeout),
            retry_policy=RetryPolicy(maximum_interval=timedelta(hours=24)),
        )

        await workflow.execute_activity(
            activity_write_transactions_to_odoo,
            start_to_close_timeout=timedelta(days=start_to_close_timeout),
            retry_policy=RetryPolicy(maximum_interval=timedelta(hours=24)),
        )

        await workflow.execute_activity(
            activity_remove_csv_files,
            start_to_close_timeout=timedelta(days=start_to_close_timeout),
            retry_policy=RetryPolicy(maximum_interval=timedelta(hours=24)),
        )

@workflow.defn
class OzonStocksWorkflow:
    @workflow.run
    async def run(self) -> None:

        start_to_close_timeout = 2

        await workflow.execute_activity(
            activity_import_stocks,
            start_to_close_timeout=timedelta(days=start_to_close_timeout),
            retry_policy=RetryPolicy(maximum_interval=timedelta(hours=24)),
        )

        await workflow.execute_activity(
            activity_write_stocks_to_odoo,
            start_to_close_timeout=timedelta(days=start_to_close_timeout),
            retry_policy=RetryPolicy(maximum_interval=timedelta(hours=24)),
        )

        await workflow.execute_activity(
            activity_remove_csv_files,
            start_to_close_timeout=timedelta(days=start_to_close_timeout),
            retry_policy=RetryPolicy(maximum_interval=timedelta(hours=24)),
        )


@workflow.defn
class OzonPostingsWorkflow:
    @workflow.run
    async def run(self) -> None:

        start_to_close_timeout = 2

        await workflow.execute_activity(
            activity_import_postings,
            start_to_close_timeout=timedelta(days=start_to_close_timeout),
            retry_policy=RetryPolicy(maximum_interval=timedelta(hours=24)),
        )

        await workflow.execute_activity(
            activity_write_postings_to_odoo,
            start_to_close_timeout=timedelta(days=start_to_close_timeout),
            retry_policy=RetryPolicy(maximum_interval=timedelta(hours=24)),
        )

        await workflow.execute_activity(
            activity_remove_csv_files,
            start_to_close_timeout=timedelta(days=start_to_close_timeout),
            retry_policy=RetryPolicy(maximum_interval=timedelta(hours=24)),
        )


@workflow.defn
class OzonActionsWorkflow:
    @workflow.run
    async def run(self) -> None:

        start_to_close_timeout = 2

        await workflow.execute_activity(
            activity_import_ozon_actions,
            start_to_close_timeout=timedelta(days=start_to_close_timeout),
            retry_policy=RetryPolicy(maximum_interval=timedelta(hours=24)),
        )

        await workflow.execute_activity(
            activity_write_ozon_actions_to_odoo,
            start_to_close_timeout=timedelta(days=start_to_close_timeout),
            retry_policy=RetryPolicy(maximum_interval=timedelta(hours=24)),
        )

        await workflow.execute_activity(
            activity_remove_csv_files,
            start_to_close_timeout=timedelta(days=start_to_close_timeout),
            retry_policy=RetryPolicy(maximum_interval=timedelta(hours=24)),
        )


@workflow.defn
class OzonTasksWorkflow:
    @workflow.run
    async def run(self) -> None:

        start_to_close_timeout = 2

        await workflow.execute_activity(
            activity_create_daily_tasks,
            start_to_close_timeout=timedelta(days=start_to_close_timeout),
            retry_policy=RetryPolicy(maximum_interval=timedelta(hours=24)),
        )


@workflow.defn
class OzonPricesWorkflow:
    @workflow.run
    async def run(self) -> None:

        start_to_close_timeout = 2

        await workflow.execute_activity(
            activity_import_prices,
            start_to_close_timeout=timedelta(days=start_to_close_timeout),
            retry_policy=RetryPolicy(maximum_interval=timedelta(hours=24)),
        )

        await workflow.execute_activity(
            activity_write_prices_to_odoo,
            start_to_close_timeout=timedelta(days=start_to_close_timeout),
            retry_policy=RetryPolicy(maximum_interval=timedelta(hours=24)),
        )

        await workflow.execute_activity(
            activity_remove_csv_files,
            start_to_close_timeout=timedelta(days=start_to_close_timeout),
            retry_policy=RetryPolicy(maximum_interval=timedelta(hours=24)),
        )


@workflow.defn
class OzonComputePercentExpensesWorkflow:
    @workflow.run
    async def run(self) -> None:

        start_to_close_timeout = 2

        await workflow.execute_activity(
            activity_compute_products_percent_expenses,
            start_to_close_timeout=timedelta(days=start_to_close_timeout),
            retry_policy=RetryPolicy(maximum_interval=timedelta(hours=24)),
        )


@workflow.defn
class OzonComputeCoefsAndGroupsWorkflow:
    @workflow.run
    async def run(self) -> None:

        start_to_close_timeout = 2

        await workflow.execute_activity(
            activity_compute_products_coefs_and_groups,
            start_to_close_timeout=timedelta(days=start_to_close_timeout),
            retry_policy=RetryPolicy(maximum_interval=timedelta(hours=24)),
        )


@workflow.defn
class OzonComputeAllExpensesWorkflow:
    @workflow.run
    async def run(self) -> None:

        start_to_close_timeout = 2

        await workflow.execute_activity(
            activity_compute_products_all_expenses,
            start_to_close_timeout=timedelta(days=start_to_close_timeout),
            retry_policy=RetryPolicy(maximum_interval=timedelta(hours=24)),
        )


@workflow.defn
class OzonAnalysisWorkflow:
    @workflow.run
    async def run(self) -> None:

        start_to_close_timeout = 2

        await workflow.execute_activity(
            activity_ozon_analysis_data_activity,
            start_to_close_timeout=timedelta(days=start_to_close_timeout),
            retry_policy=RetryPolicy(maximum_interval=timedelta(hours=24)),
        )


@workflow.defn
class OzonNumberOfProductsWorkflow:
    @workflow.run
    async def run(self) -> None:

        start_to_close_timeout = 2

        await workflow.execute_activity(
            activity_get_ozon_number_of_products,
            start_to_close_timeout=timedelta(days=start_to_close_timeout),
            retry_policy=RetryPolicy(maximum_interval=timedelta(hours=24)),
        )