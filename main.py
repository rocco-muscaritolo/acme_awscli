"""
Wrapper for AWS CLI command. 
If needed, will prompt for a new MFA OTP tokencode and update AWS credentials for profile.
"""

import logging.config
import os
import subprocess
import sys

import boto3
import botocore.session
import botocore.exceptions


logger = logging.getLogger("acme_awscli")
logging_config = {}


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

    print("AWS STS session token has expired or is not valid)")
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

    # # Set ENV variables for AWS session
    # os.environ["AWS_ACCESS_KEY_ID"] = response["Credentials"]["AccessKeyId"]
    # os.environ["AWS_SECRET_ACCESS_KEY"] = response["Credentials"]["SecretAccessKey"]
    # os.environ["AWS_SESSION_TOKEN"] = response["Credentials"]["SessionToken"]

    # for variable in os.environ.copy():
    #     if variable in [
    #         "AWS_ACCESS_KEY_ID",
    #         "AWS_SECRET_ACCESS_KEY",
    #         "AWS_SESSION_TOKEN",
    #     ]:
    #         value = os.environ[variable]
    #         subprocess.run(
    #             ["aws", "--profile", "mfa", "configure", "set", variable, value],
    #             check=True,
    #         )


def main(aws_cli_args):
    """
    Prompts for MFA token code if invalid MFA session token and
    runs a shell command with AWS CLI arguments
    """

    logging.config.dictConfig(config=logging_config)
    logger.addHandler(logging.StreamHandler())

    logger.debug("debug message")
    logger.info("info message")
    logger.warning("warning message")
    logger.error("error message")
    logger.critical("critical message")

    # TODO: argparser for AWS profile name
    aws_profile = "mfa"

    # Check for existing session
    if not valid_mfa_session_token(aws_profile):
        set_mfa_credentials()

    aws_cli_cmd = ["aws", "--profile", aws_profile]
    aws_cli_cmd.extend(aws_cli_args)

    subprocess.run(aws_cli_cmd, env=os.environ.copy(), check=True)


if __name__ == "__main__":
    main(sys.argv[1:])
