from error import ErrorInventoryReserve, InventoryRanShort


def test_state_machine(order_event):
    if 'IRS1-' in order_event['order_id']:
        raise InventoryRanShort('testing scenario')
    if 'IRS2-' in order_event['order_id']:
        raise ErrorInventoryReserve('testing scenario')
    if 'IRS3-' in order_event['order_id']:
        raise Exception('testing scenario')
