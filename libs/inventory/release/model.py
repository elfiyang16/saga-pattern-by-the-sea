from pynamodb.models import Model
from pynamodb.attributes import (
    UnicodeAttribute,
    ListAttribute
)
from pynamodb.indexes import GlobalSecondaryIndex, AllProjection


class OrderIdIndexForInventory(GlobalSecondaryIndex):
    class Meta:
        index_name = 'order_id_index'
        projection = AllProjection()
        read_capacity_units = 1
        write_capacity_units = 1

    transaction_id = UnicodeAttribute(hash_key=True)
    transaction_type = UnicodeAttribute(range_key=True)


class Inventory(Model):
    class Meta:
        table_name = 'Inventory'
        region = 'eu-west-1'
        max_retry_attempts = 8
        base_backoff_ms = 297

    transaction_id = UnicodeAttribute(hash_key=True)
    transaction_date = UnicodeAttribute()
    transaction_type = UnicodeAttribute()
    order_id = UnicodeAttribute()
    order_items = ListAttribute()
    order_id_index = OrderIdIndexForInventory()
