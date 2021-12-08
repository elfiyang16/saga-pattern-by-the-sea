from error import ErrorPaymentDebit, DebitLimitExceeded


def test_state_machine(order_event):
    if 'PD1-' in order_event['order_id']:
        raise DebitLimitExceeded('testing scenario')
    if 'PD2-' in order_event['order_id']:
        raise ErrorPaymentDebit('testing scenario')
    if 'PD3-' in order_event['order_id']:
        raise Exception('testing scenario')
