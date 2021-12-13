import logging
from aws_xray_sdk.core import patch_all
from model import Order
from pynamodb.exceptions import UpdateError
from error import ErrorOrderReject, ErrorOrderUpdate
from test import test_state_machine

logger = logging.getLogger()
logger.setLevel(logging.INFO)
patch_all()


def extract_order(event):
    return event


def reject_order(order_event):
    status = 'REJECTED'
    try:
        order = Order(order_event['order_id'])
        order.update(
            actions=[
                Order.order_status.set(status)
                # Order.cause.set(order_event['error']['Error'])
            ]
        )
        return
    except UpdateError as e:
        error_message = 'update_order Error: {}'.format(vars(e))
        logging.exception(error_message)
        raise ErrorOrderUpdate(error_message)


def set_error_message(order_event):
    order_event['cause'] = order_event['error']['Error']
    return order_event


def lambda_handler(event, context):
    logger.info('OrderReject() event: {}'.format(event))
    order_event = extract_order(event)

    try:
        reject_order(order_event)

        test_state_machine(order_event)

        order_event = set_error_message(order_event)
        return order_event

    except ErrorOrderUpdate as e:
        raise ErrorOrderReject
    except Exception as e:
        logger.error(e)
        raise ErrorOrderReject
