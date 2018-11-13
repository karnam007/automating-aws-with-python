#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Webotron script automates the process of deploying webiste to S3. It automates the whole process
1. Configure AWS S3 buckets
2. Creating a new S3 buckets
3. Set them up for static website hosting
4. deploying static website assests
5. Configure DNS Route 53
6. Configure CDN and SSL
'''


import boto3
import sys
import click
from bucket import BucketManager


session = None
bucket_manager = None

'''

session = boto3.Session(profile_name='pythonAutomation')
#s3 = session.resource('s3')
bucket_manager = BucketManager(session)

'''

@click.group()
@click.option('--profile', default=None,help="Use a given AWS profile")
def cli(profile):
    global session, bucket_manager
    session_cfg = {}
    if profile:
        session_cfg['profile_name'] = profile

    session = boto3.Session(**session_cfg)
    bucket_manager = BucketManager(session)
    '''Webotron deploys websites to AWS'''
    pass


@cli.command('list-buckets')
def list_buckets():
    '''List all s3 buckets'''
    for b1 in bucket_manager.all_bucket():
        print(b1)

@cli.command('list-buckets-objects')
@click.argument('bucket')
def list_buckets_objects(bucket):
    '''List all of S3 objects'''
    for obj in bucket_manager.all_object(bucket):
        print("obj")


@cli.command('setup-bucket')
@click.argument('bucket')
def setup_bucket(bucket):
    '''Create and configure S3 buckets'''
    s3_bucket = bucket_manager.init_bucket(bucket)
    bucket_manager.set_policy(s3_bucket)
    bucket_manager.configure_website(s3_bucket)
    return

@cli.command('sync')
@click.argument('pathname', type = click.Path(exists=True))
@click.argument('bucket')

def sync(pathname,bucket):
    '''This is to upload the contents to AWS S3'''
    bucket_manager.sync(pathname, bucket)
    print(bucket_manager.get_bucket_url(bucket_manager.s3.Bucket(bucket)))


if __name__ == '__main__':
    cli()
