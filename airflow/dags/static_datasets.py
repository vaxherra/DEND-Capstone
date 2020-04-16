from airflow import DAG
 
from operators.stage2table import stage2table
from operators.data_quality import DataQualityOperator

from datetime import datetime, timedelta
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.bash_operator import BashOperator
from airflow.operators.postgres_operator import PostgresOperator
from airflow.operators.python_operator import PythonOperator

from airflow.contrib.hooks.aws_hook import AwsHook
from airflow.hooks.postgres_hook import PostgresHook
from airflow import AirflowException
from airflow.hooks.S3_hook import S3Hook # https://airflow.apache.org/docs/stable/_api/airflow/hooks/S3_hook/index.html

import wget
import pytz

from sql_statements import sql_statements

##########################################################################

def load_to_s3(location,filename,s3_bucket,s3_key,aws_credentials_id,*args,**kwargs):
    """
    Load provided `file` in a `locaiton` to a given `s3_bucket` placing it in `s3_key` using `aws_credentials_id`.

    """

    s3_hook = S3Hook(aws_credentials_id)

    try:

        s3_hook.load_file(
            filename= location + "/" + filename,
            key = s3_key + "/" + filename ,
            bucket_name = s3_bucket, 
            replace = True, #in case re-running Airflow, we can replace file
            encrypt = False
        )

        print("Successfull upload to S3")

    except:
        print("Could not upload a file to S3: "+ filename)
        AirflowException("File could not be uploaded to S3.")

def load_data_to_redshift(target_table, s3_location,aws_credentials_id , *args, **kwargs):
    """
    TODO: document, S3 -> Redshift
    """

    # Obtain AWS S3 access credentials
    aws_hook = AwsHook(aws_credentials_id)
    credentials = aws_hook.get_credentials()
    # Obtain Redshift credentials
    redshift_hook = PostgresHook("redshift")


    copy_sql = (sql_statements.COPY_SQL.format(
        target_table, 
        s3_location,
        credentials.access_key, credentials.secret_key
        ))
    print(copy_sql)
    redshift_hook.run(  copy_sql )

##########################################################################
 
# Default parameters
default_args = {
    'owner': 'Robert Kwapich',
    'start_date': datetime(2020, 3, 29),
    'depends_on_past': False, # no need to run sequentially in time for GDELT data, can parallelize tasks
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
    'catchup': False, 
    'email_on_retry': False
}

# TODO: fill DAG description

dag = DAG(
    dag_id='static_dataset',
    description = "A set of ETL procedures for static datasets: GNIS ...",
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

# Creates a set of empty tables
create_tables = PostgresOperator(
    task_id="create_redshift_tables",
    dag=dag,
    postgres_conn_id="redshift",
    sql='/sql_statements/create_tables.sql'  
)

############# Load files to S3 

# Load file to S3
gnis_to_s3 = PythonOperator(
    task_id='gnis_to_s3',
    dag=dag,
    python_callable=load_to_s3,
    provide_context=True,
    op_kwargs = {
        'location': 'tmp_data',
        'filename' : 'NationalFile_20200301.txt',
        's3_bucket' : 'dend-lake',
        's3_key' : 'gnis',
        'aws_credentials_id': 'aws_credentials',
    }
)
############# Load S3 -> Staging Tables

# S3 -> staging table 'gnis_staging'
staging_gnis_2_redshift  = PythonOperator(
    task_id='staging_gnis_2_redshift',
    dag=dag,
    python_callable=load_data_to_redshift,
    provide_context=True,
    op_kwargs={'s3_location': "s3://dend-lake/gnis/NationalFile_20200301.txt", 
    'target_table':'gnis_staging',
    'aws_credentials_id':'aws_credentials'}, 
)

############# Dimensional modelling
# ? 


# TODO: gnis_staging to gnis
load_gnis_dim_table = stage2table(
task_id='load_gnis_dim_table',
dag=dag,

redshift_conn_id="redshift",
target_table="gnis",
target_columns="FEATURE_ID, FEATURE_NAME, FEATURE_CLASS, STATE_ALPHA, COUNTY_NAME, PRIMARY_LAT_DMS, PRIM_LONG_DMS, ELEV_IN_M, MAP_NAME, DATE_CREATED, DATE_EDITED",
insert_mode="delete_load", # delete_load/append
query=sql_statements.gnis_table_insert

)

run_quality_checks = DataQualityOperator(
    task_id='run_data_quality_checks',
    dag=dag,
    redshift_conn_id="redshift",
    tests=[ (sql_statements.gnis_check_nulls, "{}[0][0] == 0" ), # there are no NULL values in significant fields
    (sql_statements.gnis_num_records, "{}[0][0] >= 2000000") # we have more than 2 million records in this table
          ]
)


drop_gnis_staging = PostgresOperator(
    task_id="drop_gnis_staging",
    dag=dag,
    postgres_conn_id="redshift",
    sql='DROP TABLE gnis_staging'  
)




end_operator = DummyOperator(task_id='End_execution',  dag=dag)



#############################################
##### BUILDING A DAG ORDER DEPENDENCIES #####
#############################################


start_operator >> create_tables
create_tables >> gnis_to_s3
gnis_to_s3 >> staging_gnis_2_redshift
staging_gnis_2_redshift >> load_gnis_dim_table
load_gnis_dim_table >> run_quality_checks
run_quality_checks >> drop_gnis_staging
drop_gnis_staging >> end_operator