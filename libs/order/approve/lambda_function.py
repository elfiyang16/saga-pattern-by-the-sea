import logging
from pynamodb.exceptions import UpdateError
from aws_xray_sdk.core import patch_all
from model import Order
from error import ErrorOrderApprove, ErrorOrderUpdate
from test import test_state_machine

logger = logging.getLogger()
logger.setLevel(logging.INFO)
patch_all()


def extract_order(event):
    return event


def approve_order(order_event):
    status = 'APPROVED'
    try:
        order = Order(order_event['order_id'])
        order.update(
            actions=[
                Order.order_status.set(status)
            ]
        )
        return

    except UpdateError as e:
        error_message = 'update_order Error: {}'.format(vars(e))
        logging.exception(error_message)
        raise ErrorOrderUpdate(error_message)


def lambda_handler(event, context):

    logger.info('OrderApprove() event: {}'.format(event))
    order_event = extract_order(event)

    try:
        approve_order(order_event)

        test_state_machine(order_event)

        logger.info('OrderApproval APPROVED '
                    'event: {}'.format(order_event))
        return order_event

    except ErrorOrderUpdate as e:
        raise e
    except Exception as e:
        logger.error(vars(e))
        raise ErrorOrderApprove
