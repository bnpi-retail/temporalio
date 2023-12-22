#!/bin/bash

source /home/sammy/tasks/temporalio/venv/bin/activate

python /home/sammy/tasks/temporalio/ozon_task/workflow_products.py
python /home/sammy/tasks/temporalio/ozon_task/workflow_stocks.py
python /home/sammy/tasks/temporalio/ozon_task/workflow_transactions.py
python /home/sammy/tasks/temporalio/ozon_task/workflow_compute_coefs_and_groups.py
python /home/sammy/tasks/temporalio/ozon_task/workflow_percent_expenses.py