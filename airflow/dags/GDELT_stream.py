from airflow import DAG
from operators.Src2S3 import GDELT2S3

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
import wget
import pytz

from sql_statements import sql_statements
 
#############################################
######### Python functions for ETL ##########
#############################################
#   Functions for defined PythonOperator's  #
def redshift_date_delete_rows(target_table, redshift_conn_id, *args,**kwargs):
    """
    A simple helper function to delete rows in a 'target_table' templated by context variable 'ds', i.e. the day of DAG execution formatted as 'YYYY-MM-DD'.
    Uses provided 'redshift_conn_id' airflow connection ID to establish a connection to redshift.

    Args:
        target_table            : the name of the target table in Redshift/Postgres
        redshift_conn_id        : an Airflow connection ID for AWS Redshift ("Postgres" type) connection,
    """
    redshift_hook = PostgresHook(redshift_conn_id)

    delete_sql = "DELETE FROM {} WHERE sqldate={}"  .format(target_table,kwargs['ds'])
    try:
        redshift_hook.run(delete_sql)
    except:
        print("Could not run the DELETE SQL statement")
        AirflowException("Could not run the DELETE SQL statement")

def load_data_to_redshift(aws_credentials_id,redshift_conn_id,target_table,url_base,*args, **kwargs):
    """
    A helper function to facilitate transfer of files from S3 bucket to a specified redshift table.

    Args:
        aws_credentials_id              : an Airflow connection ID for AWS IAM user (requires S3 read access),
        redshift_conn_id                : an Airflow connection ID for Redshift/Posgres database,
        target_table                    : name of a Redshift/Posgres table, where the data from S3 will be placed,
        url_base                        : address of S3 bucket with three templated fields (marked with {}) that will be filled with date YYYY, MM, and YYYYMMDD.
    """
    # Obtain AWS S3 access credentials
    aws_hook = AwsHook(aws_credentials_id)
    credentials = aws_hook.get_credentials()
    # Obtain Redshift credentials
    redshift_hook = PostgresHook(redshift_conn_id)
    # Templating SQL copy statement with Airflow macro: date of execution in YYYYMMDD format
    copy_sql = (sql_statements.COPY_SQL_GZIP.format(
        target_table, 
        url_base.format(kwargs['ds_nodash'][:4], kwargs['ds_nodash'][4:6], kwargs['ds_nodash'] ),
        credentials.access_key, credentials.secret_key
        ))

    # Running the copy statement
    try:
        redshift_hook.run(  copy_sql )
    except:
        print("Could not run the COPY SQL statement")
        AirflowException("Could not run the COPY SQL statement")

#############################################
# Default parameters for a specified DAG
default_args = {
    'owner': 'Robert Kwapich',
    'start_date': datetime(2020, 1, 1),
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

# START: a dummy placeholder operator - for visibility
start_operator = DummyOperator(task_id='Begin_execution',  dag=dag)
 
# DOWNLOAD AND PUSH DATA TO S3
source_to_s3 = GDELT2S3(
    task_id="GDELT_to_s3",
    dag=dag,

    s3_bucket = 'dend-lake',
    s3_key  = "gdelt",
    src_url = "http://data.gdeltproject.org/events/{}.export.CSV.zip",
    aws_credentials_id = "aws_credentials" ,
    provide_context=True
)

# CREATE (or do nothing if already exist) A SET OF TARGET TABLES
create_tables = PostgresOperator(
    task_id="create_redshift_tables",
    dag=dag,
    postgres_conn_id="redshift",
    sql='/sql_statements/create_tables.sql'  
)

# COPY DATA FROM S3 -> Redshift staging table
staging_gdelt = PythonOperator(
    task_id='stage_from_s3_to_redshift',
    dag=dag,
    python_callable=load_data_to_redshift,
    provide_context=True,
    op_kwargs={'url_base': "s3://dend-lake/gdelt/{}/{}/{}.export.CSV.gz", # YEAR/MONTH/ds_nodash
    'target_table':'staging_gdelt_events',
    'aws_credentials_id':'aws_credentials',
    'redshift_conn_id':'redshift'}, 
)

# COPY SELECTED DATA FROM STAGING TABLE TO FACT TABLE
load_gdelt_fact_table = stage2table(
    task_id='load_gdelt_fact_table',
    dag=dag,

    redshift_conn_id="redshift",
    target_table="gdelt_events",
    target_columns=sql_statements.gdelt_fact_columns,
    insert_mode="append", # delete_load/append
    query=sql_statements.gdelt_events_table_insert 

)

# RUN DATA QUALITY CHECKS
run_quality_checks = DataQualityOperator(
    task_id='run_gdelt_quality_checks',
    dag=dag,
    redshift_conn_id="redshift",
    tests=[ (sql_statements.gdelt_check_nulls, "{}[0][0] == 0" ), # there are no NULL values in significant fields
    (sql_statements.gdelt_num_records, "{}[0][0] >= 100") # it would be unusual to see less than 100 events
          ]
)

# CLEAR STAGING TABLE for a selected day only, as there might be multiple concurrent processes running
clearing_staging_gdelt_events = PythonOperator(
    task_id='clearing_staging_gdelt_events',
    dag=dag,

    python_callable=redshift_date_delete_rows,
    provide_context=True,
    op_kwargs={'redshift_conn_id':'redshift', 
    'target_table':'staging_gdelt_events'}, 
)

# DUMMY END OPERATOR - for visibility only
end_operator = DummyOperator(task_id='End_execution',  dag=dag)

#############################################
##### BUILDING A DAG ORDER DEPENDENCIES #####
#############################################
# Building a DAG of operations for consistency:
#  a simple linear DAG that can be parallelized

start_operator >> source_to_s3
source_to_s3 >> create_tables
create_tables >> staging_gdelt
staging_gdelt >> load_gdelt_fact_table
load_gdelt_fact_table>> run_quality_checks
run_quality_checks >> clearing_staging_gdelt_events
clearing_staging_gdelt_events >> end_operator