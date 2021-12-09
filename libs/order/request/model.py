from pynamodb.models import Model
from pynamodb.attributes import (
    UnicodeAttribute,
    NumberAttribute,
    JSONAttribute,
    UTCDateTimeAttribute,
    BooleanAttribute,
    ListAttribute,
    MapAttribute
)


# class Item(MapAttribute):
#     item_id = UnicodeAttribute()
#     qty = NumberAttribute()
#     description = UnicodeAttribute()
#     unit_price = NumberAttribute()
#
#
# class Order(Model):
#     class Meta:
#         table_name = 'myOrder'
#         region = 'eu-west-1'
#         max_retry_attempts = 8
#         base_backoff_ms = 297
#
#     order_id = UnicodeAttribute(hash_key=True)
#     order_date = UnicodeAttribute()
#     customer_id = UnicodeAttribute()
#     order_status = UnicodeAttribute()
#     items = ListAttribute(of=Item)
#     transaction_id = UnicodeAttribute(null=True)
#     payment = JSONAttribute(null=True)
#     inventory = JSONAttribute(null=True)
#
#
# class OrderUpdate(Model):
#     class Meta:
#         table_name = 'myOrder'
#         region = 'eu-west-1'
#         max_retry_attempts = 8
#         base_backoff_ms = 297
#
#     order_id = UnicodeAttribute(hash_key=True)
#     transaction_id = UnicodeAttribute(null=True)
