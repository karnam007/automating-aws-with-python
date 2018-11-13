'''Classes for S3 buckets'''
import mimetypes
from pathlib import Path
from botocore.exceptions import ClientError
import util


class BucketManager:
    def __init__(self,session):
        self.session = session
        self.s3 = self.session.resource('s3')

    def all_bucket(self):
        '''retuen all the buckets from the AWS account'''
        return self.s3.buckets.all()

    def get_region_name(self,bucket):
        '''this will give the bucket region name'''
        bucket_location = self.s3.meta.client.get_bucket_location(Bucket=bucket.name)
        return bucket_location["LocationConstraint"] or 'us-east-1'


    def get_bucket_url(self, bucket):
        "get the bucket URL for the S3 which is generated thingy"
        return "http://{}.{}".format(bucket.name,
        util.get_endpoint(self.get_region_name(bucket)).host)

    def all_object(self,bucket_name):
        '''return all the objects from the S3 buckets'''
        return self.s3.Bucket(bucket_name).objects.all()

    def init_bucket(self, bucket_name):
        '''creating a new bucket '''
        s3_bucket = None
        try:
            s3_bucket = self.s3.create_bucket(Bucket=bucket_name, CreateBucketConfiguration={'LocationConstraint': self.session.region_name})
        except ClientError as e:
            if e.response['Error']['Code'] == 'BucketAlreadyOwnedByYou':
                s3_bucket = self.s3.Bucket(bucket_name)
            else:
                raise e
        return s3_bucket

    def set_policy(self, bucket):
        '''policy defination'''
        policy = '''
        {
          "Version":"2012-10-17",
          "Statement":[
            {
              "Sid":"AddPerm",
              "Effect":"Allow",
              "Principal": "*",
              "Action":["s3:GetObject"],
              "Resource":["arn:aws:s3:::%s/*"]
            }
          ]
        }
        ''' % bucket.name
        policy= policy.strip()
        pol = bucket.Policy()
        pol.put(Policy=policy)

    def configure_website(self,bucket):
        ws = bucket.Website()
        ws.put(WebsiteConfiguration={ 'ErrorDocument': {
                        'Key': 'error.html'
                    },
                    'IndexDocument': {
                        'Suffix': 'index.html'
                    }
                })
    @staticmethod
    def upload_file( bucket, path, key):
        content_type = mimetypes.guess_type(key)[0] or 'text/plain'
        return bucket.upload_file(
            path,
            key,
            ExtraArgs = {"ContentType":"text/html"}
        )

    def sync(self, pathname, bucket_name):

        bucket= self.s3.Bucket(bucket_name)

        root = Path(pathname).expanduser().resolve()

        def handle_dir(target):
            for p in target.iterdir():
                if p.is_dir(): handle_dir(p)
                #if p.is_file(): print("Path:{} Key:{}".format(p, p.relative_to(root)))
                if p.is_file(): self.upload_file(bucket,str(p),str(p.relative_to(root)))
        handle_dir(root)
