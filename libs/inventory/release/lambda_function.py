import uuid
import json
import datetime
import logging
from aws_xray_sdk.core import patch_all
from pynamodb.exceptions import PutError, QueryError
from model import Inventory
from error import ErrorInventoryRelease, ErrorPaymentException
from test import test_state_machine

logger = logging.getLogger()
logger.setLevel(logging.INFO)
patch_all()


def extract_order(event):
    return event


def get_inventory_transaction(order):
    try:
        inventory = Inventory.order_id_index.query(
            order['order_id'],
            Inventory.transaction_type == 'RESERVED'
        ).next()

        logger.info('query Inventory: '
                    '{}'.format(inventory.attribute_values))
        return inventory
    except QueryError as e:
        error_message = 'get_inventory_transaction Error: {}'.format(e)
        logging.exception(error_message)
        raise ErrorInventoryRelease(error_message)
    except StopIteration as e:
        error_message = 'get_payment_transaction() no inventory transaction: ' \
                        '{}'.format(order['order_id'])
        logging.exception(error_message)
        raise ErrorPaymentException(error_message)


def create_transaction(inventory, transaction_type):
    inventory.transaction_id = str(uuid.uuid4())
    inventory.transaction_date = str(datetime.datetime.utcnow())
    inventory.transaction_type = transaction_type
    return inventory


def release_item(inventory):
    logger.info('release_item: {}'.format(vars(inventory)))

    inventory = Inventory(
        order_id=inventory.order_id,
        order_items=inventory.order_items
    )
    inventory = create_transaction(inventory, 'RELEASED')
    return inventory


def new_release_transaction(inventory):
    try:
        inventory = release_item(inventory)
        inventory.save()
        return inventory
    except PutError as e:
        error_message = 'save_inventory Error: {}'.format(e)
        logging.exception(error_message)
        raise ErrorInventoryRelease(error_message)


def release_inventory(order_event):
    inventory = get_inventory_transaction(order_event)
    inventory = new_release_transaction(inventory)

    return inventory


def lambda_handler(event, context):
    logger.info('Inventory Release: event: {}'.format(event))
    order_event = extract_order(event)
    try:
        inventory = release_inventory(order_event)

        test_state_machine(order_event)

        release_transaction = dict(order_id=inventory.order_id,
                                   transaction_id=inventory.transaction_id)
        order_event['Inventory'] = json.dumps(release_transaction)
        logger.info('inventory release - _order_json: {}'.format(order_event))
        return order_event

    except ErrorInventoryRelease as e:
        raise e
    except ErrorPaymentException as e:
        raise e
    except Exception as e:
        logger.error(e)
        raise ErrorPaymentException
