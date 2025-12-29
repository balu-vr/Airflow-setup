import airflow
from airflow.models import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.utils.dates import days_ago
from datetime import datetime, timedelta
from airflow.providers.ssh.operators.ssh  import SSHOperator
from airflow.utils.task_group import TaskGroup
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from airflow.operators.python_operator import PythonOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator

args = {
    "owner": "airflow",
    "provide_context": True,
    'email': [
        'etl_alerts@intapp.com',
        'john.doe@abccorp.com',
        'will.smith@abccorp.com'
    ],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(seconds=30)
}

def print_xcom(dag_run):
    ti = dag_run.get_task_instance("wait_for_flag")
    print("printing the flag:", ti.xcom_pull(task_ids="wait_for_flag"))


with DAG(dag_id="prod_op_main", schedule_interval='*/12 0-3,9-23 * * 1,2,3,4,5', start_date=days_ago(1), max_active_runs=1, default_args=args, catchup=False, tags=["PROD|OP"]) as dag:

    start = BashOperator(
            task_id="start",
            bash_command='exit 0'
            )

    
    check_for_fullload = SSHOperator(
                task_id="check_for_fullload",
                ssh_conn_id='aws_etl_server',
                command='`/usr/bin/python3.8 /home/ec2-user/deploy/oneplace_prod/pyscripts/OP_Incremental_Check.py Deal >> /home/ec2-user/deploy/oneplace_dev/log/op_hourly_load.log`',
                )


    #with TaskGroup("my_task_group",trigger_rule='all_success') as my_group:
    OPIncremental = SSHOperator(
                task_id="OPIncremental",
                ssh_conn_id='ETLPROD1',
                command='`sh /home/ec2-user/DataEngineering/oneplace/oneplace/py_pre_exec_dashboard_Incr.sh >> /home/ec2-user/DataEngineering/oneplace/logs/py_pre_exec_dashboard_Incr.log`',
                trigger_rule = 'all_success'
                )

    OPFullLoad = SSHOperator(
                task_id="OPFullLoad",
                ssh_conn_id='ETLPROD1',
                command='`sh /home/ec2-user/DataEngineering/oneplace/oneplace/py_pre_exec_dashboard.sh >> /home/ec2-user/DataEngineering/oneplace/logs/py_pre_exec_dashboard.log`',
                trigger_rule = 'one_failed'
                )
    tableau_dash = SSHOperator(
        task_id="tableau_db_ref",
        ssh_conn_id='aws_etl_server', #onprem_etl_server #
        #command='`sh /root/deploy/op4i/prod/py_main_exec_dashboard.sh >> /root/deploy/op4i/prod/log/py_exec_dashboard.log`',
        command='`sh /home/ec2-user/deploy/oneplace_prod/py_main_exec_dashboard.sh >> /home/ec2-user/deploy/oneplace_prod/log/py_exec_dashboard.log`',
        trigger_rule = 'one_success'
        )

    trigger_hist_dag = TriggerDagRunOperator(
        task_id="trigger_prod_op_hist",
        trigger_dag_id="prod_op_hist",
        trigger_rule='all_success'
    )

    check_for_fullload.set_upstream(start)
    OPIncremental.set_upstream(check_for_fullload)
    OPFullLoad.set_upstream(check_for_fullload)
    tableau_dash.set_upstream(OPIncremental)
    tableau_dash.set_upstream(OPFullLoad)
    trigger_hist_dag.set_upstream(tableau_dash)

    #print_xcom_op = PythonOperator(task_id='print_xcom', python_callable=print_xcom, provide_context=True, dag=dag)

