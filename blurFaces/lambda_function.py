# Adapted from: https://github.com/awslabs/serverless-application-model/blob/master/examples/apps/rekognition-python/lambda_function.py
logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)
logger.debug('Loading function...')

import boto3
import json
import urllib
import os
import io

logger.debug('Loading in pillow...')

from PIL import Image, ImageDraw

logger.debug('Loading in boto3 functions.')

rekognition = boto3.client('rekognition')
s3 = boto3.client('s3')


# --------------- Helper Functions to call AWS APIs ------------------


def detect_faces(bucket, key):
    logger.info("Calling rekognition with s3://{}/{}".format(bucket, key))
    response = rekognition.detect_faces(Image={"S3Object": {"Bucket": bucket, "Name": key}})
    logger.info("Called rekognition with s3://{}/{}".format(bucket, key))
    return response

def download_file(bucket, key):
    name = '/tmp/img'
    logger.info("Downloading s3://{}/{} to {}".format(bucket, key, name))
    s3.download_file(bucket, key, name)
    logger.info("Downloaded image to {}".format(name))
    return name

def upload_file(bucket, key, local_path):
    logger.info("Uploading {} to s3://{}/{}".format(local_path, bucket, key))
    response = s3.upload_file(local_path, bucket, key)
    logger.info("Uploaded {} to s3://{}/{}".format(local_path, bucket, key))
    return response

# --------------- PIL Methods -------------------

def load_image(img_location):
    with open(img_location, 'rb') as f:
        img = Image.open(io.BytesIO(f.read()))
        img_format = img.format

    logger.info("Found image with format {}".format(img_format))

    return img, img_format

def draw_rectangles(img, faces):

    draw = ImageDraw.Draw(img)

    for face in faces:
        x0 = face['BoundingBox']['Left']
        y0 = face['BoundingBox']['Top']
        width = face['BoundingBox']['Width']
        height = face['BoundingBox']['Height']
        x1 = x0 + width
        y1 = y0 + height

        draw.rectangle([x0, y0, x1, y1], fill='black', outline='black')

    return img


def save_image(img, img_format, location):
    img.save(location, img_format)
    logger.info("Saved image of format {} to {}".format(img_format, location))
    return location

# --------------- Main handler ------------------


def lambda_handler(event, context):
    '''Demonstrates S3 trigger that uses
    Rekognition APIs to detect faces, labels and index faces in S3 Object.
    '''
    #print("Received event: " + json.dumps(event, indent=2))

    # Get the object from the event
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    try:
        # Calls rekognition DetectFaces API to detect faces in S3 object
        response = detect_faces(bucket, key)

        # Print response to console.
        # print(response)

        faces = response['FaceDetails']

        img_loc = download_file(bucket, key)

        img, img_format = load_image(img_loc)

        img = draw_rectangles(img, faces)

        saved_to = save_image(img, img_format, "/tmp/out")

        return upload_file(os.getenv('OUTPUT_BUCKET'), key, saved_to)

    except Exception as e:
        logger.exception("Error processing object {} from bucket {}. ".format(key, bucket) +
                         "Make sure your object and bucket exist and your bucket is in the same region as this function.")
        raise e
