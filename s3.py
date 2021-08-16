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

# local module
from util import get_logger
logger = get_logger ('s3')


class S3Client:
    """
    Some terminologies:
        fout: file name "out" there, i.e in the server (S3), or in S3 term, key.
        fin: file name "in" here, i.e local machine.
    """

    def __init__(self, config_path):
        logger.debug('Initiate connection')
        self.config = self._load_config(config_path)
        self.client = boto3.client("s3", 
                    aws_access_key_id=self.config['credentials']['secret_key'],
                    aws_secret_access_key=self.config['credentials']['access_key'],
                    endpoint_url=self.config['credentials']['endpoint_url']
                )
        logger.debug('.. Done')

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

    def _get_url(self, fout):
        # adding bucket name before host name
        addr = re.sub(
                    r"https\://", 
                    r"https://" + self.config['credentials']['bucket'] + r".", 
                    self.config['credentials']['endpoint_url']
                )
        return parse.urljoin(addr, parse.quote(fout))


    def upload(self, fin, fout=None, w_encrypt=False, w_public=False):
        logger.info('Uploading {}'.format(fin))

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
            logger.error('Failed!')
            logger.error(e)
            sys.exit()
        else:
            logger.debug("Upload successfull")

        logger.info('.. Done')
        return self._get_url(fout)

    def download(self, fout, fin=None, w_encrypt=False):
        logger.info('Downloading {}'.format(fout))

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
            logger.error('Failed!')
            logger.error(e)
            sys.exit()
        else:
            logger.debug("Download successfull")

        logger.info('.. Done')

    def delete(self, fout):
        logger.info('Deleting {}'.format(fout))
        try:
            self.client.delete_object(
                Bucket=self.config['credentials']['bucket'],
                Key=fout
            )
        except ClientError as e:
            logger.error('Failed!')
            logger.error(e)
            sys.exit()
        else:
            logger.debug("Delete successfull")

        logger.info('.. Done')


    def move(self, fout_src, fout_tgt):
        logger.info('Moving {} to {}'.format(fout_src, fout_tgt))

        # we can't rename an object, so we have to copy and delete the old one
        try:
            response = self.client.copy_object(
                    Bucket=self.config['credentials']['bucket'],
                    CopySource={'Bucket': self.config['credentials']['bucket'], 'Key': fout_src},
                    Key=fout_tgt
                )

            assert response['ResponseMetadata']['HTTPStatusCode'] == 200,\
                    'Copy object failed: {}'.format(response)

            self.delete(fout_src)

        except Exception as e:
            logger.error('Failed!')
            logger.error(e)
            sys.exit()

        else:
            logger.debug ("Move Successfull")

        logger.info('.. Done')

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
