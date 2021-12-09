import os
import logging
import json
import boto3
from botocore.exceptions import ClientError
from error import ErrorOrderTransaction, ErrorOrderProcess
from aws_xray_sdk.core import patch_all

logger = logging.getLogger()
logger.setLevel(logging.INFO)
patch_all()

ORDER_STATE_MACHINE_ARN = os.getenv('ORDER_SAGA_STATE_MACHINE_ARN')
sfn = boto3.client('stepfunctions')


def extract_order_request(event):
    request_event = json.loads(event['body'])
    logger.info('extract_order_request: {}'.format(request_event))
    return request_event


def start_order_transaction(order_request):
    try:
        order_request_json = json.dumps(order_request)
        response = sfn.start_execution(
            stateMachineArn=ORDER_STATE_MACHINE_ARN,
            input=order_request_json
        )
        logger.info('start_execution response: {}'.format(response))
        return response['executionArn']
    except ClientError as e:
        error_message = 'start_order_transaction Error: {}'.format(e)
        logging.exception(error_message)
        raise ErrorOrderTransaction(error_message)


def response_body(request_event, execution_arn='', message=''):
    data = dict(order_id=request_event['order_id'],
                transaction_id=execution_arn,
                message=message)
    return json.dumps(data)


def lambda_handler(event, context):
    """
    Order Request API from API Gateway
    :return: Success or Error + Reason
    """
    logger.info('Order Request: event: {}'.format(event))
    request_event = extract_order_request(event)

    try:
        execution_arn = start_order_transaction(request_event)
        body = response_body(request_event, execution_arn)

        return {
            "statusCode": 200,
            "body": body
        }

    except ErrorOrderTransaction as e:
        logger.exception('Order Transaction Error: {}'.format(vars(e)))
        body = response_body(request_event=request_event,
                             message='REQUEST_ERROR')
        return {
            "statusCode": 200,
            "body": body
        }

    except Exception as e:
        logger.exception('Order Request Exception: {}'.format(vars(e)))
        raise e
