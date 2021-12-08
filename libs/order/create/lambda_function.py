import logging
from aws_xray_sdk.core import patch_all
from pynamodb.exceptions import PutError
from model import Order
from error import ErrorOrderCreate, AlreadyRunning
from test import test_state_machine

logger = logging.getLogger()
logger.setLevel(logging.INFO)
patch_all()


def extract_event(event):
    return event


def order_item(order_event):
    logger.info('order_item: {}'.format(order_event))
    try:
        order = Order(order_event['order_id'],
                      order_date=order_event['order_date'],
                      customer_id=order_event['customer_id'],
                      items=order_event['items'],
                      order_status='APPROVED_PENDING')
        return order
    except Exception as e:
        logging.error('Error: order_item: {}'.format(vars(e)))
        raise e


def create_order(order_event):
    try:
        order = order_item(order_event)
        order.save(
            Order.order_id.does_not_exist()
        )
        return
    except PutError as e:
        cause = e.cause.response['Error'].get('Code')

        # Idempotency
        if cause == 'ConditionalCheckFailedException':
            error_message = 'Order transaction is already running. ' \
                            'OrderID: {}'.format(order_event['order_id'])
            logger.warning(error_message)
            raise AlreadyRunning(error_message)

        error_message = 'save_order() Error: {}'.format(vars(e))
        logger.exception(error_message)
        raise ErrorOrderCreate(error_message)


def lambda_handler(event, context):
    logger.info('OrderCreate() event: {}'.format(event))
    order_event = extract_event(event)

    try:
        create_order(order_event)
        test_state_machine(order_event)

        logger.info('OrderCreated APPROVED_PENDING '
                    'event: {}'.format(order_event))

        # raise ErrorOrderCreate
        return order_event

    except AlreadyRunning as e:
        raise e
    except ErrorOrderCreate as e:
        raise e
    except Exception as e:
        logger.exception('Order Create Exception: {}'.format(vars(e)))
        raise ErrorOrderCreate
