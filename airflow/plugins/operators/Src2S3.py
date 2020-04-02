# Airflow 
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults
from airflow.contrib.hooks.aws_hook import AwsHook
from airflow.hooks.S3_hook import S3Hook # https://airflow.apache.org/docs/stable/_api/airflow/hooks/S3_hook/index.html

# General libraries
import os
import urllib.request

class Src2S3(BaseOperator):
    """
    Custom Airflow Operator to transfer data from a target source to on-premise AWS S3 bucket ("Src2S3"). 
 
    Args:
        s3_bucket                : name of S3 bucket
        s3_key                   : name of S3 key 
        src_url                  : web address template of a source CSV file. Must contain '{}' that will be filled with context['next_ds_nodash'], i.e 'YYYMMDD'. 
 
    
    Returns:
        None
    """
    # Use "s3_key" as template, allowing to use context variables for formatting
    template_fields = ("s3_key",)
    
    ui_color = '#358140'
    
    # A constructor defining parameters to the operator
    @apply_defaults
    def __init__(self,
                 s3_bucket="",
                 s3_key="",
                 src_url = "",
                 *args, **kwargs):
        
        # Call parent constructor
        super(Src2S3, self).__init__(*args, **kwargs)
        
        # Map params to object
        self.s3_bucket = s3_bucket
        self.s3_key = s3_key
        self.src_url = src_url

    def execute(self, context):

        # Download file 
        day_url = self.src_url.format(context['next_ds_nodash'])
        print(os.system('pwd'))

        # TODO: try/except case
        urllib.request.urlretrieve(day_url, 'tmp_data/'+context['next_ds_nodash']+".zip"  )


        # Place in S3
        # https://airflow.apache.org/docs/stable/_api/airflow/hooks/S3_hook/index.html
        # def load_file...


        # Delete

        self.log.info( 'Processing date: ' + str(context['next_ds_nodash']) )
        self.log.info(os.getcwd())