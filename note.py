#!/usr/bin/env python
# sys module
import os
import sys
import json

# third parties module
import nbformat

# local module
from util import get_logger
logger = get_logger ('note')


class Note(object):

    def __init__(self, s3_client, config={}):
        pass

    def _upload(self, obj):
        pass

    def _replace_url(self, cell, obj):
        pass

    def convert(self, fnote):
        result = self.test_validity(fnote)
        print(result)


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
    s3_client = S3Client('./config.yml')
    note = Note(s3_client)
    note.convert('./sample/index.ipynb')

