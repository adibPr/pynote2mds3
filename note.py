#!/usr/bin/env python
# sys module
import os
import sys
import json
import subprocess
import shlex
import shutil
import re

# third parties module
import nbformat

# local module
path_this = os.path.abspath(os.path.dirname(__file__))
from util import get_logger
logger = get_logger ('note')


class Note(object):
    default_config = {
            # working directory (export, regexes, etc)
            'tmp_dir':  '.tmp',
            # temporary output prefix name, use for --output in nbconvert
            'tmp_output': 'out',
            # base path for referencing local image. If we have image ../../a.png,
            # the exact file will depend on the location we start the notebook. 
            # this is that location. The default will be terminal current location
            'base_path_note': '.'

    }

    def __init__(self, s3_client, config={}):
        self.config = Note.default_config
        self.config.update(config)

        self.s3_client = s3_client

    def upload(self, src, s3_prefix=''):
        tgt = s3_prefix + os.path.basename(src)
        tgt_link = self.s3_client.upload(src, tgt, w_public=True)
        return tgt_link

    def replace_url(self, content, src, target):
        return re.sub (re.escape (src), target, content)

    def list_img(self, md_content):
        # regex image pattern
        img = re.findall (r'\!\[.*\]\((.*?)\)', md_content)
        logger.debug('Found {} images'.format(len(set(img))))

        img_status = []
        for i in set(img): # to prevent the same image replaced twice
            # check for web links
            if "http" in i or "www" in i: 
                img_type = 'web'
            # all files in out_files are generated
            elif i.startswith (self.config['tmp_output'] + '_files'):
                img_type = 'generated'
            else:
                img_type = 'local'

            img_status.append({
                'link': i,
                'type': img_type
            })
            logger.debug('img: {}, type: {}'.format(i, img_type))
        return img_status

    def convert(self, fnote, fmd=None, s3_prefix=''):
        logger.info('Converting {}'.format(fnote))

        logger.debug('Validity check')
        valid_status = self.test_validity(fnote)
        if valid_status['status'] != 1:
            raise Exception(valid_status['reason'])

        try:
            # call nb convert command to convert
            logger.debug('Calling nbconvert')
            cmd = ["jupyter-nbconvert",  
                    shlex.quote (fnote), 
                    "--to=markdown", 
                    "--output={}".format(self.config['tmp_output']),
                    "--output-dir={}".format (self.config['tmp_dir'])
                ]
            status = subprocess.run(cmd)
            logger.debug("Return code: {}".format(status.returncode))

            assert status.returncode==0, "nbconvert process failed"

            # open the output, and list the image in there
            with open(os.path.join(self.config['tmp_dir'], "out.md")) as f_:
                content = f_.read()
                images = self.list_img(content)

                # upload the local and generated images only
                for i in images:
                    if i['type'] == 'web':
                        continue
                    elif i['type'] == 'generated':
                        img_path = os.path.join(self.config['tmp_dir'], i['link'])
                    else:
                        img_path = os.path.join(self.config['base_path_note'], i['link'])

                    assert os.path.isfile(img_path) is True, \
                            'File {} can\'t be found!'.format(img_path)

                    logger.debug("Uploading {}".format(img_path))
                    img_s3_link = self.upload(img_path, s3_prefix)

                    logger.debug("Replacing URL {}".format(img_path))
                    content = self.replace_url(content, i['link'], img_s3_link)

            # dumping content to final output
            if fmd is None:
                # default fmd is current notes with changing extension
                base = os.path.splitext(os.path.basename(fnote))[0]
                fmd = base + '.md'

            logger.debug('Write to {}'.format(fmd))
            with open (fmd, 'w') as f_:
                f_.write(content)

            logger.info("Success!")


        except Exception as e:
            logger.error("Failed!")
            logger.error(e)

        finally:
            self.cleanup()


    def cleanup (self):
        # remove tmp folder
        logger.debug("Removing {}".format(self.config['tmp_dir']))
        try:
           shutil.rmtree (self.config['tmp_dir'])
        except Exception as e:
            logger.error("Exception found!")
            logger.error(e)
            raise e

    def test_validity(self, fnote):
        logger.debug("File extension check")
        if not fnote.endswith ('.ipynb'):
            return {
                    "status": -1, 
                    "reason": "It does not have ipynb extension"
                }
        note = nbformat.read(fnote, as_version=4)

        logger.debug("First cell check")
        if not note['cells'][0]['cell_type'] == 'raw':
            return {
                    "status": -1,
                    "reason": "first cell is not raw"
                }

        first_cell = note['cells'][0]['source'].split('\n')
        if first_cell[0].strip () != "---" and first_cell[-1].strip () != "---":
            return {
                    "status": -1,
                    "reason": "No --- the in first and last line"
                }
                
        logger.debug("Metadata check")
        metadata_str = first_cell[1:-1]
        metadata = {}
        for line in metadata_str:
            line_splitted = line.strip ().split (':')
            if line_splitted:
                metadata[line_splitted[0].strip ()] = " ".join (line_splitted[1:]).strip () # in case the title has :

        if set (["author", "title"]) - set (metadata.keys ()):
            return {
                    "status": -1,
                    "reason": "No author and title is provided"
                }

        logger.debug ("Metadata info: ")
        for key in metadata:
            logger.debug ("\t{}: {}".format (key, metadata[key]))
        if 'draft' not in metadata or metadata['draft'].lower () != 'false':
            return {
                    "status": -1,
                    "reason": "Notes is in draft"
                } 

        return {
                "status": 1,
                "reason": "OK" 
            }

if __name__ == '__main__':
    from s3 import S3Client
    s3_client = S3Client(os.path.join(path_this, './config.yml'))
    note = Note(s3_client)
    note.convert(os.path.join(path_this, './sample/index.ipynb'), s3_prefix='blog/index_')

