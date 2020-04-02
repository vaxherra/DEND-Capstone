import boto3
from botocore.exceptions import ClientError
import logging

class iac():
    """
    IAC: Infrastructure as Code. Provides a set of useful methods to create and terminate different AWS infrastructure solutions.

    Args:
        KEY     : defines Amazon IAM user ID: "aws_access_key_id"
        SECRET  : definess Amazon IAM user password: "aws_secret_access_key"

    """
    
    ###################################################
    ################ Default parameters ###############
    ###################################################
        # AWS allowed regions
    allowed_regions = ['us-east-2',
        'us-east-1',
        'us-west-1',
        'us-west-2',
        'ap-east-1',
        'ap-south-1',
        'ap-northeast-3',
        'ap-northeast-2',
        'ap-southeast-1',
        'ap-southeast-2',
        'ap-northeast-1',
        'ca-central-1',
        'cn-north-1',
        'cn-northwest-1',
        'eu-central-1',
        'eu-west-1',
        'eu-west-2',
        'eu-west-3',
        'eu-north-1',
        'me-south-1',
        'sa-east-1',
        'us-gov-east-1',
        'us-gov-west-1']

    default_region='us_west-2'
    def __init__(self,KEY,SECRET,region):
        self.KEY = KEY
        self.SECRET = SECRET

        if(region.lower() not in self.allowed_regions  ):
            self.region = self.default_region
        else:
            self.region = region.lower()

        # S3 client on AWS
        self.s3_client = boto3.client('s3', region_name=self.region, aws_access_key_id=self.KEY, aws_secret_access_key=self.SECRET)

    ###################################################
    ################ S3 Bucket functions ##############
    ###################################################

    def create_bucket(self,bucket_name):
        """Create an S3 bucket in a specified region

        If a region is not specified, the bucket is created in the S3 default
        region (us_west-2).

        Args:
            bucket_name: Bucket to create

        Returns:
            True if bucket created, else False
        """
        try:

            location = {'LocationConstraint': self.region}
            self.s3_client.create_bucket(Bucket=bucket_name, CreateBucketConfiguration=location)

    
        except ClientError as e:
            logging.error(e)
            return False
        return True

    def delete_bucket(self,bucket_name):
        """Delete an S3 bucket in a specified region. Region is specified by the constructor. If a region is not specified, the bucket is created in the S3 default region (us_west-2).

        Args:
            bucket_name: Bucket to create

        Returns:
            True if bucket deleted, else False
        """

        try:
            response = self.s3_client.delete_bucket(Bucket=bucket_name)
        except ClientError as e:
            logging.error(e)
            return False
        return True

    def list_buckets(self):

        try:
            response = self.s3_client.list_buckets()

            buckets= {self.region : [ bucket['Name'] for bucket in response['Buckets']   ] }

        except ClientError as e:
            logging.error(e)
            return False
        return buckets
        


 