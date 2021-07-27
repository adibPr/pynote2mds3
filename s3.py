#!/usr/bin/env python3
# sys module
import os
import sys
import configparser

# third parties module
import boto3
from botocore.exceptions import ClientError


class S3Client:

    def __init__(self, config_path):

        self.config = self._load_config(config_path)
        self.client = boto3.client("s3", 
                    aws_access_key_id=self.config['credentials']['secret_key'],
                    aws_secret_access_key=self.config['credentials']['access_key'],
                    endpoint_url=self.config['credentials']['endpoint_url']
                )
        # self.bucket = self.client.Bucket(config['credentials']['bucket'])

    def _load_config(self, config_path):
        config = configparser.ConfigParser()
        config.read(config_path)
        return config
    
    def upload(self, fin, fout, w_encrypt=False, w_public=False):
        pass

    def download(self, fout, fin, w_encrypt=False):
        pass

    def delete(self, fout):
        pass

    def move(self, fout_src, fout_tgt):
        pass

    def list(self, pattern=None):
        response = self.client.list_objects_v2(Bucket=self.config['credentials']['bucket'])
        assert response['ResponseMetadata']['HTTPStatusCode'] == 200,\
                'List object failed, {}'.format(response)

        for obj in response['Contents']:
            print (obj['Key']) 

if __name__ == "__main__":
    client = S3Client('config.yml')
    client.list()
