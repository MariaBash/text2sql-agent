import kagglehub
import os
from sqlalchemy import create_engine, text
import pandas as pd

path = kagglehub.dataset_download("rohiteng/amazon-sales-dataset")


print(path)

DB_USER = "finance"
DB_PASS = "mysecretpassword"         
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "company_finance"


engine = create_engine(f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}")

df = pd.read_csv(f"{path}\\{os.listdir(path)[0]}")

df.columns = df.columns.str.lower()





orders = df.drop_duplicates(subset=['orderid'])[[
    'orderid',
    'orderdate',
    'orderstatus',
    'customerid',
    'customername',
    'city',
    'state',
    'country',
    'paymentmethod',
    'tax',
    'shippingcost',
    'totalamount',
    'sellerid'                   
]].copy()

orders['orderdate']     = pd.to_datetime(orders['orderdate'], errors='coerce')
orders['tax']           = pd.to_numeric(orders['tax'], errors='coerce')
orders['shippingcost']  = pd.to_numeric(orders['shippingcost'], errors='coerce')
orders['totalamount']   = pd.to_numeric(orders['totalamount'], errors='coerce')


order_items = df[[
    'orderid',
    'productid',
    'productname',
    'category',
    'brand',
    'quantity',
    'unitprice',
    'discount'
]].copy()

order_items['quantity']  = pd.to_numeric(order_items['quantity'],  errors='coerce', downcast='integer')
order_items['unitprice'] = pd.to_numeric(order_items['unitprice'], errors='coerce')
order_items['discount']  = pd.to_numeric(order_items['discount'],  errors='coerce')



orders.to_sql('orders', engine, if_exists='replace', index=False)
order_items.to_sql('order_items', engine, if_exists='replace', index=False)


with engine.connect() as conn:
    conn.execute(text("ALTER TABLE orders ADD PRIMARY KEY (orderid);"))
    conn.execute(text("""
        ALTER TABLE order_items
        ADD PRIMARY KEY (orderid, productid);
    """))
    conn.execute(text("""
        ALTER TABLE order_items
        ADD CONSTRAINT fk_order_items_orders
        FOREIGN KEY (orderid) REFERENCES orders(orderid)
        ON DELETE CASCADE;
    """))
    conn.execute(text("CREATE INDEX idx_orders_date ON orders(orderdate);"))
    conn.execute(text("CREATE INDEX idx_items_orderid ON order_items(orderid);"))
