from pynamodb.models import Model
from pynamodb.attributes import (
    UnicodeAttribute,
    NumberAttribute
)
from pynamodb.indexes import GlobalSecondaryIndex, AllProjection


class OrderIdIndexForPayment(GlobalSecondaryIndex):
    class Meta:
        index_name = 'order_id_index'
        projection = AllProjection()
        read_capacity_units = 1
        write_capacity_units = 1

    order_id = UnicodeAttribute(hash_key=True)
    transaction_type = UnicodeAttribute(range_key=True)


class Payment(Model):
    class Meta:
        table_name = 'Payment'
        region = 'eu-west-1'
        max_retry_attempts = 8
        base_backoff_ms = 297

    transaction_id = UnicodeAttribute(hash_key=True)
    transaction_date = UnicodeAttribute()
    transaction_type = UnicodeAttribute()
    order_id = UnicodeAttribute()
    merchant_id = UnicodeAttribute()
    payment_amount = NumberAttribute()
    order_id_index = OrderIdIndexForPayment()
