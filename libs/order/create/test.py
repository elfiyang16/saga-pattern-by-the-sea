from error import ErrorOrderCreate, AlreadyRunning


def test_state_machine(order_event):
    if 'OC1-' in order_event['order_id']:
        raise ErrorOrderCreate('testing scenario')
    if 'OC2-' in order_event['order_id']:
        raise AlreadyRunning('testing scenario')
    if 'OC3-' in order_event['order_id']:
        raise Exception('testing scenario')
