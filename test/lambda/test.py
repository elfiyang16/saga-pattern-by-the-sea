import os
import uuid
import datetime
import random
import logging
import json
import boto3
from aws_xray_sdk.core import patch_all

logger = logging.getLogger()
logger.setLevel(logging.INFO)
patch_all()

APIGATEWAY_NAME = 'serverless-saga'
API_PATH = '/order'
apigw = boto3.client('apigateway')


"""
Sample Order Request Event
{
  "order_id": "40063fe3-56d9-4c51-b91f-71929834ce03",
  "order_date": "2018-10-19T10:50:16+08:00",
  "customer_id": "8d04ea6f-c6b2-4422-8550-839a16f01feb",
  "items": [{
      "item_id": "123",
      "qty": 1.0,
      "description": "Cart item 1",
      "unit_price": 19.99
    },
    {
      "item_id": "234",
      "qty": 1.0,
      "description": "Cart item 2",
      "unit_price": 23.98
    },
    {
      "item_id": "345",
      "qty": 2.0,
      "description": "Cart item 3",
      "unit_price": 6.50
    }
  ]
}
"""


"""
Each api test_state_machine() raise an exception with a prefix of PREFIX_EXCEPTION_LIST
in order to test the state transition of StateMachine.
"""
PREFIX_EXCEPTION_LIST = [
    '',
    'OA1-',
    'OC1-',
    'OC2-',
    'OC3-',
    'PD1-',
    'PD2-',
    'PD3-',
    'IRS1-',
    'IRS2-',
    'IRS3-',
    'IRS2-IRL1-',
    'IRS3-IRL2-',
    'IRS3-PC1-',
    'IRS3-PC2-',
    'IRS3-PC3-',
    'IRS2-PC1-',
    'IRS1-PC1-',
    'PD2-PC1-',
    'PD1-PC1-',
    'PD1-OR1-',
    'PD1-OR2-'
]


def choice_order_id(i):
    uuid_random = str(uuid.uuid4())
    order_id = PREFIX_EXCEPTION_LIST[i] + uuid_random
    return order_id


def create_test_items():
    items = list()
    count = random.randint(1, 3)
    for i in range(count):
        item = dict(
            item_id=''.join(random.sample('0123456789', 5)),
            qty=random.randint(1, 3),
            description='item {}'.format(
                ''.join(random.sample('0123456789', 1))),
            unit_price=random.randint(100, 10000)/100
        )
        items.append(item)
    return items


def order_body(i):
    body = dict(
        order_id=choice_order_id(i),
        order_date=str(datetime.datetime.utcnow()),
        customer_id=str(uuid.uuid4()),
        items=create_test_items()
    )
    return json.dumps(body)


def get_api_id(apigateway_name):
    apis = apigw.get_rest_apis()
    api_id = ''
    for api in apis['items']:
        if api['name'] == apigateway_name:
            api_id = api['id']
            break
    return api_id


def get_resource_id(api_id):
    resources = apigw.get_resources(restApiId=api_id)
    resource_id = ''
    for item in resources['items']:
        if item['path'] == API_PATH:
            resource_id = item['id']
            break
    return resource_id


def invoke_test_api(api_id, resource_id):
    length = len(PREFIX_EXCEPTION_LIST)
    for i in range(length):
        apigw.test_invoke_method(
            restApiId=api_id,
            resourceId=resource_id,
            httpMethod='POST',
            body=order_body(i)
        )
    return


def lambda_handler(event, context):
    """
    Test for Order transaction
    """
    logger.info('Start test for Order Saga Transaction')
    api_id = get_api_id(APIGATEWAY_NAME)
    resource_id = get_resource_id(api_id)
    invoke_test_api(api_id, resource_id)
    return
