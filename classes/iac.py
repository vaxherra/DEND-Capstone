import boto3
from botocore.exceptions import ClientError
import logging
import configparser
import json
import pandas as pd

# TODO re-write IAC as modular class IAC and subclasses Redshift/S3/IAM
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

    config = configparser.ConfigParser()
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

        # Redshift client of AWS
        self.redshift = boto3.client('redshift',
                       region_name=self.region,
                       aws_access_key_id=self.KEY,
                       aws_secret_access_key=self.SECRET
                       )
        # IAM on AWS
        self.iam = boto3.client('iam',aws_access_key_id=self.KEY,
                     aws_secret_access_key=self.SECRET,
                     region_name=self.region
                  )

        # EC2
        self.ec2 = boto3.resource('ec2',
                       region_name='us-west-2',
                       aws_access_key_id=self.KEY,
                       aws_secret_access_key=self.SECRET
                    )

    ###################################################
    ################ S3 Bucket functions ##############
    ###################################################

    def S3_create(self,bucket_name):
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

    def S3_delete(self,bucket_name):
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

    def S3_list(self):

        try:
            response = self.s3_client.list_buckets()

            buckets= {self.region : [ bucket['Name'] for bucket in response['Buckets']   ] }

        except ClientError as e:
            logging.error(e)
            return False
        return buckets
        

    ###################################################
    ############## AWS Basic IAM Funcitons ############
    ###################################################

    # List of functions is by all means not exhaustive. Rather it serves as an easy point of access to serve assumed architectrural solutions

    # TODO: create IAM role
    def iam_s3_readonly_create(self,config_file):
        """
        TODO write description. 
        Returns ARN for a given IAM role
        """

        # Load config file:
        try:
            self.config.read_file(open(config_file))
    
        except Exception as e:
            print("Could not open config file. \n", e)
            return(e)

 
        required_fields = [ 'DWH_IAM_ROLE_NAME' ]

        # Check if all necessary fields have required keys
            # and for IAM it is only one field, and it must not be empty
        for field in required_fields:
            try:
                iam_name = self.config.get("DWH",field)

                if(iam_name==''):
                    return("The field '"+ field + "' is empty. Please fill in provided config file: " + config_file )
            except:
                return("The field "+ field + " not present in " + config_file +". The required keys in " + config_file + " are: \n " + ', \n  '.join(required_fields) )


        # Create a given IAM role:
        # TODO: source: https://github.com/vaxherra/DEND-Redshift-DWH/blob/master/IaC.ipynb

        try:
            print("1.1 Creating a new IAM Role") 
            dwhRole = self.iam.create_role(
                Path='/',
                RoleName=self.config.get("DWH",required_fields[0]),
                Description = "Allows Redshift clusters to call AWS services on your behalf.",
                AssumeRolePolicyDocument=json.dumps(
                    {'Statement': [{'Action': 'sts:AssumeRole',
                    'Effect': 'Allow',
                    'Principal': {'Service': 'redshift.amazonaws.com'}}],
                    'Version': '2012-10-17'})
            )    
        except Exception as e:
            print("Could not create an IAM ROLE: " + e)


        print("1.2 Attaching Policy")

        self.iam.attach_role_policy(RoleName=self.config.get("DWH",required_fields[0]),
                            PolicyArn="arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess"
                            )['ResponseMetadata']['HTTPStatusCode']

        print("1.3 Get the IAM role ARN")
        roleArn = self.iam.get_role(RoleName=self.config.get("DWH",required_fields[0]))['Role']['Arn']

        print("\t",roleArn)

        print("1.4 Saving IAM role ARN in provided config file: " + config_file)
        self.config['IAM_ROLE']['ARN'] = roleArn
        with open(config_file, 'w') as configfile:
            self.config.write(configfile)

 

        return roleArn
 

    ###################################################
    ############## AWS Redshift functions #############
    ###################################################
 
 
    def redshift_create(self,config_file):
        """
        Given a config file creates an AWS Redshift cluster.

        """

        # Load config file:
        try:
            self.config.read_file(open(config_file))
            print("Loaded config file...")
        except Exception as e:
            print("Could not open config file. \n", e)
            return(e)

        dwh_required_fields = ['DWH_CLUSTER_TYPE', 'DWH_NUM_NODES', 'DWH_NODE_TYPE',
        'DWH_CLUSTER_IDENTIFIER', 'DWH_DB', 'DWH_DB_USER', 'DWH_DB_PASSWORD','DWH_PORT', 'DWH_IAM_ROLE_NAME' ]
        iam_required_fields = ['arn']

        required_fields = {'DWH': dwh_required_fields, 'IAM_ROLE':iam_required_fields }

        ### Check required fields:

        for key,fields in required_fields.items():
            for field in fields:
                try:
                    field_value = self.config.get(key,field)

                    if(field_value==''):
                        return("The field '"+ key + ": "  +  field + "' is empty. Please fill in provided config file: " + config_file )
                except:
                    return("The field "+  key + ": " + field + " not present in " + config_file +". The required keys in " + config_file + " are: \n " + ', \n  '.join(required_fields) )

        ### Creating a redshift cluster


        try:
            response = self.redshift.create_cluster(        
                # DWH
                ClusterType= self.config.get("DWH",'DWH_CLUSTER_TYPE'),
                NodeType= self.config.get("DWH",'DWH_NODE_TYPE'),
                NumberOfNodes=  int(self.config.get("DWH",'DWH_NUM_NODES')),

                #Identifiers & Credentials
                DBName= self.config.get("DWH",'DWH_DB'),
                ClusterIdentifier= self.config.get("DWH",'DWH_CLUSTER_IDENTIFIER'),
                MasterUsername=self.config.get("DWH",'DWH_DB_USER'),
                MasterUserPassword=self.config.get("DWH",'DWH_DB_PASSWORD'),
                
                #Roles (for s3 access)
                IamRoles=[ self.config.get("IAM_ROLE",'arn')     ]  
            )
        except Exception as e:
            print(e)

        # TODO: write endpoint to config file

    ############################################################################
    def redshift_properties(self,config_file):
        """
        TODO: describe function
        Given a config file returns a pandas dataframe describing cluster status and properties.
        """
        # Load config file:
        try:
            self.config.read_file(open(config_file))
    
        except Exception as e:
            print("Could not open config file. \n", e)
            return(e)

        dwh_required_fields = ['DWH_CLUSTER_TYPE', 'DWH_NUM_NODES', 'DWH_NODE_TYPE',
        'DWH_CLUSTER_IDENTIFIER', 'DWH_DB', 'DWH_DB_USER', 'DWH_DB_PASSWORD', 'DWH_DB_PASSWORD','DWH_PORT', 'DWH_IAM_ROLE_NAME' ]
        iam_required_fields = ['arn']

        required_fields = {'DWH': dwh_required_fields, 'IAM_ROLE':iam_required_fields }

        ### Check required fields:

        for key,fields in required_fields.items():
            for field in fields:
                try:
                    field_value = self.config.get(key,field)

                    if(field_value==''):
                        return("The field '"+ key + ": "  +  field + "' is empty. Please fill in provided config file: " + config_file )
                except:
                    return("The field "+  key + ": " + field + " not present in " + config_file +". The required keys in " + config_file + " are: \n " + ', \n  '.join(required_fields) )

        ### Obtain cluster properties:

        DWH_CLUSTER_IDENTIFIER = self.config.get("DWH",'DWH_CLUSTER_IDENTIFIER')

        try:
            cluster_properties = self.redshift.describe_clusters(ClusterIdentifier=DWH_CLUSTER_IDENTIFIER)['Clusters'][0]

        except Exception as e:
            print("Could not describe cluster: "+DWH_CLUSTER_IDENTIFIER+". Possibly the cluster doest not exist. Check AWS console. Error message: \n")
            return(e)

        keysToShow = ["ClusterIdentifier", "NodeType", "ClusterStatus", "MasterUsername", "DBName",  "NumberOfNodes", 'VpcId','Endpoint']
        x = [(k, v) for k,v in cluster_properties.items() if k in keysToShow]
        
        return pd.DataFrame(data=x, columns=["Key", "Value"])

    ############################################################################
    def redshift_delete(self,config_file):
 
        # Load config file:
        try:
            self.config.read_file(open(config_file))
            print("Loaded config file...")
        except Exception as e:
            print("Could not open config file. \n", e)
            return(e)

        dwh_required_fields = ['DWH_CLUSTER_IDENTIFIER' ]
     
        required_fields = {'DWH': dwh_required_fields,   }

        ### Check required fields:

        for key,fields in required_fields.items():
            for field in fields:
                try:
                    field_value = self.config.get(key,field)

                    if(field_value==''):
                        return("The field '"+ key + ": "  +  field + "' is empty. Please fill in provided config file: " + config_file )
                except:
                    return("The field "+  key + ": " + field + " not present in " + config_file +". The required keys in " + config_file + " are: \n " + ', \n  '.join(required_fields) )

        ### Delete a redshift cluster

        try: 
            DWH_CLUSTER_IDENTIFIER = self.config.get("DWH",'DWH_CLUSTER_IDENTIFIER')
            response = self.redshift.delete_cluster( ClusterIdentifier=DWH_CLUSTER_IDENTIFIER,  SkipFinalClusterSnapshot=True)
        
            print("Deleting cluster")
            return(response)

        except Exception as e:
            print(e)        

    ############################################################################
    def redshift_authorize_connection(self,config_file,VPC_ID):
        """
        # TODO: describe 
        """
        # TODO: implement
        # Load config file:
        try:
            self.config.read_file(open(config_file))
    
        except Exception as e:
            print("Could not open config file. \n", e)
            return(e)

        dwh_required_fields = ['DWH_PORT','DWH_DB_USER','DWH_DB_PASSWORD','DWH_ENDPOINT','DWH_DB' ]
 

        required_fields = {'DWH': dwh_required_fields  }

        ### Check required fields:

        for key,fields in required_fields.items():
            for field in fields:
                try:
                    field_value = self.config.get(key,field)

                    if(field_value==''):
                        return("The field '"+ key + ": "  +  field + "' is empty. Please fill in provided config file: " + config_file )
                except:
                    return("The field "+  key + ": " + field + " not present in " + config_file +". The required keys in " + config_file + " are: \n " + ', \n  '.join(required_fields) )


        ###################### Test connection

        try:
            vpc = self.ec2.Vpc(id=VPC_ID)
            defaultSg = list(vpc.security_groups.all())[0]
            print(defaultSg)
            defaultSg.authorize_ingress(
                GroupName=defaultSg.group_name,
                CidrIp='0.0.0.0/0',
                IpProtocol='TCP',
                FromPort=int(self.config.get("DWH",'DWH_PORT')),
                ToPort=int(self.config.get("DWH",'DWH_PORT'))
            )
        except Exception as e:
            print("Could not authorize ingress or ingress already present. Read the error below:")
            print(e)

        conn_string="postgresql://{}:{}@{}:{}/{}".format(
            self.config.get("DWH","DWH_DB_USER"), 
            self.config.get("DWH","DWH_DB_PASSWORD") , 
            self.config.get("DWH","DWH_ENDPOINT"), 
            self.config.get("DWH","DWH_PORT") ,
            self.config.get("DWH","DWH_DB") 
        )

        return conn_string