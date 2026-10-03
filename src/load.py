import mysql.connector as connection
from config.config import DB_HOST, DB_USER, DB_PASSWORD, DB_NAME
import pandas as pd

def create_database_if_not_exists():

    conn=connection.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD)
    cursor= conn.cursor()
    cursor.execute (f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
    cursor.close()
    conn.close()

def get_connection():
    return connection.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME)

def create_table_if_not_exist():
    conn=get_connection()
    cursor=conn.cursor()

    cursor.execute("""
            CREATE TABLE IF NOT EXISTS customers (  
                customer_unique_id VARCHAR(50)  NOT NULL,
                total_order INT NOT NULL,
                first_purchase_date DATETIME,
                repeat_customer BOOLEAN,
                cohort_month VARCHAR(10),
                total_revenue DECIMAL(10,2),
                value_segment VARCHAR(20),
                retention_segment VARCHAR(20),
                customer_segment VARCHAR(40),
                UNIQUE KEY unique_customer (customer_unique_id)
                )
    """)

    cursor.execute("""
            CREATE TABLE IF NOT EXISTS customer_month (
             customer_unique_id VARCHAR(50) NOT NULL,
             order_month VARCHAR(10),
             orders_that_month INT,
             UNIQUE KEY unique_customer_month (customer_unique_id, order_month) )
             """)

    conn.commit()
    cursor.close()
    conn.close()

def load_data(df, table_name, columns):
    conn = get_connection()
    cursor = conn.cursor()

    col_names = ", ".join(columns)
    placeholders = ", ".join(["%s"] * len(columns))
    update_clause = ", ".join([f"{col}=VALUES({col})" for col in columns])

    insert_query = f"""
        INSERT INTO {table_name} ({col_names})
        VALUES ({placeholders})
        ON DUPLICATE KEY UPDATE {update_clause}
    """

    data = [tuple(row) for row in df[columns].itertuples(index=False, name=None)]

    cursor.executemany(insert_query, data)

    conn.commit()
    cursor.close()
    conn.close()
