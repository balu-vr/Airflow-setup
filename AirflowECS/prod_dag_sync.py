from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from datetime import datetime, timedelta

args = {
    "owner": "airflow",
    "provide_context": True,
    'email': [
        'user_email@org.com'
    ],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 0,
    'retry_delay': timedelta(seconds=30)
}

with DAG(
    dag_id='prod_dag_sync',
    schedule_interval='@hourly',
    start_date=datetime(2024, 10, 15),
    default_args=args,
    catchup=False,
    tags=["PROD|GIT_DAG_SYNC"]
	) as dag:

    git_clone = BashOperator(
        task_id="git_clone",
        bash_command="""
		git config --global --add safe.directory /opt/airflow/dags
        if [ ! -d /opt/airflow/dags/.git ]; then
			echo "Files not available in dag path"
		else
			echo "Pulling latest changes"
			cd /opt/airflow/dags && git pull origin main;
		fi
        """
    )

    

    git_clone 
