from pynamodb.models import Model
from pynamodb.attributes import (
    UnicodeAttribute,
    JSONAttribute,
    ListAttribute
)


class Order(Model):
    class Meta:
        table_name = 'Order'
        region = 'eu-west-1'
        max_retry_attempts = 8
        base_backoff_ms = 297

    order_id = UnicodeAttribute(hash_key=True)
    order_date = UnicodeAttribute()
    customer_id = UnicodeAttribute()
    order_status = UnicodeAttribute()
    items = ListAttribute()
    payment = JSONAttribute(null=True)
    inventory = JSONAttribute(null=True)
