sql tables:
orders

order_id

order_date

order_status

customer_id

customer_name

city

state

country

payment_method

tax

shipping_cost

total_amount

order_items

order_id

seller_id

product_id

product_name

category

brand

quantity

unit_price

discount

связь:
orders.order_id = order_items.order_id (1 → many)
