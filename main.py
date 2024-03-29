"""
Wrapper for AWS CLI command. 
If needed, will prompt for a new MFA OTP tokencode and update AWS credentials for profile.
"""
import logging
import os
import subprocess
import sys

import boto3
import botocore.session
import botocore.exceptions

import mylogger

logger = logging.getLogger(__name__)


def valid_mfa_session_token(aws_profile):
    """
    Checks AWS profile for a valid session token
    """
    try:
        session = boto3.session.Session(profile_name=aws_profile)
        client = session.client("sts")
        client.get_caller_identity()
        return True
    except botocore.exceptions.ClientError:
        return False


def set_mfa_credentials():
    """
    Updates AWS profile configuration with new STS session token
    """
    logger.info("AWS STS session token has expired or is not valid")
    session = botocore.session.Session()
    mfa_serial = session.get_scoped_config()["mfa_serial"]
    sts = boto3.client("sts")

    token_code = input("Input your one-time MFA token code: ")
    response = sts.get_session_token(SerialNumber=mfa_serial, TokenCode=token_code)

    session_credentials = {
        "AWS_ACCESS_KEY_ID": response["Credentials"]["AccessKeyId"],
        "AWS_SECRET_ACCESS_KEY": response["Credentials"]["SecretAccessKey"],
        "AWS_SESSION_TOKEN": response["Credentials"]["SessionToken"],
    }

    for variable, value in session_credentials.items():
        subprocess.run(
            ["aws", "--profile", "mfa", "configure", "set", variable, value], check=True
        )


def main(aws_cli_args):
    """
    Prompts for MFA token code if invalid MFA session token and
    runs a shell command with AWS CLI arguments
    """
    # TODO: argparser for AWS profile name
    aws_profile = "mfa"

    # Check for existing session
    if not valid_mfa_session_token(aws_profile):
        set_mfa_credentials()

    aws_cli_cmd = ["aws", "--profile", aws_profile]
    aws_cli_cmd.extend(aws_cli_args)

    subprocess.run(aws_cli_cmd, env=os.environ.copy(), check=True)


if __name__ == "__main__":
    mylogger.setup_logging()
    main(sys.argv[1:])
