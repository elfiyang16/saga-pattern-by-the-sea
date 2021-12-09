from error import ErrorOrderUpdate, ErrorOrderApprove


def test_state_machine(order_event):
    if 'OA1-' in order_event['order_id']:
        raise ErrorOrderUpdate('testing scenario')
    if 'OA2-' in order_event['order_id']:
        raise Exception('testing scenario')
