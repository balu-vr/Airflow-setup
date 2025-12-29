import airflow
from airflow.models import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.utils.dates import days_ago
from datetime import datetime, timedelta
from airflow.providers.ssh.operators.ssh  import SSHOperator
from airflow.utils.task_group import TaskGroup

args = {
    "owner": "airflow",
    "provide_context": True,
    'email': ['john.doe@abccorp.com','will.smith@abccorp.com'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(seconds=30)
}
with DAG(dag_id="daily_aha_loads", schedule_interval='0 1 * * *', start_date=datetime(2022, 8, 24, 22, 15), max_active_runs=1, default_args=args, catchup=False, tags=["PROD|AHA"]) as dag:
    
    start = BashOperator(
            task_id="start",
            bash_command='exit 0'
            )
    
    with TaskGroup(group_id="details") as details:

        feature_details = SSHOperator(
                task_id="feature_details",
                ssh_conn_id='aws_etl_server',
                command='`python3.8 /home/ec2-user/deploy/aha/prod/pyscripts/aha_extract_detail.py feature_details >> /home/ec2-user/deploy/aha/prod/logs/aha_daily_load.log`',
                )

        product_details = SSHOperator(
                task_id="product_details",
                ssh_conn_id='aws_etl_server',
                command='`sleep 5;python3.8 /home/ec2-user/deploy/aha/prod/pyscripts/aha_extract_detail.py product_details >> /home/ec2-user/deploy/aha/prod/logs/aha_daily_load.log`'
                )



    with TaskGroup(group_id="jobs") as jobs:

        
        initiatives = SSHOperator(
            task_id="initiatives",
            ssh_conn_id='aws_etl_server',
            command='`python3.8 /home/ec2-user/deploy/aha/prod/pyscripts/aha_extract_base.py initiatives >> /home/ec2-user/deploy/aha/prod/logs/aha_daily_load.log`',
            )

        releases = SSHOperator(
            task_id="releases",
            ssh_conn_id='aws_etl_server',
            command='`sleep 5; python3.8 /home/ec2-user/deploy/aha/prod/pyscripts/aha_extract_base.py releases >> /home/ec2-user/deploy/aha/prod/logs/aha_daily_load.log`',
            )

        products = SSHOperator(
            task_id="products",
            ssh_conn_id='aws_etl_server',
            command='`sleep 10; python3.8 /home/ec2-user/deploy/aha/prod/pyscripts/aha_extract_base.py products >> /home/ec2-user/deploy/aha/prod/logs/aha_daily_load.log`',
            )

        features = SSHOperator(
            task_id="features",
            ssh_conn_id='aws_etl_server',
            command='`sleep 15; python3.8 /home/ec2-user/deploy/aha/prod/pyscripts/aha_extract_base.py features >> /home/ec2-user/deploy/aha/prod/logs/aha_daily_load.log`',
            )

        goals = SSHOperator(
            task_id="goals",
            ssh_conn_id='aws_etl_server',
            command='`sleep 20; python3.8 /home/ec2-user/deploy/aha/prod/pyscripts/aha_extract_base.py goals >> /home/ec2-user/deploy/aha/prod/logs/aha_daily_load.log`',
            )

        release_phases = SSHOperator(
            task_id="release_phases",
            ssh_conn_id='aws_etl_server',
            command='`sleep 25; python3.8 /home/ec2-user/deploy/aha/prod/pyscripts/aha_extract_base.py release_phases >> /home/ec2-user/deploy/aha/prod/logs/aha_daily_load.log`',
            )

        strategy_visions = SSHOperator(
            task_id="strategy_visions",
            ssh_conn_id='aws_etl_server',
            command='`sleep 30; python3.8 /home/ec2-user/deploy/aha/prod/pyscripts/aha_extract_base.py strategy_visions >> /home/ec2-user/deploy/aha/prod/logs/aha_daily_load.log`',
            )

        strategy_models = SSHOperator(
            task_id="strategy_models",
            ssh_conn_id='aws_etl_server',
            command='`sleep 35; python3.8 /home/ec2-user/deploy/aha/prod/pyscripts/aha_extract_base.py strategy_models >> /home/ec2-user/deploy/aha/prod/logs/aha_daily_load.log`',
            )

        

        start >> jobs >> details
   


