import cv2

import boto3
import urllib

import os

import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)

OUTPUT_BUCKET = str(os.getenv('OUTPUT_BUCKET'))
KP_METHOD = str(os.getenv('KP_METHOD'))
BORDER_TYPE = str(os.getenv('BORDER_TYPE'))
BORDER_SIZE = int(os.getenv('BORDER_SIZE'))

MAX_SIZE = 240 * 1024 * 1024

s3 = boto3.client('s3')

# --------------- Helper Functions to call AWS APIs ------------------

def download_file(bucket, key):
    name = get_tmp_file_from_key(key)
    logger.info("Downloading s3://{}/{} to {}".format(bucket, key, name))
    s3.download_file(bucket, key, name)
    logger.info("Downloaded video file to {}".format(name))
    return name

def upload_file(bucket, key, local_path):
    logger.info("Uploading {} to s3://{}/{}".format(local_path, bucket, key))
    response = s3.upload_file(local_path, bucket, key)
    logger.info("Uploaded {} to s3://{}/{}".format(local_path, bucket, key))
    logger.debug(response)
    return response

# --------------- Other Helper Functions --------

from pathlib import Path

def get_tmp_file_from_key(key):
    name = Path(key).name
    return '/tmp/{}'.format(name)

# --------------- Main handler ------------------

VIDSTAB_ERROR = None

try:
    from vidstab import VidStab
except ImportError as e:
    logger.critical("Could not import VidStab")
    VIDSTAB_ERROR = e

def lambda_handler(event, context):
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.unquote_plus(event['Records'][0]['s3']['object']['key'].encode('utf8'))

    if VIDSTAB_ERROR is not None:
        raise VIDSTAB_ERROR

    try:
        in_path = download_file(bucket, key)
        out_path = "/tmp/out_{}".format(key)
        head_response = s3.head_object(Bucket=bucket, Key=key)
        size = head_response['ContentLength']
        content_type = head_response['ContentType']
        if size <= MAX_SIZE:
            # Do the stabilization
            if content_type[0:5] == "video":
                stabilizer = VidStab(kp_method=KP_METHOD)
                if BORDER_TYPE == "black":
                    stabilizer.stabilize(input_path=in_path,
                                         output_path=out_path,
                                         border_type=BORDER_TYPE,
                                         border_size=BORDER_SIZE)
                else:
                    stabilizer.stabilize(input_path=in_path,
                                         output_path=out_path,
                                         border_type=BORDER_TYPE)
                return upload_file(OUTPUT_BUCKET, key, out_path)
            else:
                raise IOError("Object {} from bucket {} ".format(key, bucket) +
                              "is not a video.")
        else:
            raise IOError("Object {} from bucket {} ".format(key, bucket) +
                          "exceeds max allowable size for stabilization.")

    except IOError as e:
        logger.exception("IOError occurred during lambda handling")
        raise e
    except Exception as e:
        logger.exception("Error processing object {} from bucket {}. ".format(key, bucket) +
                         "Make sure your object and bucket exist and your bucket is in the same region as this function.")
        raise e
