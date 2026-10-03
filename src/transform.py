from config.config import VALID_ORDER_STATUS


def get_delivered_customer_orders(orders, customers):
    """
    Merge orders with customers on customer_id, and filter down to
    only valid (delivered) orders. This is the shared base that both
    build_customer_table() and build_customer_month_table() start from.
    """
    merged = orders.merge(
        customers[['customer_id', 'customer_unique_id']],
        on='customer_id',
        how='left'
    )

    delivered = merged[merged['order_status'] == VALID_ORDER_STATUS]

    return delivered


def build_customer_table(delivered):
    """
    One row per customer_unique_id:
    total_orders, first_purchase_date, cohort_month, repeat_customer.
    """
    total_orders = (
        delivered.groupby('customer_unique_id')['order_id']
        .nunique()
        .reset_index(name='total_orders')
    )

    first_purchase = (
        delivered.groupby('customer_unique_id')['order_purchase_timestamp']
        .min()
        .reset_index(name='first_purchase_date')
    )

    customer_table = total_orders.merge(first_purchase, on='customer_unique_id')

    customer_table['repeat_customer'] = customer_table['total_orders'] > 1
    customer_table['cohort_month'] = customer_table['first_purchase_date'].dt.to_period('M')

    return customer_table


def build_customer_month_table(delivered):
    """
    One row per customer_unique_id per active order_month,
    with a count of how many orders they placed that month.
    """
    delivered = delivered.copy()
    delivered['order_month'] = delivered['order_purchase_timestamp'].dt.to_period('M')

    customer_month = (
        delivered.groupby(['customer_unique_id', 'order_month'])
        .size()
        .reset_index(name='orders_that_month')
    )

    return customer_month


def build_customer_revenue_table(order_items_raw,delivered):
    order_value= order_items_raw.groupby('order_id')['price'].sum().reset_index(name='order_value')

    order_value_with_customer= order_value.merge(
        delivered[['order_id','customer_unique_id']],
        on='order_id',
        how='inner'
    )

    customer_revenue= order_value_with_customer.groupby('customer_unique_id')['order_value'].sum().reset_index(name='total_revenue')

    return customer_revenue


def add_customer_segments(customer_table):
    median_revenue = customer_table['total_revenue'].median()

    customer_table = customer_table.copy()

    customer_table['value_segment'] = customer_table['total_revenue'].apply(
        lambda x: 'High Value' if x > median_revenue else 'Low Value'
    )

    customer_table['retention_segment'] = customer_table['repeat_customer'].map(
        {True: 'Repeat', False: 'One-Time'}
    )

    customer_table['customer_segment'] = (
        customer_table['value_segment'] + ' - ' + customer_table['retention_segment']
    )

    return customer_table