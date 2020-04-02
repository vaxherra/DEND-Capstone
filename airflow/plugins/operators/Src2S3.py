from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults
from airflow.contrib.hooks.aws_hook import AwsHook



class Src2S3(BaseOperator):
    """
    Custom Airflow Operator to transfer data from a target source to on-premise AWS S3 bucket ("Src2S3"). 
 
    Args:
        s3_bucket                : name of S3 bucket
        s3_key                   : name of S3 key 
 
    
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
                 *args, **kwargs):
        
        # Call parent constructor
        super(Src2S3, self).__init__(*args, **kwargs)
        
        # Map params to object
 
        self.s3_bucket = s3_bucket
        self.s3_key = s3_key


    def execute(self, context):
        self.log.info('StageToRedshiftOperator not implemented yet')