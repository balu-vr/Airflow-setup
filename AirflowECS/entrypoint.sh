#!/bin/bash

# Initialize the Airflow database
airflow db init

# Start the Airflow webserver in the background
airflow webserver &

# Start the Airflow scheduler
airflow scheduler

# Wait for all background jobs to finish
wait
