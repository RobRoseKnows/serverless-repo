import hashlib
import hmac
import json
import os

import boto3

SECRET = os.getenv('SECRET')
SNS_TOPIC = os.getenv('SNS_TOPIC')

SNS = boto3.client('sns')

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
    digest = hmac.new(CONFIG['SECRET'].encode(), request.raw_body.encode(), hashlib.sha1) \
        .hexdigest()
    if not hmac.compare_digest(digest.encode(), sha1.encode()):
        raise UnauthorizedError()