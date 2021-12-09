from error import ErrorPaymentCredit, ErrorPaymentException


def test_state_machine(order_event):
    if 'PC1-' in order_event['order_id']:
        raise ErrorPaymentCredit('testing scenario')
    if 'PC2-' in order_event['order_id']:
        raise ErrorPaymentException('testing scenario')
    if 'PC3-' in order_event['order_id']:
        raise Exception('testing scenario')
