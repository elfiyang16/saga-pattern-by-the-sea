from error import ErrorInventoryRelease, ErrorPaymentException


def test_state_machine(order_event):
    if 'IRL1-' in order_event['order_id']:
        raise ErrorInventoryRelease('testing scenario')
    if 'IRL2-' in order_event['order_id']:
        raise Exception('testing scenario')
