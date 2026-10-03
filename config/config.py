import os

BASE_DIR= os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DATA_DIR= os.path.join(BASE_DIR,"data","raw")
PROCESSED_DATA_DIR= os.path.join(BASE_DIR,"data","processed")

ORDERS_FILE= 'olist_orders_dataset.csv'
CUSTOMERS_FILE= 'olist_customers_dataset.csv'
ORDER_ITEMS_FILE= 'olist_order_items_dataset.csv'

CUSTOMER_TABLE_FILE= "customer_retention.csv"
CUSTOMER_MONTH_FILE="customer_month_activity.csv"


#mysql connection
DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = "root"
DB_NAME = "ecommerce_retention"

CUSTOMER_TABLE = "customer_retention"
CUSTOMER_MONTH_TABLE = "customer_month_activity"

VALID_ORDER_STATUS = "delivered"
