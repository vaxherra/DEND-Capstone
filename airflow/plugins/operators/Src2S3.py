# Airflow 
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults
from airflow.contrib.hooks.aws_hook import AwsHook
from airflow.hooks.S3_hook import S3Hook # https://airflow.apache.org/docs/stable/_api/airflow/hooks/S3_hook/index.html

from airflow import AirflowException
# General libraries
import os
import urllib.request


class GDELT2S3(BaseOperator):
    """
    Custom Airflow Operator for a specific data source "GDELT". It transfers data from a target file available on the internet throgh provided url to on-premise AWS S3 bucket. 
 
    Args:
        s3_bucket                : name of S3 bucket
        s3_key                   : name of S3 key 
        src_url                  : web address template of a source CSV file. Must contain '{}' that will be filled with context['ds_nodash'], i.e 'YYYMMDD' from the previous day (due to GDELT 1.0 reporting of events)
        aws_credentials_id       : an Airflow conn_id for AWS user
    
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
                 aws_credentials_id = "",
                 *args, **kwargs):
        
        # Call parent constructor
        super(GDELT2S3, self).__init__(*args, **kwargs)
        
        # Map params to object
        self.s3_bucket = s3_bucket
        self.s3_key = s3_key
        self.src_url = src_url
        self.aws_credentials_id = aws_credentials_id

    def execute(self, context):
        """
        Performs a series of operations:
            1. Downloads a CSV file in .ZIP format
            2. Converts .ZIP to .GZ, as AWS can operate on gzipped archive. This saves space on S3 bucket.
            3. Places file in S3://s3_key/YYYY/MM location stratified by year and month
            4. Deletes local files after successfully uploading them to S3 location.

        """
        ########################################################
        ############ DOWNLOADING A FILE ########################
        ########################################################
        # try downloading a file, using a context variable
        day_url = self.src_url.format(context['ds_nodash'])
        filename = 'tmp_data/'+context['ds_nodash']+".export.CSV" # output file location and name
        try: 
            urllib.request.urlretrieve(day_url, filename + ".zip" )
        except:
            self.log.info("Could not download a file from: "+day_url)
            AirflowException("File could not be downloaded.")

        ######################################################## 
        ############ Convert ZIP to GZIP ####################### 
        ######################################################## 
        try:
            os.system('unzip '+ filename+".zip -d tmp_data/"  )
            os.system('gzip -c ' + filename +" > " + filename+".gz"  )

        except:
            self.log.info("Could not zip/gzip files")
            AirflowException("File could not be unzipped or gzipped.")

        ########################################################
        ########### PLACE FILE IN S3 ###########################
        ########################################################
        # S3 hook documentation: https://airflow.apache.org/docs/stable/_api/airflow/hooks/S3_hook/index.html
        s3_hook = S3Hook(self.aws_credentials_id)
        self.log.info("Uploading file to S3 ...")
        try:
            s3_hook.load_file(
                filename= filename + ".gz",
                key = self.s3_key  + "/" +  context['ds_nodash'][:4] + "/" + context['ds_nodash'][4:6]  + "/"  + context['ds_nodash']+".export.CSV.gz" ,
                bucket_name = self.s3_bucket, 
                replace = True, #in case re-running Airflow, we can replace file
                encrypt = False
            )
            self.log.info("Successfull upload to S3")
        except:
            self.log.info("Could not upload a file to S3: "+ filename)
            AirflowException("File could not be uploaded to S3.")

        ########################################################
        ############ Deletes local tmp files ###################
        ########################################################
        # The files are only temporarily stored in EC2 machine operating Airflow, and need to be removed as soon as stored in persisten S3 storage.
        try:
            os.remove(filename)
            os.remove(filename+".gz")
            os.remove(filename+".zip")
            self.log.info("Local tmp file removed")
        except:
            self.log.info("Could not remove tmp stream file. Aborting.")
            AirflowException("Could not remove tmp stream file. Aborting.")