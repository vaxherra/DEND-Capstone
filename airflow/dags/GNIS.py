from airflow import DAG
from operators.Src2S3 import Src2S3
from operators.S32Redshift import S32Redshift
from datetime import datetime, timedelta
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.bash_operator import BashOperator
from airflow.operators.postgres_operator import PostgresOperator
from airflow.operators.python_operator import PythonOperator

from airflow.contrib.hooks.aws_hook import AwsHook
from airflow.hooks.postgres_hook import PostgresHook

import wget
import pytz

from sql_statements import sql_statements

##########################################################################
 
# Default parameters
default_args = {
    'owner': 'Robert Kwapich',
    'start_date': datetime(2020, 3, 29),
    'end_date': datetime(2020, 4, 30),
    'depends_on_past': False, # no need to run sequentially in time for GDELT data, can parallelize tasks
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
    'catchup': False, 
    'email_on_retry': False
}


dag = DAG(
    dag_id='gnis_dataset',
    default_args=default_args,
    schedule_interval= "@once", #  once, and only once
    dagrun_timeout=timedelta(minutes=60), # how long a DagRun should be up before timing out / failing,
    tags=['gnis_dataset'],
    max_active_runs=1
)


#############################################
######### DEFINE A SET OF ETL TASKS #########
#############################################

start_operator = DummyOperator(task_id='Begin_execution',  dag=dag)







end_operator = DummyOperator(task_id='End_execution',  dag=dag)



#############################################
##### BUILDING A DAG ORDER DEPENDENCIES #####
#############################################


start_operator > end_operator