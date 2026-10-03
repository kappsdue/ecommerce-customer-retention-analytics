import os
import pandas as pd
from config.config import RAW_DATA_DIR,ORDERS_FILE,CUSTOMERS_FILE,ORDER_ITEMS_FILE

def load_orders():
    filepath=os.path.join(RAW_DATA_DIR,ORDERS_FILE)
    orders =pd.read_csv(filepath)
    orders["order_purchase_timestamp"]= pd.to_datetime(orders['order_purchase_timestamp'])
    return orders

def load_customers():
    filepath=os.path.join(RAW_DATA_DIR,CUSTOMERS_FILE)
    return pd.read_csv(filepath)

def load_order_items():
    filepath=os.path.join(RAW_DATA_DIR,ORDER_ITEMS_FILE)
    return pd.read_csv(filepath)