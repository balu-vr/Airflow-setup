import airflow
from airflow.models import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.utils.dates import days_ago
from datetime import datetime, timedelta
from airflow.providers.ssh.operators.ssh  import SSHOperator
from airflow.utils.task_group import TaskGroup
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator

args = {
    "owner": "airflow",
    "provide_context": True,
    'email': ['john.doe@abccorp.com','will.smith@abccorp.com'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(seconds=30)
}  
with DAG(dag_id="openair_loads", schedule_interval='0 12 * * 1-5', start_date=datetime(2022, 5, 6, 22, 15), default_args=args, catchup=False, tags=["PROD|OPENAIR"]) as dag:
    
    start = BashOperator(
            task_id="start",
            bash_command='exit 0'
            )

    BookingsByDay = SSHOperator(
            task_id="BookingsByDay",
            ssh_conn_id='aws_etl_server',
            command='`cd /home/ec2-user/deploy/oair/prod; python3.8 oa_pipeline_v2.py bookingbyday update >> /home/ec2-user/deploy/oair/prod/logs/oair_loads.log`',
            )
    
    Contact = SSHOperator(
            task_id="Contact",
            ssh_conn_id='aws_etl_server',
            command='`cd /home/ec2-user/deploy/oair/prod; python3.8 oa_pipeline_v2.py contact update >> /home/ec2-user/deploy/oair/prod/logs/oair_loads.log`',
            )
 
    Department = SSHOperator(
            task_id="Department",
            ssh_conn_id='aws_etl_server',
            command='`cd /home/ec2-user/deploy/oair/prod; python3.8 oa_pipeline_v2.py department update >> /home/ec2-user/deploy/oair/prod/logs/oair_loads.log`',
            )
 
    start >> BookingsByDay >> Contact >> Department
   



