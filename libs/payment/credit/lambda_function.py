import uuid
import json
import datetime
import logging
from aws_xray_sdk.core import patch_all
from pynamodb.exceptions import PutError, QueryError
from model import Payment
from error import ErrorPaymentCredit, ErrorPaymentException
from test import test_state_machine

logger = logging.getLogger()
logger.setLevel(logging.INFO)
patch_all()


def extract_order(event):
    return event


def set_payment_attributes(order_event, payment):
    order_event['payment'] = payment.attribute_values
    return order_event


def get_payment_transaction(order_event):
    try:
        payment = Payment.order_id_index.query(
            order_event['order_id'],
            Payment.transaction_type == 'DEBITED'
        ).next()
        logger.info('payment_transaction: {}'.format(payment))
        return payment
    except QueryError as e:
        error_message = 'get_payment_transaction Error: {}'.format(vars(e))
        logging.exception(error_message)
        raise ErrorPaymentCredit(error_message)
    except StopIteration as e:
        error_message = 'get_payment_transaction() no payment transaction: ' \
                        '{}'.format(order_event['order_id'])
        logging.exception(error_message)
        raise ErrorPaymentException(error_message)


def create_transaction(inventory, transaction_type):
    inventory.transaction_id = str(uuid.uuid4())
    inventory.transaction_date = str(datetime.datetime.utcnow())
    inventory.transaction_type = transaction_type
    return inventory


def credit_item(payment):

    payment = Payment(
        order_id=payment.order_id,
        merchant_id=payment.merchant_id,
        payment_amount=payment.payment_amount
    )
    payment = create_transaction(payment, 'CREDITED')
    return payment


def new_credit_transaction(payment):
    # New compensation transaction
    try:
        payment = credit_item(payment)
        payment.save()
        return payment
    except PutError as e:
        logging.error('save_payment Error: {}'.format(e))


def credit_payment(order_event):
    payment = get_payment_transaction(order_event)
    payment = new_credit_transaction(payment)
    return payment


def lambda_handler(event, context):
    logger.info('Payment Credit: event: {}'.format(event))
    order_event = extract_order(event)
    try:
        payment = credit_payment(order_event)

        test_state_machine(order_event)

        order = set_payment_attributes(order_event, payment)
        logger.info('PaymentCredit() Event: {}'.format(order))
        return order

    except ErrorPaymentCredit as e:
        raise e
    except ErrorPaymentException as e:
        raise e
    except Exception as e:
        logger.error(e)
        raise ErrorPaymentException
