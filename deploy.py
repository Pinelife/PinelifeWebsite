"""
Run this to deploy Pinelife.net
"""
from __future__ import print_function
import os
import boto3

from io import BytesIO
import gzip
import shutil

BUCKET_NAME = 'pinelife.net'
DO_NOT_DEPLOY = ('deploy.py', 'requirements.txt', 'env', 'README.md', '.git', '.gitignore')
DO_NOT_COMPRESS = ('png', 'jpeg', 'gif', 'ico', 'jpg')
CONTENT_TYPES = {
    'html': 'text/html',
    'css': 'text/css',
    'jpg': 'image/jpeg',
    'jpeg': 'image/jpeg',
    'png': 'image/png',
    'gif': 'image/gif',
    'ico': 'image/x-icon',
    'js': 'application/javascript',
    'json': 'application/json'
}
bucket = boto3.resource('s3').Bucket(BUCKET_NAME)


def get_file_extension(filename):
    return filename.split('.')[-1]


def get_content_type(filename):
    extension = get_file_extension(filename)
    return CONTENT_TYPES.get(extension, 'text/plain')


def upload(path='./'):
    files = (
        os.path.join(path, node) for node in os.listdir(path)
        if os.path.isfile(os.path.join(path, node)) and
        node not in DO_NOT_DEPLOY
    )
    
    folders = (
        os.path.join(path, node) for node in os.listdir(path)
        if os.path.isdir(os.path.join(path, node)) and
        node not in DO_NOT_DEPLOY
    )

    for folder in folders:
        upload(folder)

    for filename in files:
        with open(filename, 'rb') as f:
            content_type = get_content_type(filename)

            file_extension = get_file_extension(filename)
            should_compress = file_extension not in DO_NOT_COMPRESS
            if should_compress:
                f_compressed = BytesIO()
                with gzip.GzipFile(fileobj=f_compressed, mode='wb') as gz:
                    shutil.copyfileobj(f, gz)
                f_compressed.seek(0)
                f_upload = f_compressed
            else:
                f_upload = f

            file_metadata = {
                'ContentType': content_type, 
                'ACL': 'public-read'
            }
            if should_compress:
                file_metadata['ContentEncoding'] = 'gzip'
            key = filename.replace('\\', '/').replace('./', '')
            print('uploading {} as {} to {}...'.format(filename, content_type, key), end='')
            bucket.upload_fileobj(f_upload, key, file_metadata)
            print('done')

if __name__ == '__main__':
    upload()
