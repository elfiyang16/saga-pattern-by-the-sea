import uuid
import datetime
import logging
from aws_xray_sdk.core import patch_all
from pynamodb.exceptions import PutError
from model import Inventory
from error import ErrorInventoryReserve, InventoryRanShort
from test import test_state_machine


logger = logging.getLogger()
logger.setLevel(logging.INFO)
patch_all()


def extract_order(event):
    return event


def create_transaction(inventory, transaction_type):
    inventory.transaction_id = str(uuid.uuid4())
    inventory.transaction_date = str(datetime.datetime.utcnow())
    inventory.transaction_type = transaction_type
    return inventory


def inventory_item(order_event):
    inventory = Inventory(
        order_id=order_event['order_id'],
        order_items=order_event['items']
    )
    inventory = create_transaction(inventory, "RESERVED")
    return inventory


def reserve_inventory(order_event):
    inventory = inventory_item(order_event)

    try:
        inventory.save()
        return inventory

    except PutError as e:
        cause = e.cause.response['Error'].get('Code')

        if cause == 'ConditionalCheckFailedException':
            error_message = 'Inventory ran short. ' \
                            'OrderID: {}'.format(order_event['order_id'])
            logger.warning(error_message)
            raise InventoryRanShort(error_message)

        error_message = 'save_inventory() Error: {}'.format(vars(e))
        logger.exception(error_message)
        raise ErrorInventoryReserve(error_message)


def set_inventory_attributes(order_event, inventory):
    order_event['inventory'] = inventory.attribute_values
    return order_event


def lambda_handler(event, context):

    logger.info('Inventory Reserve: event: {}'.format(event))
    order_event = extract_order(event)

    try:
        inventory = reserve_inventory(order_event)

        test_state_machine(order_event)

        order_event = set_inventory_attributes(order_event, inventory)
        logger.info('InventoryReserve() event: {}'.format(order_event))
        return order_event

    except InventoryRanShort as e:
        raise e
    except ErrorInventoryReserve as e:
        raise e
    except Exception as e:
        logger.error(e)
        raise ErrorInventoryReserve
