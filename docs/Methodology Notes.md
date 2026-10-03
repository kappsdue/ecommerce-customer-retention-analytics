# Methodology Notes

This document explains the analytical decisions behind the E-commerce Customer Retention & Cohort Analytics project in more depth than the main README. Each section covers a decision that wasn't obvious from the raw data and had to be investigated or justified before being locked in.

---

## 1. Customer identity: `customer_unique_id`, not `customer_id`

Olist's `customers` table contains a `customer_id` and a `customer_unique_id` for every row. It's tempting to treat `customer_id` as the customer identifier, but it isn't one — it's generated fresh for every individual order. The same real person receives a different `customer_id` each time they purchase.

This was confirmed directly: `customer_id` has zero duplicates across the entire `customers` table (99,441 rows, 99,441 unique values), while `customer_unique_id` has 3,345 duplicates — meaning 3,345 real people are responsible for more than one row/order in the dataset. `customer_unique_id` is the only field that correctly identifies the same person across multiple purchases, and it is used for all customer-level aggregation in this project.

**Why this matters:** if `customer_id` had been used instead, every customer would appear to have made exactly one purchase, since the ID itself never repeats. The entire retention and cohort analysis would have been built on a false premise.

---

## 2. Valid purchase population: delivered orders only

The `orders` table contains 99,441 order records across 8 statuses: `delivered` (96,478), `shipped` (1,107), `canceled` (625), `unavailable` (609), `invoiced` (314), `processing` (301), `created` (5), `approved` (2).

Only `delivered` orders are treated as completed purchases throughout this project. Canceled and unavailable orders clearly never resulted in a transaction; in-progress statuses (`shipped`, `invoiced`, `processing`, `created`, `approved`) represent orders that hadn't completed as of the dataset's snapshot and carry the same ambiguity. Restricting to `delivered` orders gives the cleanest, most defensible definition of "a customer actually purchased something."

---

## 3. Cohort and retention definitions

**Cohort:** the calendar month of a customer's first delivered order, anchored on `order_purchase_timestamp` — the moment the customer acted — rather than any delivery-related timestamp, which can lag purchase by days to weeks in this dataset.

**Monthly retention:** the percentage of a cohort's *original* size that placed at least one additional delivered order in a specific calendar month since acquisition. The denominator is fixed at the cohort's starting size and does not shrink as months pass — retention in month 6 is still measured against the full original cohort, not against customers still active at month 5.

**Unobserved periods:** a cohort acquired near the end of the dataset's window (e.g. August 2018) cannot have data for "6 months later," because the dataset ends before that time elapses. These cells are shown as blank (not observed) rather than 0%, since a missing observation is not evidence of zero returns. This creates the triangular shape visible in the cohort matrix.

---

## 4. Investigating rapid repeat orders

797 of the 2,801 repeat customers (28.5%) placed their second delivered order within one hour of their first. Before accepting these as genuine repeat purchases, they were investigated directly rather than excluded on a guessed duplicate-order rule.

**What was checked, in order:**
1. Compared item count, product count, seller count, merchandise value, and freight value between each customer's first and second order.
2. Built a direct product-ID overlap check: for each of the 797 customers, did their two orders share at least one identical product?

**Result:** only 64 of 797 pairs (8.03%) shared any product between the two orders; 733 (91.97%) did not. Most rapid-repeat pairs also differed in seller, item count, and order value.

**Conclusion:** the low product overlap suggests most rapid repeats are genuinely separate purchasing decisions rather than duplicate or split-cart artifacts, so they remain in the primary repeat-customer definition. This cannot be established with full certainty from the available data — it is the project's best defensible interpretation of the evidence, documented explicitly as a limitation.

---

## 5. Order value: price only, excluding freight

Customer-level revenue is calculated as the sum of item `price` across a customer's delivered orders, excluding `freight_value`. Freight cost reflects shipping logistics — distance, weight, carrier choice — rather than how much the customer valued what they purchased. Including it would mix purchasing behavior with shipping-cost noise unrelated to retention.

---

## 6. Value segmentation: median split, not mean

Customers are classified as "High Value" or "Low Value" based on whether their total observed revenue falls above or below the **median** (R$89.73), not the mean (R$141.62).

Customer revenue in this dataset is right-skewed: a small number of very large orders pull the mean well above the median (the 75th percentile, R$154.74, sits close to the mean itself). A mean-based cutoff would therefore classify the large majority of customers as "low value," producing an unbalanced and less useful segmentation. The median always splits the customer base into two comparably-sized groups regardless of skew, which is what a segmentation needs to be useful for comparison.

---

## 7. Validation checks run before loading to MySQL

Three structural checks run against the pipeline's output tables before any data is loaded:

- **No duplicate customers:** `customer_unique_id` is unique in the customer dimension table.
- **No missing identity or cohort data:** `customer_unique_id` and `cohort_month` are never null — guaranteed structurally, since both tables are built from `groupby` operations that only produce a row for customers who actually have at least one delivered order.
- **Cross-table consistency:** for every customer, `total_orders` in the customer dimension table equals the sum of their `orders_that_month` values in the customer-month fact table. This catches any case where an order was counted differently across the two tables.

---

## Known limitations

- **Observation window bias:** cohorts acquired later in the dataset's window have had less time to demonstrate repeat behavior than earlier cohorts. Comparisons across cohorts should account for this; it is also why unobserved periods are shown as blank rather than zero.
- **Small-sample volatility:** several cohort/month cells, particularly in later columns and the smallest cohorts, are based on very few customers. The three cohorts before January 2017 (264 customers combined) are excluded from the retention visuals for this reason.
- **Rapid-order ambiguity:** the product-overlap audit is strong supporting evidence but not proof that all rapid repeat orders are genuine separate purchases.
- **No causal claims:** this project is observational. It identifies patterns and segments (e.g. the High Value – One-Time opportunity) but does not establish why customers return or don't, or what specific intervention would change that behavior.
