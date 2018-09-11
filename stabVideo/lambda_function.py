import cv2

import boto3
import urllib

import os

OUTPUT_BUCKET = str(os.getenv('OUTPUT_BUCKET'))
KP_METHOD = str(os.getenv('KP_METHOD'))
BORDER_TYPE = str(os.getenv('BORDER_TYPE'))
BORDER_SIZE = int(os.getenv('BORDER_SIZE'))

MAX_SIZE = 240 * 1024 * 1024

s3 = boto3.client('s3')

# --------------- Helper Functions to call AWS APIs ------------------

def download_file(bucket, key):
    name = get_tmp_file_from_key(key)
    s3.download_file(bucket, key, name)
    return name

def upload_file(bucket, key, local_path):
    response = s3.upload_file(local_path, bucket, key)
    return response

# --------------- Other Helper Functions --------

from pathlib import Path

def get_tmp_file_from_key(key):
    name = Path(key).name
    return '/tmp/{}'.format(name)

# --------------- Main handler ------------------

def lambda_handler(event, context):
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.unquote_plus(event['Records'][0]['s3']['object']['key'].encode('utf8'))

    try:

        head_response = s3.head_object(Bucket=bucket, Key=key)
        size = head_response['ContentLength']
        if size <= MAX_SIZE:
            # Do the stabilization
            pass
        else:
            raise IOError("Object {} from bucket {}".format(key, bucket) +
                          "exceeds max allowable size for stabilization.")

    except IOError as e:
        print(e)
        raise e
    except Exception as e:
        print(e)
        print("Error processing object {} from bucket {}. ".format(key, bucket) +
              "Make sure your object and bucket exist and your bucket is in the same region as this function.")
        raise e
