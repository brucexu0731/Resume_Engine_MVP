import boto3
from pathlib import Path
from main import extract_text_from_resume

s3 = boto3.client("s3")

import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    #testing logging
    logger.info("test logging")

    """
    AWS Lambda entry point.

    Expected event:
    {
        "bucket": "my-resume-bucket",
        "key": "uploads/resume.pdf"
    }
    """

    bucket = event["bucket"]
    key = event["key"]

    local_path = Path("/tmp") / Path(key).name

    logger.info(f"Processing resume from S3: {bucket}/{key}")

    # 1. Download from S3
    s3.download_file(
        bucket,
        key,
        str(local_path)
    )

    # 2. Run existing parser
    result = extract_text_from_resume(local_path)

    # 3. Return parsed result
    return result