# Adapted from: https://github.com/awslabs/serverless-application-model/blob/master/examples/apps/rekognition-python/lambda_function.py

import boto3
import json
import urllib
import os

from PIL import Image, ImageDraw

print('Loading function')

rekognition = boto3.client('rekognition')
s3 = boto3.client('s3')


# --------------- Helper Functions to call AWS APIs ------------------


def detect_faces(bucket, key):
    response = rekognition.detect_faces(Image={"S3Object": {"Bucket": bucket, "Name": key}})
    return response

def download_file(bucket, key):
    s3.download_file(bucket, key, '/tmp/img')
    return '/tmp/img'

def upload_file(bucket, key, local_path):
    response = s3.upload_file(local_path, bucket, key)
    return response

# --------------- PIL Methods -------------------

def load_image(img_location):
    with open(img_location, 'rb') as f:
        img = Image.open(io.BytesIO(f.read()))
        img_format = img.format

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
    return location

# --------------- Main handler ------------------


def lambda_handler(event, context):
    '''Demonstrates S3 trigger that uses
    Rekognition APIs to detect faces, labels and index faces in S3 Object.
    '''
    #print("Received event: " + json.dumps(event, indent=2))

    # Get the object from the event
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.unquote_plus(event['Records'][0]['s3']['object']['key'].encode('utf8'))
    try:
        # Calls rekognition DetectFaces API to detect faces in S3 object
        response = detect_faces(bucket, key)

        # Print response to console.
        # print(response)

        faces = response['FaceDetails']

        img_loc = download_file(bucket, key)

        img, img_format = load_image(img_loc)

        saved_to = save_image(img, img_format, "/tmp/out")

        return upload_file(os.environ('OUTPUT_BUCKET'), key, saved_to)

    except Exception as e:
        print(e)
        print("Error processing object {} from bucket {}. ".format(key, bucket) +
              "Make sure your object and bucket exist and your bucket is in the same region as this function.")
        raise e
