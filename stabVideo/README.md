# AWS Lambda Video Stabilizer

This stabilizes video uploaded to an S3 bucket and then outputs it to another S3
bucket. It uses OpenCV and a [modified version][1] of the `vidstab` python library
to do this.

For the AWS Serverless Application Repo hackathon.

Install the dependencies on your own with:

`pip install -t <your code directory>  git+https://github.com/RobRoseKnows/python_video_stab.git`

The function will throw an error if you try to stabilize a video >240MB because
that's too big for AWS Lambda's `/tmp/` directory to have room for input + output.
Technically that's 32 MB shy of the 512MB capacity of AWS Lambda tmp storage, but
the output file size isn't always the same as the input.

I encourage anyone using this to experiment with different memory and timeout limits. I set the memory
rather low (though far above the max used) in order to reduce the costs. You may be able to get away
with more or less memory depending on your use case. You can change the memory and timeout limits in
the AWS Lambda console!

[1]: https://github.com/RobRoseKnows/python_video_stab