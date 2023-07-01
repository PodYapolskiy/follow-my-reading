#!/bin/sh

redis-server &
huey_consumer.py core.task_system.scheduler -n -k thread &
uvicorn main:app --host "0.0.0.0" --port 80;
fg