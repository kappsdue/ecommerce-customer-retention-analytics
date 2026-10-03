from src.extract import load_orders,load_customers,load_order_items
from src.transform import (get_delivered_customer_orders,build_customer_month_table,
                           build_customer_table,build_customer_revenue_table,
                           add_customer_segments)
from src.validate import run_all_val_checks
from src.load import create_database_if_not_exists,create_table_if_not_exist,load_data

orders = load_orders()
customers = load_customers()
order_items= load_order_items()

delivered = get_delivered_customer_orders(orders, customers)
customer_table = build_customer_table(delivered)
customer_month_table = build_customer_month_table(delivered)
customer_revenue= build_customer_revenue_table(order_items,delivered)

customer_table['cohort_month']=customer_table['cohort_month'].astype(str)
customer_month_table['order_month'] = customer_month_table['order_month'].astype(str)
customer_table = customer_table.merge(customer_revenue, on='customer_unique_id', how='left')
customer_table['total_revenue'] = customer_table['total_revenue'].fillna(0)
customer_table = add_customer_segments(customer_table)

run_all_val_checks(customer_table,customer_month_table)

create_database_if_not_exists()
create_table_if_not_exist()
load_data(customer_table,'customers',
['customer_unique_id','total_orders','first_purchase_date', 'repeat_customer', 'cohort_month','total_revenue',
           'value_segment','retention_segment','customer_segment'])
load_data(customer_month_table,'customer_month',['customer_unique_id','order_month','orders_that_month'])
