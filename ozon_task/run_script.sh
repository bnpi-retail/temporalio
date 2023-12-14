#!/bin/bash

source /home/sammy/tasks/temporalio/venv/bin/activate

python /home/sammy/tasks/temporalio/ozon_task/workflow_products.py
python /home/sammy/tasks/temporalio/ozon_task/workflow_transactions.py