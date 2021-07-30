#!/usr/bin/env python3
# sys module
import os
import sys
import configparser
import ntpath
from urllib import parse
import re

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
    
    def _get_encrypt_param(self, enabled=False):
        if enabled:
            encrypt_args = {
                    "SSECustomerKey": self.config['encryption']['key'],
                    "SSECustomerAlgorithm": self.config['encryption']['algo']
                }
        else:
            encrypt_args = {}
        return encrypt_args

    def upload(self, fin, fout=None, w_encrypt=False, w_public=False):
        encrypt_args = self._get_encrypt_param(w_encrypt)
        if w_public:
            ACL='public-read'
        else:
            ACL='private'

        # get filename in case fout is none
        # source: https://stackoverflow.com/questions/8384737/extract-file-name-from-path-no-matter-what-the-os-path-format
        if fout is None:
            head, tail = ntpath.split(fin)
            fout = tail or ntpath.basename(head)

        try:
            response = self.client.upload_file(
                Filename=fin,
                Bucket=self.config['credentials']['bucket'],
                Key=fout,
                ExtraArgs = {**encrypt_args, 'ACL': ACL}
            )
        except ClientError as e:
            print(e)
        else:
            print("Upload successfull")


        # adding bucket name before host name
        addr = re.sub(
                    r"https\://", 
                    r"https://" + self.config['credentials']['bucket'] + r".", 
                    self.config['credentials']['endpoint_url']
                )
        return parse.urljoin(addr, parse.quote(fout))

    def download(self, fout, fin=None, w_encrypt=False):
        encrypt_args = self._get_encrypt_param(w_encrypt)

        if fin is None:
            head, tail = ntpath.split(fout)
            fin = tail or ntpath.basename(head)

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
        try:
            self.client.delete_object(
                Bucket=self.config['credentials']['bucket'],
                Key=fout
            )
        except ClientError as e:
            print (e)
        else:
            print("Delete successfull")


    def move(self, fout_src, fout_tgt):
        pass

    def iter(self, pattern=None):
        response = self.client.list_objects_v2(Bucket=self.config['credentials']['bucket'])
        assert response['ResponseMetadata']['HTTPStatusCode'] == 200,\
                'List object failed, {}'.format(response)

        for obj in response.get('Contents', []):
            yield obj

    def list(self, pattern=None):
        fouts = []
        for obj in self.iter():
            fouts.append(obj)
        return fouts

if __name__ == "__main__":
    client = S3Client('config.idcloudhost.yml')
    fouts = client.list()

    # test list
    print("\n".join([o['Key'] for o in fouts]))

    # test download
    # client.download(fouts[0]['Key'])

    # test upload
    # url = client.upload('/home/pi/sample.jpeg', fout='encrypt.jpg', w_public=True, w_encrypt=True)
    # print(url)

    # test delete
    print("Delete {}".format(fouts[-1]['Key']))
    client.delete(fouts[-1]['Key'])
