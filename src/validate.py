
def no_duplicates(customer_table):
    count=customer_table['customer_unique_id'].duplicated().sum()

    if count>0:
         raise ValueError('duplicate customer_unique_id found')
    else:
        return "No duplicates found"

def no_nulls(customer_table):
    count=customer_table[['customer_unique_id','cohort_month']].isnull().sum()

    if (count>0).any():
        raise ValueError('Null values found in customer_unique_id and cohort_month')

def check_order_count(customer_tbl,customer_month_tbl):
    monthly_total= customer_month_tbl.groupby('customer_unique_id')['orders_that_month'].sum()

    customer_total= customer_tbl.set_index('customer_unique_id')['total_orders']

    if not (customer_total == monthly_total).all():
            raise ValueError ("total orders does not match summed orders")
    return "Values match"

def run_all_val_checks(customer_tbl,customer_month_tbl):
    no_duplicates(customer_tbl)

    no_nulls(customer_tbl)

    check_order_count(customer_tbl,customer_month_tbl)

    print  ("All Validation Checks Passed"
            )