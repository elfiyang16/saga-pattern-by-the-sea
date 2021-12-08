import uuid
import datetime
import logging
from aws_xray_sdk.core import patch_all
from pynamodb.exceptions import PutError
from model import Payment
from error import ErrorPaymentDebit, DebitLimitExceeded
from test import test_state_machine

logger = logging.getLogger()
logger.setLevel(logging.INFO)
patch_all()


def extract_order(event):
    return event


def order_total(order):
    total = 0.0
    items = order['items']
    for item in items:
        total += item['qty'] * item['unit_price']
    return round(total, 2)


def create_transaction(peyment, transaction_type):
    # This transaction is for Compensating Transaction
    peyment.transaction_id = str(uuid.uuid4())
    peyment.transaction_date = str(datetime.datetime.utcnow())
    peyment.transaction_type = transaction_type
    return peyment


def payment_item(order_event):
    payment = Payment(
        order_id=order_event['order_id'],
        merchant_id='merchant_xxxxxxxx',
        payment_amount=order_total(order_event),
    )

    payment = create_transaction(payment, "DEBITED")
    return payment


def debit_payment(order_event):
    try:
        payment = payment_item(order_event)
        payment.save()
        return payment
    except PutError as e:
        error_message = 'save_payment() Error: {}'.format(vars(e))
        logging.exception(error_message)
        raise ErrorPaymentDebit(error_message)


def payment_attributes(order_event, payment):
    order_event['payment'] = payment.attribute_values
    return order_event


def lambda_handler(event, context):
    logger.info('PaymentDebit: event: {}'.format(event))
    order_event = extract_order(event)

    try:

        payment = debit_payment(order_event)

        order_event = payment_attributes(order_event, payment)

        test_state_machine(order_event)

        logger.info('PaymentDebit() event: {}'.format(order_event))
        return order_event

    except DebitLimitExceeded as e:
        raise e
    except ErrorPaymentDebit as e:
        raise e
    except Exception as e:
        logger.exception(vars(e))
        raise ErrorPaymentDebit
