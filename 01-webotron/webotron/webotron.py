import boto3
import sys
import click

session = boto3.Session(profile_name='pythonAutomation')
s3=session.resource('s3')

@click.group()
def cli():
    "Webotron deploys websites to AWS"
    pass

@cli.command('list-buckets')
def list_buckets():
    "List all s3 buckets"
    for b1 in s3.buckets.all():
        print(b1)

@cli.command('list-buckets-objects')
@click.argument('bucket')
def list_buckets_objects(bucket):
    "List all of S3 objects"
    for obj in s3.Bucket(bucket).objects.all():
        print("obj")

if __name__ == '__main__':
    cli()
