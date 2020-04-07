from airflow.hooks.postgres_hook import PostgresHook
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults
from airflow.contrib.hooks.aws_hook import AwsHook


class S32Redshift(BaseOperator):
    """
    Custom Airflow Operator to load any JSON formatted file residing in S3 bucket to Amazon Redshift warehouse. Operator runs an SQL copy statement based using provided AWS credentials and Airflow PostgresHook for a pre-configured connection.
    
    
    Args:
        redshift_conn_id         : an Airflow conn_id for Redshift 
        aws_credentials_id       : an Airflow conn_id for AWS user
        table                    : name of target staging table
        s3_bucket                : name of S3 bucket
        s3_key                   : name of S3 key 
        JSONPaths                :
    
    Returns:
        None
    """


    # TODO: ensure staging tables and dim/fact tables were created before


    def execute(self, context):

        self.log.info("To implement this part.")