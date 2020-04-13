
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
 
 


#############################################
######### Python functions for ETL ##########
#############################################

def load_data_to_redshift(*args, **kwargs):
    """
    TODO: document
    """

    # Obtain AWS S3 access credentials
    aws_hook = AwsHook("aws_credentials")
    credentials = aws_hook.get_credentials()
    # Obtain Redshift credentials
    redshift_hook = PostgresHook("redshift")

    # TODO: remove below 2 lines
    print("Kurwa")
    print(kwargs)

    copy_sql = (sql_statements.COPY_SQL.format(
        kwargs['target_table'], 
        kwargs['url_base'].format(kwargs['ds_nodash'][:4], kwargs['ds_nodash'][4:6], kwargs['ds_nodash'] ),
        credentials.access_key, credentials.secret_key
        ))
    print(copy_sql)
    redshift_hook.run(  copy_sql )


#############################################
# Default parameters
default_args = {
    'owner': 'Robert Kwapich',
    'start_date': datetime(2020, 3, 29),
    'end_date': datetime(2020, 4, 30),
    'depends_on_past': False, # no need to run sequentially in time for GDELT data, can parallelize tasks
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
    'catchup': True, # we want backfills on GDELT data streams
    'email_on_retry': False
}

schedule_interval = '15 {} * * *' # we'll start the pipeline 15 minutes AFTER the source data is published at 6am EST time
# UTC vs EST time interval difference
est_utc_timedelta =datetime.utcnow().hour - datetime.now().hour
schedule_interval = schedule_interval.format(6+est_utc_timedelta) # 6am EST data is published, there is a variable shift, accounted by est_utc_timedelta

dag = DAG(
    dag_id='gdelt_stream',
    default_args=default_args,
    schedule_interval= schedule_interval, #  i.e. "@daily", but at 6:15am EST
    dagrun_timeout=timedelta(minutes=60), # how long a DagRun should be up before timing out / failing,
    tags=['gdelt_data_stream'],
    max_active_runs=2
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
    aws_credentials_id = "aws_credentials" ,
    provide_context=True
)

create_tables = PostgresOperator(
    task_id="create_redshift_tables",
    dag=dag,
    postgres_conn_id="redshift",
    sql='/sql_statements/create_tables.sql'  
)


staging_gdelt = PythonOperator(
    task_id='load_from_s3_to_redshift',
    dag=dag,
    python_callable=load_data_to_redshift,
    provide_context=True,
    op_kwargs={'url_base': "s3://dend-lake/gdelt/{}/{}/{}.export.CSV.gz", # YEAR/MONTH/ds_nodash
    'target_table':'staging_gdelt_events'}, 
)

end_operator = DummyOperator(task_id='End_execution',  dag=dag)

#############################################
##### BUILDING A DAG ORDER DEPENDENCIES #####
#############################################
start_operator >> source_to_s3
source_to_s3 >> create_tables
create_tables >> staging_gdelt
# TODO: data quality operator
# TODO: dimensional modeling
# TODO: additional source - dimension tables
# TODO: staging table clearing
staging_gdelt >> end_operator