import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)
logger.debug('Loading function...')

import hashlib
import hmac
import json
import os

import boto3

logger.debug("Loading in environment variables...")
SECRET = os.getenv('SECRET')
SNS_TOPIC = os.getenv('SNS_TOPIC')

logger.debug("Loading SNS client...")
SNS = boto3.client('sns')

logger.debug("Done loading!")

class BadRequestError(Exception):
    pass

class UnauthorizedError(Exception):
    pass

def validate_signature(request):
    """Validate that the signature in the header matches the payload.
    Based off of: https://github.com/LambdaLint/github-webhook-lambda/blob/master/app.py
    """
    if SECRET is None:
        return
    try:
        signature = request.headers['X-Hub-Signature']
        _, sha1 = signature.split('=')
    except (KeyError, ValueError):
        raise BadRequestError()
    digest = hmac.new(CONFIG['SECRET'], request.body, hashlib.sha1).hexdigest()
    if not hmac.compare_digest(digest, sha1):
        raise UnauthorizedError()

def lambda_handler(event, context):
    try:
        validate_signature(event)
        response = SNS.publish(
            TopicArn=SNS_TOPIC,
            Message=event.body,
            MessageAttributes={
                    "X-Github-Delivery": {
                        "DataType": "String",
                        "StringValue": event.headers['X-Github-Delivery']
                    },
                    "X-GitHub-Event": {
                        "DataType": "String",
                        "StringValue": event.headers['X-GitHub-Event']
                    }
                })
    except BadRequestError as e:
        logger.exception("Got a bad request error.")
        return "{'statusCode': 400}"
    except UnauthorizedError as e:
        logger.exception("Got an unauthorized error.")
        return "{'statusCode': 403}"
    except Exception as e:
        logger.exception("Got an unknown error.")
        raise e
