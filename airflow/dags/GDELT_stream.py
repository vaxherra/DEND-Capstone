
from airflow import DAG
from operators.Src2S3 import Src2S3
from datetime import datetime, timedelta
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.bash_operator import BashOperator

import wget

# Default parameters
default_args = {
    'owner': 'Robert Kwapich',
    'start_date': datetime(2020, 3, 31),
    'end_date': datetime(2020, 4, 2),
    'depends_on_past': False, # no need to run sequentially in time for GDELT data, can parallelize tasks
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
    'catchup': True, # we want backfills on GDELT data streams
    'email_on_retry': False
}


dag = DAG(
    dag_id='gdelt_stream',
    default_args=default_args,
    schedule_interval="@daily",
    dagrun_timeout=timedelta(minutes=60),
    tags=['example'],
    max_active_runs=1
)

#############################################
######### DEFINE A SET OF ETL TASKS #########
#############################################

start_operator = DummyOperator(task_id='Begin_execution',  dag=dag)

 
source_to_s3 = Src2S3(
    task_id="GDELT_to_s3",
    dag=dag,

    s3_bucket = 'dend-lake',
    s3_key  = "gdelt",
    src_url = "http://data.gdeltproject.org/events/{}.export.CSV.zip",
    provide_context=True
)

# TODO: task here: remove file

end_operator = DummyOperator(task_id='End_execution',  dag=dag)

#############################################
##### BUILDING A DAG ORDER DEPENDENCIES #####
#############################################

start_operator >> source_to_s3

source_to_s3 >> end_operator