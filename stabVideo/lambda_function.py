import cv2

import boto3
import urllib

MAX_SIZE = 240 * 1024 * 1024

s3 = boto3.client('s3')

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
