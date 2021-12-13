from error import ErrorOrderReject


def test_state_machine(order_event):
    if 'OR1-' in order_event['order_id']:
        raise ErrorOrderReject('testing scenario')
    if 'OR2-' in order_event['order_id']:
        raise Exception('testing scenario')
