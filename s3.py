#!/usr/bin/env python3
# sys module
import os
import sys
import configparser

# third parties module
import boto3
from botocore.exceptions import ClientError


class S3Client:
    """
    Some terminologies:
        fout: file name "out" there, i.e in the server (S3), or in S3 term, key.
        fin: file name "in" here, i.e local machine.
    """

    def __init__(self, config_path):
        self.config = self._load_config(config_path)
        self.client = boto3.client("s3", 
                    aws_access_key_id=self.config['credentials']['secret_key'],
                    aws_secret_access_key=self.config['credentials']['access_key'],
                    endpoint_url=self.config['credentials']['endpoint_url']
                )

    def _load_config(self, config_path):
        config = configparser.ConfigParser()
        config.read(config_path)
        return config
    
    def upload(self, fin, fout, w_encrypt=False, w_public=False):
        pass

    def download(self, fout, fin, w_encrypt=False):
        if w_encrypt:
            encrypt_args = {
                    "SSECustomerKey": self.config['encryption']['key'],
                    "SSECustomerAlgorithm": self.config['encryption']['algo']
                }
        else:
            encrypt_args = {}

        try:
            response = self.client.download_file(
                Key=fout,
                Bucket=self.config['credentials']['bucket'],
                Filename=fin,
                ExtraArgs = encrypt_args
            )
        except ClientError as e:
            print(e)
        else:
            print("Download successfull")

    def delete(self, fout):
        pass

    def move(self, fout_src, fout_tgt):
        pass

    def iter(self, pattern=None):
        response = self.client.list_objects_v2(Bucket=self.config['credentials']['bucket'])
        assert response['ResponseMetadata']['HTTPStatusCode'] == 200,\
                'List object failed, {}'.format(response)

        for obj in response['Contents']:
            yield obj

    def list(self, pattern=None):
        fouts = []
        for obj in self.iter():
            fouts.append(obj)
        return fouts

if __name__ == "__main__":
    client = S3Client('config.yml')
    fouts = client.list()
    print("\n".join([o['Key'] for o in fouts]))
    client.download(fouts[0]['Key'], fouts[1]['Key'], w_encrypt=True)
