# AWS Lambda Video Stabilizer

This stabilizes video uploaded to an S3 bucket and then outputs it to another S3
bucket. It uses OpenCV and a [modified version][1] of the `vidstab` python library
to do this.

For the AWS Serverless Application Repo hackathon.

If you're trying to recreate the ZIP file, follow the instructions in [this repo][2]
to create an OpenCV python bindings library for AWS Lambda functions.

The function will throw an error if you try to stabilize a video >240MB because
that's too big for AWS Lambda's `/tmp/` directory to have room for input + output.
Technically that's 32 MB shy of the 512MB capacity of AWS Lambda tmp storage, but
the output file size isn't always the same as the input.

[1]: https://github.com/RobRoseKnows/python_video_stab
[2]: https://github.com/aeddi/aws-lambda-python-opencv